"""Slack API client with security hardening.

Slack-specific notes:
- Slack uses POST for all API methods, even reads
- Responses use {"ok": false, "error": "code"} instead of HTTP status codes
- Rate limits return HTTP 429 with Retry-After header
"""

import json
import logging
from importlib.metadata import version
from typing import Any

import httpx

from .config import get_config
from .errors import (
    ChannelNotFoundError,
    MissingScopeError,
    PermissionDeniedError,
    RateLimitError,
    SlackApiError,
    UserNotFoundError,
)

logger = logging.getLogger(__name__)

MAX_RESPONSE_SIZE = 10 * 1024 * 1024
REQUEST_TIMEOUT = 30.0
HTTP_TOO_MANY_REQUESTS = 429
BODY_SNIPPET_CHARS = 200
ELLIPSIS = "..."

# Identify this client by name. httpx otherwise sends `python-httpx/<version>`,
# which bot protection answers with an HTML challenge page instead of the API --
# the failure that cost an afternoon on mcp-wordpress (RT #1596). The version
# comes from installed package metadata so it cannot drift from pyproject.toml.
USER_AGENT = (
    f"mcp-slack-crunchtools/{version('mcp-slack-crunchtools')} "
    "(+https://github.com/crunchtools/mcp-slack)"
)


def _body_snippet(body: bytes) -> str:
    """A short, single-line excerpt of a response body, for an error message."""
    prefix = body[: BODY_SNIPPET_CHARS * 4]
    collapsed = " ".join(prefix.decode("utf-8", errors="replace").split())
    if not collapsed:
        return "<empty body>"
    if len(collapsed) > BODY_SNIPPET_CHARS or len(body) > len(prefix):
        return collapsed[: BODY_SNIPPET_CHARS - len(ELLIPSIS)] + ELLIPSIS
    return collapsed


def _where(response: httpx.Response) -> str:
    """Which request a response answered, for an error message.

    Slack answers failures with HTTP 200 and `{"ok": false}`, so the one thing
    an unparseable body can be is something that is not Slack: a captive portal,
    a corporate proxy, an SSO interstitial. Naming the URL and the content-type
    is what tells those apart from the API.
    """
    return (
        f"{response.request.method} {response.request.url} "
        f"(HTTP {response.status_code}, {response.headers.get('content-type', 'no content-type')})"
    )


async def _read_capped(response: httpx.Response) -> bytes:
    """Read the body, aborting as soon as it would pass MAX_RESPONSE_SIZE.

    One buffer, measured before the copy: `aiter_bytes()` promises nothing about
    chunk size -- one chunk can be the whole body -- so appending first would
    copy in exactly the response being refused. The `content-length` check this
    replaces was the only limit, and it is a header Slack need not send.
    """
    declared = response.headers.get("content-length")
    if declared and declared.isdigit() and int(declared) > MAX_RESPONSE_SIZE:
        raise SlackApiError(
            "response_too_large",
            f"{_where(response)} declared {declared} bytes, over the "
            f"{MAX_RESPONSE_SIZE} byte limit",
        )
    body = bytearray()
    async for chunk in response.aiter_bytes():
        if len(body) + len(chunk) > MAX_RESPONSE_SIZE:
            raise SlackApiError(
                "response_too_large",
                f"{_where(response)} sent over the {MAX_RESPONSE_SIZE} byte limit",
            )
        body += chunk
    return bytes(body)


_ERROR_MAP: dict[str, type[Exception]] = {
    "not_authed": PermissionDeniedError,
    "invalid_auth": PermissionDeniedError,
    "account_inactive": PermissionDeniedError,
    "token_revoked": PermissionDeniedError,
    "token_expired": PermissionDeniedError,
    "channel_not_found": ChannelNotFoundError,
    "user_not_found": UserNotFoundError,
    "ratelimited": RateLimitError,
    "missing_scope": MissingScopeError,
}


class SlackClient:
    """Async HTTP client for Slack Web API.

    Security features:
    - Hardcoded base URL (prevents SSRF)
    - Token passed via auth header (not URL)
    - TLS certificate validation (httpx default)
    - Request timeout enforcement
    - Response size limits
    - All methods use POST (Slack convention)
    """

    def __init__(self) -> None:
        self._config = get_config()
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            headers: dict[str, str] = {
                "Authorization": f"Bearer {self._config.token}",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": USER_AGENT,
            }
            if self._config.cookie_d is not None:
                headers["Cookie"] = f"d={self._config.cookie_d}"
            self._client = httpx.AsyncClient(
                base_url=self._config.api_base_url,
                headers=headers,
                timeout=httpx.Timeout(REQUEST_TIMEOUT),
                verify=True,
            )
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def api_call(
        self,
        method: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a Slack API call.

        All Slack API methods use POST with form-encoded parameters.

        Args:
            method: Slack API method name (e.g., "conversations.list")
            params: API method parameters

        Returns:
            API response data (with "ok" field)

        Raises:
            SlackApiError: On API errors
            RateLimitError: On rate limiting
            PermissionDeniedError: On authorization failures
            ChannelNotFoundError: When channel is not found
            UserNotFoundError: When user is not found
            MissingScopeError: When OAuth scope is missing
        """
        client = await self._get_client()
        logger.debug("Slack API call: %s", method)

        form_params: dict[str, Any] = {}
        if params:
            for key, value in params.items():
                if value is not None:
                    form_params[key] = value

        try:
            request = client.build_request("POST", f"/{method}", data=form_params)
            response = await client.send(request, stream=True)
            try:
                body = await _read_capped(response)
            finally:
                await response.aclose()
        except httpx.TimeoutException as e:
            raise SlackApiError("timeout", f"Request timeout: {e}") from e
        except httpx.RequestError as e:
            raise SlackApiError("request_error", f"Request failed: {e}") from e

        if response.status_code == HTTP_TOO_MANY_REQUESTS:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(int(retry_after) if retry_after else None)

        try:
            api_response: dict[str, Any] = json.loads(body)
        except ValueError as e:
            raise SlackApiError(
                "invalid_json",
                f"{_where(response)} is not JSON ({e}): {_body_snippet(body)}",
            ) from e

        if not api_response.get("ok"):
            error_code = api_response.get("error", "unknown_error")
            self._handle_slack_error(error_code, api_response)

        return api_response

    def _handle_slack_error(self, error_code: str, response_body: dict[str, Any]) -> None:
        error_class = _ERROR_MAP.get(error_code)

        if error_class is PermissionDeniedError:
            raise PermissionDeniedError("Valid Slack User OAuth Token")
        if error_class is ChannelNotFoundError:
            raise ChannelNotFoundError(error_code)
        if error_class is UserNotFoundError:
            raise UserNotFoundError(error_code)
        if error_class is RateLimitError:
            retry_after = response_body.get("retry_after")
            raise RateLimitError(int(retry_after) if retry_after else None)
        if error_class is MissingScopeError:
            needed = response_body.get("needed", error_code)
            raise MissingScopeError(str(needed))

        raise SlackApiError(error_code)


_client: SlackClient | None = None


def get_client() -> SlackClient:
    """Get the global Slack client instance."""
    global _client
    if _client is None:
        _client = SlackClient()
    return _client

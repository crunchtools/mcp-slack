"""Slack API client with security hardening.

Slack-specific notes:
- Slack uses POST for all API methods, even reads
- Responses use {"ok": false, "error": "code"} instead of HTTP status codes
- Rate limits return HTTP 429 with Retry-After header
"""

import logging
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
            response = await client.post(f"/{method}", data=form_params)
        except httpx.TimeoutException as e:
            raise SlackApiError("timeout", f"Request timeout: {e}") from e
        except httpx.RequestError as e:
            raise SlackApiError("request_error", f"Request failed: {e}") from e

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(int(retry_after) if retry_after else None)

        content_length = response.headers.get("content-length")
        if content_length and int(content_length) > MAX_RESPONSE_SIZE:
            raise SlackApiError("response_too_large", "Response too large")

        try:
            api_response: dict[str, Any] = response.json()
        except ValueError as e:
            raise SlackApiError("invalid_json", f"Invalid JSON response: {e}") from e

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

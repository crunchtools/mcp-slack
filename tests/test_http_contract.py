"""The outbound HTTP contract (constitution v1.36.0, MCP Server profile Layer 3).

The client is built through its own `_get_client()` over a `MockTransport`,
rather than handed a client the test assembled: the agent string is one of the
headers `_get_client` sets, so a test that builds its own client cannot see it.
"""

from collections.abc import AsyncIterator, Callable, Iterator
from contextlib import contextmanager
from importlib.metadata import version
from typing import Any
from unittest.mock import patch

import httpx
import pytest

from mcp_slack_crunchtools import client as client_mod
from mcp_slack_crunchtools.errors import SlackApiError

Handler = Callable[[httpx.Request], httpx.Response]


async def _chunks(chunk: bytes, times: int) -> AsyncIterator[bytes]:
    """A chunked body, which carries no content-length -- what a header check misses."""
    for _ in range(times):
        yield chunk


@contextmanager
def _serving(handler: Handler, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Let `_get_client` build a real client, on a mock transport."""
    monkeypatch.setenv("SLACK_USER_TOKEN", "xoxp-test-token")
    import mcp_slack_crunchtools.config as config_mod

    config_mod._config = None
    client_mod._client = None
    real = httpx.AsyncClient

    def factory(**kwargs: Any) -> httpx.AsyncClient:
        kwargs.pop("transport", None)
        return real(transport=httpx.MockTransport(handler), **kwargs)

    with patch.object(httpx, "AsyncClient", factory):
        yield
    config_mod._config = None
    client_mod._client = None


class TestUserAgent:
    """A request says what it is, and the version cannot drift from the release."""

    @pytest.mark.asyncio
    async def test_outgoing_request_names_the_product_and_version(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        seen: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(request.headers["User-Agent"])
            return httpx.Response(200, json={"ok": True})

        with _serving(handler, monkeypatch):
            await client_mod.get_client().api_call("auth.test")

        expected = (
            f"mcp-slack-crunchtools/{version('mcp-slack-crunchtools')} "
            "(+https://github.com/crunchtools/mcp-slack)"
        )
        assert seen == [expected]
        assert "python-httpx" not in seen[0]


class TestResponseCeiling:
    """The cap is enforced while reading, not taken from a header."""

    @pytest.mark.asyncio
    async def test_chunked_body_over_the_cap_is_refused(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(client_mod, "MAX_RESPONSE_SIZE", 4096)

        def handler(_request: httpx.Request) -> httpx.Response:
            response = httpx.Response(
                200, headers={"content-type": "application/json"}, content=_chunks(b"x" * 1024, 16)
            )
            assert "content-length" not in response.headers
            return response

        with _serving(handler, monkeypatch), pytest.raises(SlackApiError) as caught:
            await client_mod.get_client().api_call("conversations.history")

        message = str(caught.value)
        assert "over the 4096 byte limit" in message
        assert "conversations.history" in message

    @pytest.mark.asyncio
    async def test_a_single_oversized_chunk_is_refused_before_it_is_copied(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(client_mod, "MAX_RESPONSE_SIZE", 1024)

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200, headers={"content-type": "application/json"}, content=_chunks(b"x" * 8192, 1)
            )

        with _serving(handler, monkeypatch), pytest.raises(SlackApiError) as caught:
            await client_mod.get_client().api_call("conversations.history")

        assert "over the 1024 byte limit" in str(caught.value)


class TestErrorNamesTheSite:
    """Slack answers failures with HTTP 200, so a non-JSON body is not Slack."""

    @pytest.mark.asyncio
    async def test_a_captive_portal_is_quoted_with_the_request(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                headers={"content-type": "text/html"},
                text="<title>Network sign-in required</title>",
            )

        with _serving(handler, monkeypatch), pytest.raises(SlackApiError) as caught:
            await client_mod.get_client().api_call("auth.test")

        message = str(caught.value)
        assert "Network sign-in required" in message
        assert "text/html" in message
        assert "auth.test" in message

    @pytest.mark.asyncio
    async def test_slacks_own_ok_false_is_still_mapped(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The contract changes the unparseable case, not Slack's own errors."""
        from mcp_slack_crunchtools.errors import ChannelNotFoundError

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"ok": False, "error": "channel_not_found"})

        with _serving(handler, monkeypatch), pytest.raises(ChannelNotFoundError):
            await client_mod.get_client().api_call("conversations.history")

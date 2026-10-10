"""Tests for MCP tool registration and imports."""

import asyncio
import os
from collections.abc import Iterator

import httpx
import pytest


class TestToolRegistration:
    """Tests to verify all tools are properly registered."""

    def test_server_has_tools(self) -> None:
        """Server should have all expected tools registered."""
        os.environ.setdefault("SLACK_USER_TOKEN", "xoxp-test-token-for-ci")
        from mcp_slack_crunchtools.server import mcp

        assert mcp is not None

    def test_imports(self) -> None:
        """All tool functions should be importable."""
        from mcp_slack_crunchtools.tools import (
            auth_test,
            cancel_scheduled_message,
            get_channel_history,
            get_channel_info,
            get_file_info,
            get_reactions,
            get_thread_replies,
            get_user_info,
            get_user_profile,
            list_channel_members,
            list_channels,
            list_files,
            list_reactions,
            list_stars,
            list_users,
            search_messages,
            send_message,
        )

        assert callable(auth_test)
        assert callable(list_channels)
        assert callable(get_channel_info)
        assert callable(get_channel_history)
        assert callable(get_thread_replies)
        assert callable(list_channel_members)
        assert callable(search_messages)
        assert callable(get_reactions)
        assert callable(list_reactions)
        assert callable(list_stars)
        assert callable(get_user_info)
        assert callable(list_users)
        assert callable(get_user_profile)
        assert callable(list_files)
        assert callable(get_file_info)
        assert callable(send_message)
        assert callable(cancel_scheduled_message)

    def test_tool_count(self) -> None:
        """Should have exactly 17 tool functions exported."""
        from mcp_slack_crunchtools.tools import __all__

        assert len(__all__) == 17


READ_ONLY = frozenset(
    {
        "slack_auth_test",
        "slack_list_channels",
        "slack_get_channel_info",
        "slack_get_channel_history",
        "slack_get_thread_replies",
        "slack_list_channel_members",
        "slack_search_messages",
        "slack_get_reactions",
        "slack_list_reactions",
        "slack_list_stars",
        "slack_get_user_info",
        "slack_list_users",
        "slack_get_user_profile",
        "slack_list_files",
        "slack_get_file_info",
    }
)
WRITES = frozenset({"slack_send_message", "slack_cancel_scheduled_message"})

# Slack's Web API takes POST for reads and writes alike, so the HTTP verb says
# nothing. What separates them is the API method in the path. These are the
# methods a read-only tool may call; each returns data and changes nothing.
# conversations.mark, chat.* and reactions.add are absent on purpose.
READ_METHODS = frozenset(
    {
        "auth.test",
        "conversations.list",
        "conversations.info",
        "conversations.history",
        "conversations.replies",
        "conversations.members",
        "search.messages",
        "reactions.get",
        "reactions.list",
        "stars.list",
        "users.info",
        "users.list",
        "users.profile.get",
        "files.list",
        "files.info",
    }
)

# Every parameter of each read-only tool, so optional branches run too.
READ_ONLY_CALLS: dict[str, dict[str, object]] = {
    "slack_auth_test": {},
    "slack_list_channels": {"types": "im", "exclude_archived": False, "limit": 5, "cursor": "c1"},
    "slack_get_channel_info": {"channel_id": "C012345678"},
    "slack_get_channel_history": {
        "channel_id": "C012345678",
        "limit": 5,
        "cursor": "c1",
        "oldest": "1700000000.000100",
        "latest": "1700000001.000100",
        "inclusive": True,
    },
    "slack_get_thread_replies": {
        "channel_id": "C012345678",
        "thread_ts": "1700000000.000100",
        "limit": 5,
        "cursor": "c1",
        "oldest": "1700000000.000100",
        "latest": "1700000001.000100",
        "inclusive": True,
    },
    "slack_list_channel_members": {"channel_id": "C012345678", "limit": 5, "cursor": "c1"},
    "slack_search_messages": {
        "query": "from:scott",
        "sort": "score",
        "sort_dir": "asc",
        "count": 5,
        "page": 2,
    },
    "slack_get_reactions": {
        "channel_id": "C012345678",
        "timestamp": "1700000000.000100",
        "full": True,
    },
    "slack_list_reactions": {"user_id": "U012345678", "count": 5, "page": 2, "full": True},
    "slack_list_stars": {"count": 5, "page": 2, "cursor": "c1"},
    "slack_get_user_info": {"user_id": "U012345678"},
    "slack_list_users": {"limit": 5, "cursor": "c1"},
    "slack_get_user_profile": {"user_id": "U012345678", "include_labels": True},
    "slack_list_files": {
        "channel_id": "C012345678",
        "user_id": "U012345678",
        "types": "images",
        "count": 5,
        "page": 2,
        "ts_from": "1700000000",
        "ts_to": "1700000001",
    },
    "slack_get_file_info": {"file_id": "F012345678", "count": 5, "page": 2},
}


@pytest.fixture
def slack_requests(monkeypatch: pytest.MonkeyPatch) -> Iterator[list[httpx.Request]]:
    """Route the Slack client through a mock transport and record what it sends."""
    import mcp_slack_crunchtools.client as client_module
    import mcp_slack_crunchtools.config as config_module

    monkeypatch.setenv("SLACK_USER_TOKEN", "xoxp-test-token-for-ci")
    monkeypatch.setenv("SLACK_ADD_MESSAGE_DELAY", "0")
    monkeypatch.setattr(config_module, "_config", None)

    sent: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        sent.append(request)
        return httpx.Response(200, json={"ok": True})

    slack = client_module.SlackClient()
    slack._client = httpx.AsyncClient(
        base_url=config_module.get_config().api_base_url,
        transport=httpx.MockTransport(handler),
    )
    monkeypatch.setattr(client_module, "_client", slack)
    yield sent
    monkeypatch.setattr(config_module, "_config", None)


def _api_methods(sent: list[httpx.Request]) -> set[str]:
    """Slack API method names from recorded requests (the last path segment)."""
    return {request.url.path.rsplit("/", 1)[-1] for request in sent}


class TestReadOnlyAnnotation:
    """Every registered tool is classified, and the reads really only read."""

    @pytest.mark.asyncio
    async def test_every_tool_is_classified(self) -> None:
        os.environ.setdefault("SLACK_USER_TOKEN", "xoxp-test-token-for-ci")
        from mcp_slack_crunchtools.server import mcp

        tools = await mcp.list_tools()
        assert READ_ONLY.isdisjoint(WRITES)
        assert {tool.name for tool in tools} == READ_ONLY | WRITES
        annotated = {
            tool.name
            for tool in tools
            if tool.annotations is not None
            and tool.annotations.model_dump(by_alias=True).get("readOnlyHint") is True
        }
        assert annotated == READ_ONLY

    def test_every_read_only_tool_has_a_call(self) -> None:
        assert set(READ_ONLY_CALLS) == READ_ONLY

    @pytest.mark.asyncio
    @pytest.mark.parametrize("name", sorted(READ_ONLY))
    async def test_read_only_tool_calls_only_read_methods(
        self, name: str, slack_requests: list[httpx.Request]
    ) -> None:
        from mcp_slack_crunchtools.server import mcp

        await mcp.call_tool(name, READ_ONLY_CALLS[name])
        assert slack_requests, f"{name} sent nothing to Slack"
        assert _api_methods(slack_requests) <= READ_METHODS

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("name", "args"),
        [
            ("slack_send_message", {"channel_id": "C012345678", "text": "hello"}),
            (
                "slack_cancel_scheduled_message",
                {"channel_id": "C012345678", "scheduled_message_id": "Q1234ABCD"},
            ),
        ],
    )
    async def test_write_tool_is_caught_by_the_method_check(
        self, name: str, args: dict[str, object], slack_requests: list[httpx.Request]
    ) -> None:
        """The same recording flags a write, so the read check above can fail."""
        from mcp_slack_crunchtools.server import mcp

        await mcp.call_tool(name, args)
        assert slack_requests
        assert not _api_methods(slack_requests) <= READ_METHODS


class TestWriteTools:
    """Tests for scheduled messaging tools."""

    def test_delay_default(self) -> None:
        """Default delay should be 180 seconds (3 minutes)."""
        import mcp_slack_crunchtools.tools.write as write_module

        token = os.environ.pop("SLACK_ADD_MESSAGE_DELAY", None)
        try:
            assert write_module._get_delay_seconds() == 180
        finally:
            if token is not None:
                os.environ["SLACK_ADD_MESSAGE_DELAY"] = token

    def test_delay_zero_disables_scheduling(self) -> None:
        """SLACK_ADD_MESSAGE_DELAY=0 or 0s should return 0."""
        import mcp_slack_crunchtools.tools.write as write_module

        for value in ("0", "0s"):
            os.environ["SLACK_ADD_MESSAGE_DELAY"] = value
            try:
                assert write_module._get_delay_seconds() == 0
            finally:
                del os.environ["SLACK_ADD_MESSAGE_DELAY"]

    def test_delay_custom_values(self) -> None:
        """Custom duration strings should parse correctly."""
        import mcp_slack_crunchtools.tools.write as write_module

        cases = [("5m", 300), ("30s", 30), ("1h", 3600), ("120", 120)]
        for raw, expected in cases:
            os.environ["SLACK_ADD_MESSAGE_DELAY"] = raw
            try:
                assert write_module._get_delay_seconds() == expected, f"failed for {raw!r}"
            finally:
                del os.environ["SLACK_ADD_MESSAGE_DELAY"]

    def test_send_message_invalid_channel(self) -> None:
        """send_message should raise on an invalid channel_id."""
        from mcp_slack_crunchtools.tools.write import send_message

        with pytest.raises(ValueError, match="channel_id"):
            asyncio.run(send_message(channel_id="invalid", text="hello"))

    def test_write_tools_registered(self) -> None:
        """slack_send_message and slack_cancel_scheduled_message should be in the server."""
        os.environ.setdefault("SLACK_USER_TOKEN", "xoxp-test-token-for-ci")
        from mcp_slack_crunchtools import server

        assert hasattr(server, "slack_send_message")
        assert hasattr(server, "slack_cancel_scheduled_message")
        assert callable(server.slack_send_message)
        assert callable(server.slack_cancel_scheduled_message)


class TestErrorSafety:
    """Tests to verify error messages don't leak sensitive data."""

    def test_slack_api_error_sanitizes_token(self) -> None:
        """SlackApiError should sanitize tokens from messages."""
        from mcp_slack_crunchtools.errors import SlackApiError

        os.environ["SLACK_USER_TOKEN"] = "xoxp-secret-token-12345"

        try:
            error = SlackApiError("invalid_auth", "Token xoxp-secret-token-12345 is invalid")
            assert "xoxp-secret-token-12345" not in str(error)
            assert "***" in str(error)
        finally:
            del os.environ["SLACK_USER_TOKEN"]

    def test_channel_not_found_truncates_long_ids(self) -> None:
        """ChannelNotFoundError should truncate long identifiers."""
        from mcp_slack_crunchtools.errors import ChannelNotFoundError

        long_id = "a" * 100
        error = ChannelNotFoundError(long_id)
        error_str = str(error)

        assert long_id not in error_str
        assert "..." in error_str

    def test_user_not_found_truncates_long_ids(self) -> None:
        """UserNotFoundError should truncate long identifiers."""
        from mcp_slack_crunchtools.errors import UserNotFoundError

        long_id = "b" * 100
        error = UserNotFoundError(long_id)
        error_str = str(error)

        assert long_id not in error_str
        assert "..." in error_str

    def test_missing_scope_error(self) -> None:
        """MissingScopeError should include the scope name."""
        from mcp_slack_crunchtools.errors import MissingScopeError

        error = MissingScopeError("channels:read")
        assert "channels:read" in str(error)

    def test_rate_limit_error_with_retry(self) -> None:
        """RateLimitError should include retry-after when provided."""
        from mcp_slack_crunchtools.errors import RateLimitError

        error = RateLimitError(30)
        assert "30" in str(error)
        assert "Retry after" in str(error)

    def test_rate_limit_error_without_retry(self) -> None:
        """RateLimitError should work without retry-after."""
        from mcp_slack_crunchtools.errors import RateLimitError

        error = RateLimitError()
        assert "Rate limit exceeded" in str(error)


class TestConfigSafety:
    """Tests for configuration security."""

    def test_config_repr_hides_token(self) -> None:
        """Config repr should never show the token."""
        os.environ["SLACK_USER_TOKEN"] = "xoxp-secret-test-token"

        try:
            from mcp_slack_crunchtools.config import Config

            config = Config()
            assert "xoxp-secret-test-token" not in repr(config)
            assert "xoxp-secret-test-token" not in str(config)
            assert "***" in repr(config)
        finally:
            del os.environ["SLACK_USER_TOKEN"]

    def test_config_requires_token(self) -> None:
        """Config should require SLACK_USER_TOKEN."""
        from mcp_slack_crunchtools.config import Config
        from mcp_slack_crunchtools.errors import ConfigurationError

        token = os.environ.pop("SLACK_USER_TOKEN", None)

        try:
            import mcp_slack_crunchtools.config as config_module

            config_module._config = None

            with pytest.raises(ConfigurationError):
                Config()
        finally:
            if token:
                os.environ["SLACK_USER_TOKEN"] = token

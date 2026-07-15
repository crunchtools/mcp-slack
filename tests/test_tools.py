"""Tests for MCP tool registration and imports."""

import os

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
        import asyncio

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

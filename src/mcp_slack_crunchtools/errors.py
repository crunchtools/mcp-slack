"""Safe error types that can be shown to users.

This module defines exception classes that are safe to expose to MCP clients.
Internal errors should be caught and converted to UserError before propagating.
"""

import os

MAX_SAFE_ID_LENGTH = 20


class UserError(Exception):
    """Base class for safe errors that can be shown to users.

    All error messages in UserError subclasses must be carefully crafted
    to avoid leaking sensitive information like API tokens or internal paths.
    """

    pass


class ConfigurationError(UserError):
    """Error in server configuration."""

    pass


class InvalidChannelIdError(UserError):
    """Invalid Slack channel ID format."""

    def __init__(self) -> None:
        super().__init__(
            "Invalid channel_id format. Expected C/D/G prefix + 8+ alphanumeric chars."
        )


class InvalidUserIdError(UserError):
    """Invalid Slack user ID format."""

    def __init__(self) -> None:
        super().__init__("Invalid user_id format. Expected U/W/B prefix + 8+ alphanumeric chars.")


class InvalidTeamIdError(UserError):
    """Invalid Slack team ID format."""

    def __init__(self) -> None:
        super().__init__("Invalid team_id format. Expected T prefix + 8+ alphanumeric chars.")


class InvalidFileIdError(UserError):
    """Invalid Slack file ID format."""

    def __init__(self) -> None:
        super().__init__("Invalid file_id format. Expected F prefix + 8+ alphanumeric chars.")


class InvalidTimestampError(UserError):
    """Invalid Slack message timestamp format."""

    def __init__(self) -> None:
        super().__init__(
            "Invalid timestamp format. Expected digits.digits (e.g., 1234567890.123456)."
        )


class ChannelNotFoundError(UserError):
    """Channel not found or not accessible."""

    def __init__(self, identifier: str) -> None:
        truncated = len(identifier) > MAX_SAFE_ID_LENGTH
        safe_id = identifier[:MAX_SAFE_ID_LENGTH] + "..." if truncated else identifier
        super().__init__(f"Channel not found or not accessible: {safe_id}")


class UserNotFoundError(UserError):
    """User not found."""

    def __init__(self, identifier: str) -> None:
        truncated = len(identifier) > MAX_SAFE_ID_LENGTH
        safe_id = identifier[:MAX_SAFE_ID_LENGTH] + "..." if truncated else identifier
        super().__init__(f"User not found: {safe_id}")


class PermissionDeniedError(UserError):
    """Permission denied for the requested operation."""

    def __init__(self, required_scope: str) -> None:
        super().__init__(f"Permission denied. Required scope: {required_scope}")


class MissingScopeError(UserError):
    """OAuth scope missing for the requested operation."""

    def __init__(self, scope: str) -> None:
        super().__init__(f"Missing OAuth scope: {scope}. Re-authorize the app with this scope.")


class RateLimitError(UserError):
    """Rate limit exceeded."""

    def __init__(self, retry_after: int | None = None) -> None:
        msg = "Rate limit exceeded."
        if retry_after:
            msg += f" Retry after {retry_after} seconds."
        super().__init__(msg)


class SlackApiError(UserError):
    """Error from Slack API.

    The message is sanitized to remove any potential token references.
    """

    def __init__(self, error_code: str, message: str = "") -> None:
        safe_message = message
        for env_var in ("SLACK_USER_TOKEN", "SLACK_COOKIE_TOKEN", "SLACK_COOKIE_D"):
            secret = os.environ.get(env_var, "")
            if secret:
                safe_message = safe_message.replace(secret, "***")
        if safe_message:
            super().__init__(f"Slack API error '{error_code}': {safe_message}")
        else:
            super().__init__(f"Slack API error: {error_code}")


class ValidationError(UserError):
    """Input validation error."""

    pass

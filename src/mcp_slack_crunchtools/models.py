"""Input validation for Slack resource identifiers."""

import re

CHANNEL_ID_PATTERN = re.compile(r"^[CDG][A-Z0-9]{8,}$")
USER_ID_PATTERN = re.compile(r"^[UWB][A-Z0-9]{8,}$")
TEAM_ID_PATTERN = re.compile(r"^T[A-Z0-9]{8,}$")
FILE_ID_PATTERN = re.compile(r"^F[A-Z0-9]{8,}$")
TIMESTAMP_PATTERN = re.compile(r"^\d+\.\d+$")


def validate_channel_id(channel_id: str) -> str:
    """Validate a Slack channel ID (C/D/G prefix + 8+ alphanumeric)."""
    if not CHANNEL_ID_PATTERN.match(channel_id):
        raise ValueError(
            "channel_id must start with C, D, or G followed by 8+ uppercase alphanumeric chars"
        )
    return channel_id


def validate_user_id(user_id: str) -> str:
    """Validate a Slack user ID (U/W/B prefix + 8+ alphanumeric)."""
    if not USER_ID_PATTERN.match(user_id):
        raise ValueError(
            "user_id must start with U, W, or B followed by 8+ uppercase alphanumeric chars"
        )
    return user_id


def validate_team_id(team_id: str) -> str:
    """Validate a Slack team ID (T prefix + 8+ alphanumeric)."""
    if not TEAM_ID_PATTERN.match(team_id):
        raise ValueError("team_id must start with T followed by 8+ uppercase alphanumeric chars")
    return team_id


def validate_file_id(file_id: str) -> str:
    """Validate a Slack file ID (F prefix + 8+ alphanumeric)."""
    if not FILE_ID_PATTERN.match(file_id):
        raise ValueError("file_id must start with F followed by 8+ uppercase alphanumeric chars")
    return file_id


def validate_timestamp(ts: str) -> str:
    """Validate a Slack message timestamp (digits.digits)."""
    if not TIMESTAMP_PATTERN.match(ts):
        raise ValueError("timestamp must be in format digits.digits (e.g., 1234567890.123456)")
    return ts

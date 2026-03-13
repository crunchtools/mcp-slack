"""Tests for input validation."""

import pytest

from mcp_slack_crunchtools.models import (
    validate_channel_id,
    validate_file_id,
    validate_team_id,
    validate_timestamp,
    validate_user_id,
)


class TestChannelIdValidation:
    """Tests for channel_id validation."""

    def test_valid_public_channel(self) -> None:
        """Public channel ID (C prefix) should pass."""
        assert validate_channel_id("C0123456789") == "C0123456789"

    def test_valid_dm_channel(self) -> None:
        """DM channel ID (D prefix) should pass."""
        assert validate_channel_id("D0123456789") == "D0123456789"

    def test_valid_group_channel(self) -> None:
        """Group channel ID (G prefix) should pass."""
        assert validate_channel_id("G0123456789") == "G0123456789"

    def test_valid_long_channel_id(self) -> None:
        """Longer channel IDs should pass."""
        assert validate_channel_id("C012345678901") == "C012345678901"

    def test_invalid_prefix(self) -> None:
        """Channel ID with wrong prefix should fail."""
        with pytest.raises(ValueError, match="channel_id"):
            validate_channel_id("U0123456789")

    def test_too_short(self) -> None:
        """Channel ID that is too short should fail."""
        with pytest.raises(ValueError, match="channel_id"):
            validate_channel_id("C01234")

    def test_lowercase_rejected(self) -> None:
        """Lowercase characters should fail."""
        with pytest.raises(ValueError, match="channel_id"):
            validate_channel_id("C0123456abc")

    def test_empty_string(self) -> None:
        """Empty string should fail."""
        with pytest.raises(ValueError, match="channel_id"):
            validate_channel_id("")

    def test_special_characters(self) -> None:
        """Special characters should fail."""
        with pytest.raises(ValueError, match="channel_id"):
            validate_channel_id("C0123456!@#")


class TestUserIdValidation:
    """Tests for user_id validation."""

    def test_valid_user_id(self) -> None:
        """Standard user ID (U prefix) should pass."""
        assert validate_user_id("U0123456789") == "U0123456789"

    def test_valid_enterprise_user(self) -> None:
        """Enterprise user ID (W prefix) should pass."""
        assert validate_user_id("W0123456789") == "W0123456789"

    def test_valid_bot_user(self) -> None:
        """Bot user ID (B prefix) should pass."""
        assert validate_user_id("B0123456789") == "B0123456789"

    def test_invalid_prefix(self) -> None:
        """User ID with wrong prefix should fail."""
        with pytest.raises(ValueError, match="user_id"):
            validate_user_id("C0123456789")

    def test_too_short(self) -> None:
        """User ID that is too short should fail."""
        with pytest.raises(ValueError, match="user_id"):
            validate_user_id("U01234")


class TestTeamIdValidation:
    """Tests for team_id validation."""

    def test_valid_team_id(self) -> None:
        """Valid team ID should pass."""
        assert validate_team_id("T0123456789") == "T0123456789"

    def test_invalid_prefix(self) -> None:
        """Team ID with wrong prefix should fail."""
        with pytest.raises(ValueError, match="team_id"):
            validate_team_id("U0123456789")

    def test_too_short(self) -> None:
        """Team ID that is too short should fail."""
        with pytest.raises(ValueError, match="team_id"):
            validate_team_id("T01234")


class TestFileIdValidation:
    """Tests for file_id validation."""

    def test_valid_file_id(self) -> None:
        """Valid file ID should pass."""
        assert validate_file_id("F0123456789") == "F0123456789"

    def test_invalid_prefix(self) -> None:
        """File ID with wrong prefix should fail."""
        with pytest.raises(ValueError, match="file_id"):
            validate_file_id("C0123456789")

    def test_too_short(self) -> None:
        """File ID that is too short should fail."""
        with pytest.raises(ValueError, match="file_id"):
            validate_file_id("F01234")


class TestTimestampValidation:
    """Tests for message timestamp validation."""

    def test_valid_timestamp(self) -> None:
        """Standard Slack timestamp should pass."""
        assert validate_timestamp("1234567890.123456") == "1234567890.123456"

    def test_valid_short_timestamp(self) -> None:
        """Short decimal timestamp should pass."""
        assert validate_timestamp("1234567890.1") == "1234567890.1"

    def test_missing_decimal(self) -> None:
        """Timestamp without decimal should fail."""
        with pytest.raises(ValueError, match="timestamp"):
            validate_timestamp("1234567890")

    def test_non_numeric(self) -> None:
        """Non-numeric timestamp should fail."""
        with pytest.raises(ValueError, match="timestamp"):
            validate_timestamp("abc.def")

    def test_empty_string(self) -> None:
        """Empty string should fail."""
        with pytest.raises(ValueError, match="timestamp"):
            validate_timestamp("")

    def test_multiple_dots(self) -> None:
        """Multiple dots should fail."""
        with pytest.raises(ValueError, match="timestamp"):
            validate_timestamp("123.456.789")

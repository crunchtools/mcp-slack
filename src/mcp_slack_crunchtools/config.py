"""Secure configuration handling with SecretStr credential storage."""

import logging
import os

from pydantic import SecretStr

from .errors import ConfigurationError

logger = logging.getLogger(__name__)


class Config:
    """Secure configuration handling.

    Supports two auth modes:
      - OAuth: Set SLACK_USER_TOKEN (xoxp-...)
      - Cookie: Set SLACK_COOKIE_TOKEN (xoxc-...) and SLACK_COOKIE_D (xoxd-...)
    """

    def __init__(self) -> None:
        oauth_token = os.environ.get("SLACK_USER_TOKEN")
        cookie_token = os.environ.get("SLACK_COOKIE_TOKEN")
        cookie_d = os.environ.get("SLACK_COOKIE_D")

        if oauth_token:
            self._token = SecretStr(oauth_token)
            self._cookie_d: SecretStr | None = None
            self._auth_mode = "oauth"
            logger.info("Configuration loaded (OAuth token mode)")
            return

        if cookie_token and cookie_d:
            self._token = SecretStr(cookie_token)
            self._cookie_d = SecretStr(cookie_d)
            self._auth_mode = "cookie"
            logger.info("Configuration loaded (cookie auth mode)")
            return

        if cookie_token:
            raise ConfigurationError(
                "SLACK_COOKIE_D environment variable required when using SLACK_COOKIE_TOKEN. "
                "Extract the 'd' cookie value from your browser's Slack session."
            )

        raise ConfigurationError(
            "Slack authentication required. Set one of:\n"
            "  - SLACK_USER_TOKEN (xoxp-...) for OAuth app token\n"
            "  - SLACK_COOKIE_TOKEN (xoxc-...) + SLACK_COOKIE_D (xoxd-...) for cookie auth"
        )

    @property
    def token(self) -> str:
        """Get token value for API calls."""
        return self._token.get_secret_value()

    @property
    def cookie_d(self) -> str | None:
        """Get the d cookie value for cookie auth mode."""
        if self._cookie_d is None:
            return None
        return self._cookie_d.get_secret_value()

    @property
    def auth_mode(self) -> str:
        """Get the authentication mode: 'oauth' or 'cookie'."""
        return self._auth_mode

    @property
    def api_base_url(self) -> str:
        """Hardcoded to prevent SSRF — not configurable by design."""
        return "https://slack.com/api"

    def __repr__(self) -> str:
        """Safe repr that never exposes secrets."""
        return f"Config(mode={self._auth_mode}, token=***)"

    def __str__(self) -> str:
        """Safe str that never exposes secrets."""
        return f"Config(mode={self._auth_mode}, token=***)"


_config: Config | None = None


def get_config() -> Config:
    """Get the global configuration instance.

    This function lazily initializes the configuration on first call.
    Subsequent calls return the same instance.

    Returns:
        The global Config instance.

    Raises:
        ConfigurationError: If configuration is invalid.
    """
    global _config
    if _config is None:
        _config = Config()
    return _config

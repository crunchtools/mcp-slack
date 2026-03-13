"""Slack MCP tools.

This package contains all the MCP tool implementations for Slack operations.
All tools are read-only.
"""

from .channels import (
    get_channel_history,
    get_channel_info,
    get_thread_replies,
    list_channel_members,
    list_channels,
)
from .messages import (
    get_reactions,
    list_reactions,
    list_stars,
    search_messages,
)
from .users import (
    auth_test,
    get_file_info,
    get_user_info,
    get_user_profile,
    list_files,
    list_users,
)

__all__ = [
    # Auth
    "auth_test",
    # Channels
    "list_channels",
    "get_channel_info",
    "get_channel_history",
    "get_thread_replies",
    "list_channel_members",
    # Messages
    "search_messages",
    "get_reactions",
    "list_reactions",
    "list_stars",
    # Users
    "get_user_info",
    "list_users",
    "get_user_profile",
    # Files
    "list_files",
    "get_file_info",
]

"""Message-related tools (read-only).

Tools for searching messages, listing reactions, and starred items.
"""

from typing import Any

from ..client import get_client
from ..models import validate_channel_id, validate_timestamp


async def search_messages(
    query: str,
    sort: str = "timestamp",
    sort_dir: str = "desc",
    count: int = 20,
    page: int = 1,
) -> dict[str, Any]:
    """Search messages in the workspace.

    Args:
        query: Search query string (supports Slack search modifiers like
               from:user, in:channel, has:link, before:date, after:date)
        sort: Sort by "timestamp" or "score" (default: timestamp)
        sort_dir: Sort direction "asc" or "desc" (default: desc)
        count: Results per page, 1-100 (default: 20)
        page: Page number for pagination (default: 1)

    Returns:
        Dictionary with messages matches and pagination info
    """
    client = get_client()

    params: dict[str, Any] = {
        "query": query,
        "sort": sort if sort in ("timestamp", "score") else "timestamp",
        "sort_dir": sort_dir if sort_dir in ("asc", "desc") else "desc",
        "count": min(max(count, 1), 100),
        "page": max(page, 1),
    }

    response = await client.api_call("search.messages", params)

    messages = response.get("messages", {})
    return {
        "matches": messages.get("matches", []),
        "total": messages.get("total", 0),
        "pagination": messages.get("pagination", {}),
    }


async def get_reactions(
    channel_id: str,
    timestamp: str,
    full: bool = False,
) -> dict[str, Any]:
    """Get reactions for a specific message.

    Args:
        channel_id: Slack channel ID (C/D/G prefix)
        timestamp: Message timestamp
        full: If true, return complete reaction list for each emoji

    Returns:
        Dictionary with the message and its reactions
    """
    channel_id = validate_channel_id(channel_id)
    timestamp = validate_timestamp(timestamp)
    client = get_client()

    params: dict[str, Any] = {
        "channel": channel_id,
        "timestamp": timestamp,
    }
    if full:
        params["full"] = "true"

    response = await client.api_call("reactions.get", params)

    return {"message": response.get("message", {})}


async def list_reactions(
    user_id: str | None = None,
    count: int = 100,
    page: int = 1,
    full: bool = False,
) -> dict[str, Any]:
    """List reactions made by a user.

    Args:
        user_id: User ID to list reactions for (default: authenticated user)
        count: Results per page, 1-100 (default: 100)
        page: Page number for pagination (default: 1)
        full: If true, return complete reaction list

    Returns:
        Dictionary with reaction items and pagination info
    """
    client = get_client()

    params: dict[str, Any] = {
        "count": min(max(count, 1), 100),
        "page": max(page, 1),
    }
    if user_id:
        from ..models import validate_user_id

        user_id = validate_user_id(user_id)
        params["user"] = user_id
    if full:
        params["full"] = "true"

    response = await client.api_call("reactions.list", params)

    return {
        "items": response.get("items", []),
        "paging": response.get("paging", {}),
    }


async def list_stars(
    count: int = 100,
    page: int = 1,
    cursor: str | None = None,
) -> dict[str, Any]:
    """List starred items for the authenticated user.

    Args:
        count: Results per page, 1-100 (default: 100)
        page: Page number for pagination (default: 1)
        cursor: Pagination cursor from previous response

    Returns:
        Dictionary with starred items and pagination info
    """
    client = get_client()

    params: dict[str, Any] = {
        "count": min(max(count, 1), 100),
        "page": max(page, 1),
    }
    if cursor:
        params["cursor"] = cursor

    response = await client.api_call("stars.list", params)

    return {
        "items": response.get("items", []),
        "paging": response.get("paging", {}),
    }

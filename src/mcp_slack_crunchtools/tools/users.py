"""User and file-related tools (read-only).

Tools for authentication testing, user info, profiles, and file metadata.
"""

from typing import Any

from ..client import get_client
from ..models import validate_file_id, validate_user_id


async def auth_test() -> dict[str, Any]:
    """Test the Slack authentication and get info about the token owner.

    Returns:
        Dictionary with authenticated user info (user_id, team_id, team, user, url)
    """
    client = get_client()

    response = await client.api_call("auth.test")

    return {
        "user_id": response.get("user_id", ""),
        "team_id": response.get("team_id", ""),
        "team": response.get("team", ""),
        "user": response.get("user", ""),
        "url": response.get("url", ""),
        "bot_id": response.get("bot_id", ""),
    }


async def get_user_info(user_id: str) -> dict[str, Any]:
    """Get information about a user.

    Args:
        user_id: Slack user ID (U/W/B prefix)

    Returns:
        Dictionary with user details
    """
    user_id = validate_user_id(user_id)
    client = get_client()

    response = await client.api_call("users.info", {"user": user_id})

    return {"user": response.get("user", {})}


async def list_users(
    limit: int = 200,
    cursor: str | None = None,
) -> dict[str, Any]:
    """List users in the workspace.

    Args:
        limit: Max users to return, 1-1000 (default: 200)
        cursor: Pagination cursor from previous response

    Returns:
        Dictionary with members list and pagination metadata
    """
    client = get_client()

    params: dict[str, Any] = {
        "limit": min(max(limit, 1), 1000),
    }
    if cursor:
        params["cursor"] = cursor

    response = await client.api_call("users.list", params)

    return {
        "members": response.get("members", []),
        "response_metadata": response.get("response_metadata", {}),
    }


async def get_user_profile(
    user_id: str,
    include_labels: bool = False,
) -> dict[str, Any]:
    """Get a user's profile information.

    Args:
        user_id: Slack user ID (U/W/B prefix)
        include_labels: Include custom profile field labels

    Returns:
        Dictionary with user profile details
    """
    user_id = validate_user_id(user_id)
    client = get_client()

    params: dict[str, Any] = {"user": user_id}
    if include_labels:
        params["include_labels"] = "true"

    response = await client.api_call("users.profile.get", params)

    return {"profile": response.get("profile", {})}


async def list_files(
    channel_id: str | None = None,
    user_id: str | None = None,
    types: str | None = None,
    count: int = 100,
    page: int = 1,
    ts_from: str | None = None,
    ts_to: str | None = None,
) -> dict[str, Any]:
    """List files in the workspace (metadata only, no content download).

    Args:
        channel_id: Filter by channel ID
        user_id: Filter by user who uploaded
        types: Filter by file types (comma-separated: spaces, snippets, images,
               gdocs, zips, pdfs, all)
        count: Results per page, 1-100 (default: 100)
        page: Page number for pagination (default: 1)
        ts_from: Filter files created after this Unix timestamp
        ts_to: Filter files created before this Unix timestamp

    Returns:
        Dictionary with files list and pagination info
    """
    client = get_client()

    params: dict[str, Any] = {
        "count": min(max(count, 1), 100),
        "page": max(page, 1),
    }

    if channel_id:
        from ..models import validate_channel_id

        channel_id = validate_channel_id(channel_id)
        params["channel"] = channel_id
    if user_id:
        user_id = validate_user_id(user_id)
        params["user"] = user_id
    if types:
        params["types"] = types
    if ts_from:
        params["ts_from"] = ts_from
    if ts_to:
        params["ts_to"] = ts_to

    response = await client.api_call("files.list", params)

    return {
        "files": response.get("files", []),
        "paging": response.get("paging", {}),
    }


async def get_file_info(
    file_id: str,
    count: int = 100,
    page: int = 1,
) -> dict[str, Any]:
    """Get metadata about a file (no content download).

    Args:
        file_id: Slack file ID (F prefix)
        count: Number of comments per page (default: 100)
        page: Page of comments (default: 1)

    Returns:
        Dictionary with file metadata and comments
    """
    file_id = validate_file_id(file_id)
    client = get_client()

    params: dict[str, Any] = {
        "file": file_id,
        "count": min(max(count, 1), 100),
        "page": max(page, 1),
    }

    response = await client.api_call("files.info", params)

    return {
        "file": response.get("file", {}),
        "comments": response.get("comments", []),
        "paging": response.get("paging", {}),
    }

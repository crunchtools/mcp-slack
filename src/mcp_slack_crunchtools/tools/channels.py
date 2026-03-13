"""Channel-related tools (read-only).

Tools for listing channels, reading history, thread replies, and members.
"""

from typing import Any

from ..client import get_client
from ..models import validate_channel_id, validate_timestamp


async def list_channels(
    types: str = "public_channel,private_channel",
    exclude_archived: bool = True,
    limit: int = 200,
    cursor: str | None = None,
) -> dict[str, Any]:
    """List channels in the workspace.

    Args:
        types: Comma-separated channel types (public_channel, private_channel,
               mpim, im). Default: public_channel,private_channel
        exclude_archived: Exclude archived channels (default: True)
        limit: Max results per page, 1-1000 (default: 200)
        cursor: Pagination cursor from previous response

    Returns:
        Dictionary with channels list and pagination metadata
    """
    client = get_client()

    params: dict[str, Any] = {
        "types": types,
        "exclude_archived": str(exclude_archived).lower(),
        "limit": min(max(limit, 1), 1000),
    }
    if cursor:
        params["cursor"] = cursor

    response = await client.api_call("conversations.list", params)

    return {
        "channels": response.get("channels", []),
        "response_metadata": response.get("response_metadata", {}),
    }


async def get_channel_info(channel_id: str) -> dict[str, Any]:
    """Get detailed information about a channel.

    Args:
        channel_id: Slack channel ID (C/D/G prefix)

    Returns:
        Channel details
    """
    channel_id = validate_channel_id(channel_id)
    client = get_client()

    response = await client.api_call("conversations.info", {"channel": channel_id})

    return {"channel": response.get("channel", {})}


async def get_channel_history(
    channel_id: str,
    limit: int = 100,
    cursor: str | None = None,
    oldest: str | None = None,
    latest: str | None = None,
    inclusive: bool = False,
) -> dict[str, Any]:
    """Get message history from a channel.

    Args:
        channel_id: Slack channel ID (C/D/G prefix)
        limit: Max messages to return, 1-1000 (default: 100)
        cursor: Pagination cursor from previous response
        oldest: Only messages after this timestamp
        latest: Only messages before this timestamp
        inclusive: Include messages with oldest/latest timestamps

    Returns:
        Dictionary with messages list and pagination metadata
    """
    channel_id = validate_channel_id(channel_id)
    client = get_client()

    params: dict[str, Any] = {
        "channel": channel_id,
        "limit": min(max(limit, 1), 1000),
    }
    if cursor:
        params["cursor"] = cursor
    if oldest:
        oldest = validate_timestamp(oldest)
        params["oldest"] = oldest
    if latest:
        latest = validate_timestamp(latest)
        params["latest"] = latest
    if inclusive:
        params["inclusive"] = "true"

    response = await client.api_call("conversations.history", params)

    return {
        "messages": response.get("messages", []),
        "has_more": response.get("has_more", False),
        "response_metadata": response.get("response_metadata", {}),
    }


async def get_thread_replies(
    channel_id: str,
    thread_ts: str,
    limit: int = 100,
    cursor: str | None = None,
    oldest: str | None = None,
    latest: str | None = None,
    inclusive: bool = False,
) -> dict[str, Any]:
    """Get replies in a message thread.

    Args:
        channel_id: Slack channel ID (C/D/G prefix)
        thread_ts: Timestamp of the parent message
        limit: Max replies to return, 1-1000 (default: 100)
        cursor: Pagination cursor from previous response
        oldest: Only replies after this timestamp
        latest: Only replies before this timestamp
        inclusive: Include messages with oldest/latest timestamps

    Returns:
        Dictionary with messages list and pagination metadata
    """
    channel_id = validate_channel_id(channel_id)
    thread_ts = validate_timestamp(thread_ts)
    client = get_client()

    params: dict[str, Any] = {
        "channel": channel_id,
        "ts": thread_ts,
        "limit": min(max(limit, 1), 1000),
    }
    if cursor:
        params["cursor"] = cursor
    if oldest:
        oldest = validate_timestamp(oldest)
        params["oldest"] = oldest
    if latest:
        latest = validate_timestamp(latest)
        params["latest"] = latest
    if inclusive:
        params["inclusive"] = "true"

    response = await client.api_call("conversations.replies", params)

    return {
        "messages": response.get("messages", []),
        "has_more": response.get("has_more", False),
        "response_metadata": response.get("response_metadata", {}),
    }


async def list_channel_members(
    channel_id: str,
    limit: int = 200,
    cursor: str | None = None,
) -> dict[str, Any]:
    """List members of a channel.

    Args:
        channel_id: Slack channel ID (C/D/G prefix)
        limit: Max members to return, 1-1000 (default: 200)
        cursor: Pagination cursor from previous response

    Returns:
        Dictionary with member IDs list and pagination metadata
    """
    channel_id = validate_channel_id(channel_id)
    client = get_client()

    params: dict[str, Any] = {
        "channel": channel_id,
        "limit": min(max(limit, 1), 1000),
    }
    if cursor:
        params["cursor"] = cursor

    response = await client.api_call("conversations.members", params)

    return {
        "members": response.get("members", []),
        "response_metadata": response.get("response_metadata", {}),
    }

"""FastMCP server setup for Slack MCP.

This module creates and configures the MCP server with all read-only tools.
"""

import logging
from typing import Any

from fastmcp import FastMCP

from .tools import (
    auth_test,
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
)

logger = logging.getLogger(__name__)

# Create the FastMCP server
mcp = FastMCP(
    name="mcp-slack-crunchtools",
    version="0.1.2",
    instructions="Secure read-only MCP server for Slack workspaces",
)


# Auth tool


@mcp.tool()
async def slack_auth_test() -> dict[str, Any]:
    """Test Slack authentication and get info about the token owner.

    Returns the authenticated user's ID, team ID, team name, username, and workspace URL.
    Use this to verify the connection is working.
    """
    return await auth_test()


# Channel tools


@mcp.tool()
async def slack_list_channels(
    types: str = "public_channel,private_channel",
    exclude_archived: bool = True,
    limit: int = 200,
    cursor: str | None = None,
) -> dict[str, Any]:
    """List channels in the Slack workspace.

    Args:
        types: Comma-separated channel types: public_channel, private_channel, mpim, im
        exclude_archived: Exclude archived channels (default: true)
        limit: Max results per page, 1-1000 (default: 200)
        cursor: Pagination cursor from previous response

    Returns:
        List of channels with pagination metadata
    """
    return await list_channels(
        types=types, exclude_archived=exclude_archived, limit=limit, cursor=cursor
    )


@mcp.tool()
async def slack_get_channel_info(channel_id: str) -> dict[str, Any]:
    """Get detailed information about a Slack channel.

    Args:
        channel_id: Channel ID (starts with C, D, or G)

    Returns:
        Channel details including name, topic, purpose, member count
    """
    return await get_channel_info(channel_id=channel_id)


@mcp.tool()
async def slack_get_channel_history(
    channel_id: str,
    limit: int = 100,
    cursor: str | None = None,
    oldest: str | None = None,
    latest: str | None = None,
    inclusive: bool = False,
) -> dict[str, Any]:
    """Get message history from a Slack channel.

    Args:
        channel_id: Channel ID (starts with C, D, or G)
        limit: Max messages to return, 1-1000 (default: 100)
        cursor: Pagination cursor from previous response
        oldest: Only messages after this timestamp (e.g., 1234567890.123456)
        latest: Only messages before this timestamp
        inclusive: Include messages at oldest/latest boundary

    Returns:
        List of messages with pagination metadata
    """
    return await get_channel_history(
        channel_id=channel_id,
        limit=limit,
        cursor=cursor,
        oldest=oldest,
        latest=latest,
        inclusive=inclusive,
    )


@mcp.tool()
async def slack_get_thread_replies(
    channel_id: str,
    thread_ts: str,
    limit: int = 100,
    cursor: str | None = None,
    oldest: str | None = None,
    latest: str | None = None,
    inclusive: bool = False,
) -> dict[str, Any]:
    """Get replies in a Slack message thread.

    Args:
        channel_id: Channel ID (starts with C, D, or G)
        thread_ts: Timestamp of the parent message
        limit: Max replies to return, 1-1000 (default: 100)
        cursor: Pagination cursor from previous response
        oldest: Only replies after this timestamp
        latest: Only replies before this timestamp
        inclusive: Include messages at oldest/latest boundary

    Returns:
        List of thread messages with pagination metadata
    """
    return await get_thread_replies(
        channel_id=channel_id,
        thread_ts=thread_ts,
        limit=limit,
        cursor=cursor,
        oldest=oldest,
        latest=latest,
        inclusive=inclusive,
    )


@mcp.tool()
async def slack_list_channel_members(
    channel_id: str,
    limit: int = 200,
    cursor: str | None = None,
) -> dict[str, Any]:
    """List members of a Slack channel.

    Args:
        channel_id: Channel ID (starts with C, D, or G)
        limit: Max members to return, 1-1000 (default: 200)
        cursor: Pagination cursor from previous response

    Returns:
        List of member user IDs with pagination metadata
    """
    return await list_channel_members(channel_id=channel_id, limit=limit, cursor=cursor)


# Message tools


@mcp.tool()
async def slack_search_messages(
    query: str,
    sort: str = "timestamp",
    sort_dir: str = "desc",
    count: int = 20,
    page: int = 1,
) -> dict[str, Any]:
    """Search messages in the Slack workspace.

    Supports Slack search modifiers: from:user, in:channel, has:link,
    before:date, after:date, during:month.

    Args:
        query: Search query string
        sort: Sort by "timestamp" or "score" (default: timestamp)
        sort_dir: Sort direction "asc" or "desc" (default: desc)
        count: Results per page, 1-100 (default: 20)
        page: Page number (default: 1)

    Returns:
        Matching messages with total count and pagination info
    """
    return await search_messages(query=query, sort=sort, sort_dir=sort_dir, count=count, page=page)


@mcp.tool()
async def slack_get_reactions(
    channel_id: str,
    timestamp: str,
    full: bool = False,
) -> dict[str, Any]:
    """Get reactions for a specific Slack message.

    Args:
        channel_id: Channel ID (starts with C, D, or G)
        timestamp: Message timestamp (e.g., 1234567890.123456)
        full: If true, return complete reaction list for each emoji

    Returns:
        Message with its reactions
    """
    return await get_reactions(channel_id=channel_id, timestamp=timestamp, full=full)


@mcp.tool()
async def slack_list_reactions(
    user_id: str | None = None,
    count: int = 100,
    page: int = 1,
    full: bool = False,
) -> dict[str, Any]:
    """List reactions made by a user.

    Args:
        user_id: User ID to list reactions for (default: authenticated user)
        count: Results per page, 1-100 (default: 100)
        page: Page number (default: 1)
        full: If true, return complete reaction list

    Returns:
        Reaction items with pagination info
    """
    return await list_reactions(user_id=user_id, count=count, page=page, full=full)


@mcp.tool()
async def slack_list_stars(
    count: int = 100,
    page: int = 1,
    cursor: str | None = None,
) -> dict[str, Any]:
    """List starred items for the authenticated user.

    Args:
        count: Results per page, 1-100 (default: 100)
        page: Page number (default: 1)
        cursor: Pagination cursor from previous response

    Returns:
        Starred items with pagination info
    """
    return await list_stars(count=count, page=page, cursor=cursor)


# User tools


@mcp.tool()
async def slack_get_user_info(user_id: str) -> dict[str, Any]:
    """Get information about a Slack user.

    Args:
        user_id: User ID (starts with U, W, or B)

    Returns:
        User details including name, email, status, timezone
    """
    return await get_user_info(user_id=user_id)


@mcp.tool()
async def slack_list_users(
    limit: int = 200,
    cursor: str | None = None,
) -> dict[str, Any]:
    """List users in the Slack workspace.

    Args:
        limit: Max users to return, 1-1000 (default: 200)
        cursor: Pagination cursor from previous response

    Returns:
        List of workspace members with pagination metadata
    """
    return await list_users(limit=limit, cursor=cursor)


@mcp.tool()
async def slack_get_user_profile(
    user_id: str,
    include_labels: bool = False,
) -> dict[str, Any]:
    """Get a Slack user's profile information.

    Args:
        user_id: User ID (starts with U, W, or B)
        include_labels: Include custom profile field labels

    Returns:
        User profile with display name, status, image URLs, custom fields
    """
    return await get_user_profile(user_id=user_id, include_labels=include_labels)


# File tools


@mcp.tool()
async def slack_list_files(
    channel_id: str | None = None,
    user_id: str | None = None,
    types: str | None = None,
    count: int = 100,
    page: int = 1,
    ts_from: str | None = None,
    ts_to: str | None = None,
) -> dict[str, Any]:
    """List files in the Slack workspace (metadata only, no content download).

    Args:
        channel_id: Filter by channel ID
        user_id: Filter by uploader's user ID
        types: Filter by types (comma-separated: spaces, snippets, images, gdocs, zips, pdfs, all)
        count: Results per page, 1-100 (default: 100)
        page: Page number (default: 1)
        ts_from: Filter files created after this Unix timestamp
        ts_to: Filter files created before this Unix timestamp

    Returns:
        File metadata list with pagination info
    """
    return await list_files(
        channel_id=channel_id,
        user_id=user_id,
        types=types,
        count=count,
        page=page,
        ts_from=ts_from,
        ts_to=ts_to,
    )


@mcp.tool()
async def slack_get_file_info(
    file_id: str,
    count: int = 100,
    page: int = 1,
) -> dict[str, Any]:
    """Get metadata about a Slack file (no content download).

    Args:
        file_id: File ID (starts with F)
        count: Number of comments per page (default: 100)
        page: Page of comments (default: 1)

    Returns:
        File metadata, comments, and pagination info
    """
    return await get_file_info(file_id=file_id, count=count, page=page)

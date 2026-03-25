"""MCP Slack CrunchTools - Secure read-only MCP server for Slack.

A security-focused read-only MCP server for Slack workspaces.

Usage:
    # Run directly
    mcp-slack-crunchtools

    # Or with Python module
    python -m mcp_slack_crunchtools

    # With uvx
    uvx mcp-slack-crunchtools

Environment Variables (one of these auth modes):
    SLACK_USER_TOKEN: Slack User OAuth Token (xoxp-).
    SLACK_COOKIE_TOKEN + SLACK_COOKIE_D: Browser cookie auth (xoxc- + xoxd-).

Example with Claude Code:
    claude mcp add mcp-slack-crunchtools \\
        --env SLACK_USER_TOKEN=xoxp-your-token \\
        -- uvx mcp-slack-crunchtools
"""

import argparse

from .server import mcp

__version__ = "0.1.2"
__all__ = ["main", "mcp"]


def main() -> None:
    """Main entry point for the MCP server."""
    parser = argparse.ArgumentParser(description="MCP server for Slack")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport protocol (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to for HTTP transports (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8005,
        help="Port to bind to for HTTP transports (default: 8005)",
    )
    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run()
    else:
        mcp.run(transport=args.transport, host=args.host, port=args.port)

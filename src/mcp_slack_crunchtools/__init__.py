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

from .server import mcp

__version__ = "0.1.0"
__all__ = ["main", "mcp"]


def main() -> None:
    """Main entry point for the MCP server."""
    mcp.run()

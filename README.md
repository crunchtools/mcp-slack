# mcp-slack-crunchtools

Secure read-only MCP server for Slack workspaces. Provides Claude Code (and other MCP clients) with access to your Slack channels, messages, users, and files without any write permissions.

## Features

- **Read-only**: 15 tools, all read-only. Never posts, edits, or deletes anything.
- **Secure**: 6-layer security model (input validation, token handling, client hardening, output sanitization, runtime protection, supply chain security).
- **User OAuth Token**: Uses `xoxp-` tokens for user-scoped access to your workspace.
- **No SDK dependency**: Uses `httpx` directly for minimal, auditable HTTP calls.

## Quick Start

### Using uvx (Recommended)

```bash
claude mcp add mcp-slack-crunchtools \
    --env SLACK_USER_TOKEN=xoxp-your-token \
    -- uvx mcp-slack-crunchtools
```

### Using Container

```bash
claude mcp add mcp-slack-crunchtools \
    --env SLACK_USER_TOKEN=xoxp-your-token \
    -- podman run -i --rm -e SLACK_USER_TOKEN quay.io/crunchtools/mcp-slack
```

### Local Development

```bash
claude mcp add mcp-slack-crunchtools \
    --env SLACK_USER_TOKEN=xoxp-your-token \
    -- uv run mcp-slack-crunchtools
```

## Setup

See [CLAUDE.md](CLAUDE.md) for detailed instructions on creating a Slack app and obtaining a User OAuth Token.

## Tools

| Tool | Description |
|------|-------------|
| `slack_auth_test` | Test connection and get token owner info |
| `slack_list_channels` | List workspace channels |
| `slack_get_channel_info` | Get channel details |
| `slack_get_channel_history` | Read channel messages |
| `slack_get_thread_replies` | Read thread replies |
| `slack_list_channel_members` | List channel members |
| `slack_search_messages` | Search messages |
| `slack_get_reactions` | Get message reactions |
| `slack_list_reactions` | List user's reactions |
| `slack_list_stars` | List starred items |
| `slack_get_user_info` | Get user details |
| `slack_list_users` | List workspace members |
| `slack_get_user_profile` | Get user profile |
| `slack_list_files` | List files (metadata only) |
| `slack_get_file_info` | Get file metadata |

## Security

See [SECURITY.md](SECURITY.md) for the full security design document.

## License

AGPL-3.0-or-later

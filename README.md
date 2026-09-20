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

See [CLAUDE.md](CLAUDE.md) for detailed instructions on creating a Slack app and
obtaining a User OAuth Token.

## Configuration

Authentication uses one of two mutually exclusive modes. The server picks cookie
mode when both cookie variables are set, and token mode otherwise.

| Variable | Required | Default | Description |
|---|---|---|---|
| `SLACK_USER_TOKEN` | token mode | — | User OAuth token (`xoxp-...`) from a Slack app installed in the workspace. |
| `SLACK_COOKIE_TOKEN` | cookie mode | — | Browser session token (`xoxc-...`). Must be paired with `SLACK_COOKIE_D`. |
| `SLACK_COOKIE_D` | cookie mode | — | Value of the `d` cookie (`xoxd-...`) from the same browser session. Sent as a `Cookie:` header alongside `SLACK_COOKIE_TOKEN`. |
| `SLACK_ADD_MESSAGE_DELAY` | no | `3m` | How far ahead outgoing messages are scheduled, giving you a window to cancel one. Duration string: `30s`, `5m`, `2h`, or a bare integer for seconds. Set to `0`, `0s`, `none`, or `false` to disable scheduling and post immediately. |

### Which auth mode to use

**Cookie mode is the working path for this deployment.** Token mode requires a
Slack app to be created and approved in the workspace; where that approval is not
available, cookie mode is the only way to authenticate at all.

Cookie mode borrows an existing browser session rather than holding a credential
issued to an application. That has consequences worth stating plainly:

- Both values are live session credentials. Anything holding them can act as you
  in Slack, with your full access. Treat them exactly as you would your password.
- They expire when the browser session does, so cookie mode needs periodic
  re-extraction. A sudden wave of auth failures usually means the session rotated,
  not that the server broke.
- Slack does not issue these for programmatic use and can invalidate them at any
  time. Cookie mode is a workaround for the absence of an approved app, not a
  supported integration path.

Prefer `SLACK_USER_TOKEN` whenever a Slack app can actually be installed.

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

<!-- mcp-name: io.github.crunchtools/slack -->

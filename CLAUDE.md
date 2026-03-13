# Claude Code Instructions

This is a secure read-only MCP server for Slack workspaces.

## Quick Start

### Option 1: Using uvx (Recommended)

```bash
claude mcp add mcp-slack-crunchtools \
    --env SLACK_USER_TOKEN=xoxp-your-token \
    -- uvx mcp-slack-crunchtools
```

### Option 2: Using Container

```bash
claude mcp add mcp-slack-crunchtools \
    --env SLACK_USER_TOKEN=xoxp-your-token \
    -- podman run -i --rm -e SLACK_USER_TOKEN quay.io/crunchtools/mcp-slack
```

### Option 3: Local Development

```bash
cd ~/Projects/crunchtools/mcp-slack
claude mcp add mcp-slack-crunchtools \
    --env SLACK_USER_TOKEN=xoxp-your-token \
    -- uv run mcp-slack-crunchtools
```

## Creating a Slack User OAuth Token

### Step-by-Step Instructions

1. **Go to Slack API Apps**
   - Navigate to https://api.slack.com/apps
   - Sign in with your Slack account

2. **Create a New App**
   - Click "Create New App"
   - Choose "From scratch"
   - Enter app name: `mcp-slack-crunchtools`
   - Select your workspace
   - Click "Create App"

3. **Configure OAuth Scopes**
   - In the left sidebar, click "OAuth & Permissions"
   - Scroll to "User Token Scopes"
   - Click "Add an OAuth Scope" for each scope below

4. **Required Scopes (Read-Only)**

   | Scope | Purpose |
   |-------|---------|
   | `channels:read` | List public channels, get channel info |
   | `channels:history` | Read messages in public channels |
   | `groups:read` | List private channels |
   | `groups:history` | Read messages in private channels |
   | `im:read` | List direct messages |
   | `im:history` | Read direct message history |
   | `mpim:read` | List group DMs |
   | `mpim:history` | Read group DM history |
   | `search:read` | Search messages |
   | `users:read` | List users, get user info |
   | `users:read.email` | Access user email addresses |
   | `users.profile:read` | Read user profiles |
   | `reactions:read` | List reactions |
   | `stars:read` | List starred items |
   | `files:read` | List files and file metadata |

5. **Install the App**
   - Scroll up to "OAuth Tokens for Your Workspace"
   - Click "Install to Workspace"
   - Review the permissions and click "Allow"

6. **Copy the User OAuth Token**
   - Copy the "User OAuth Token" (starts with `xoxp-`)
   - **Store it securely** - it will not be shown again in full

7. **Add to Claude Code**
   ```bash
   claude mcp add mcp-slack-crunchtools \
       --env SLACK_USER_TOKEN=xoxp-your-copied-token \
       -- uvx mcp-slack-crunchtools
   ```

### Scope Sets by Use Case

#### Minimal (channels only)
| Scope | Purpose |
|-------|---------|
| `channels:read` | List channels |
| `channels:history` | Read channel messages |

#### Standard (recommended)
All 15 scopes listed above for full read-only access.

### Security Best Practices

- **Read-only scopes only**: This server never writes to Slack
- **User token, not bot**: Uses `xoxp-` token for user-scoped access
- **Never commit tokens**: Don't put tokens in code or config files
- **Rotate regularly**: Revoke and recreate tokens periodically
- **Least privilege**: Only add scopes you actually need

## Available Tools (all read-only)

### Authentication
- `slack_auth_test` - Test connection and get token owner info

### Channels
- `slack_list_channels` - List workspace channels with filtering
- `slack_get_channel_info` - Get channel details (name, topic, purpose)
- `slack_get_channel_history` - Read channel messages with pagination
- `slack_get_thread_replies` - Read thread replies
- `slack_list_channel_members` - List channel member IDs

### Messages
- `slack_search_messages` - Search messages (supports from:, in:, has:, etc.)
- `slack_get_reactions` - Get reactions on a specific message
- `slack_list_reactions` - List reactions by a user
- `slack_list_stars` - List starred items

### Users
- `slack_get_user_info` - Get user details
- `slack_list_users` - List workspace members
- `slack_get_user_profile` - Get user profile with custom fields

### Files
- `slack_list_files` - List files (metadata only)
- `slack_get_file_info` - Get file metadata and comments

## Example Usage

```
User: Test my Slack connection
User: List my Slack channels
User: Show messages from #general
User: Search Slack for messages about deployment
User: Who is user U0123456789?
User: List files shared in #engineering
```

## Development

```bash
# Install dependencies
uv sync --all-extras

# Run tests
SLACK_USER_TOKEN=xoxp-test uv run pytest -v

# Lint
uv run ruff check src tests

# Type check
uv run mypy src
```

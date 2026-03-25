# Specification: Baseline Tool Inventory

> **Spec ID:** 000-baseline
> **Status:** Implemented
> **Version:** 0.1.0
> **Author:** crunchtools.com
> **Date:** 2026-03-25

## Overview

Baseline specification documenting the 15 read-only tools shipped in mcp-slack-crunchtools v0.1.0. All tools use the Slack Web API via POST requests with form-encoded parameters. Two authentication modes are supported: User OAuth Token (xoxp-) and Cookie Auth (xoxc- + xoxd-).

---

## Tool Inventory

### Auth (1 tool)

| Tool | Slack API Method | Description |
|------|-----------------|-------------|
| `slack_auth_test` | `auth.test` | Test connection and get token owner info |

### Channels (5 tools)

| Tool | Slack API Method | Description |
|------|-----------------|-------------|
| `slack_list_channels` | `conversations.list` | List workspace channels with filtering |
| `slack_get_channel_info` | `conversations.info` | Get channel details (name, topic, purpose) |
| `slack_get_channel_history` | `conversations.history` | Read channel messages with pagination |
| `slack_get_thread_replies` | `conversations.replies` | Read thread replies |
| `slack_list_channel_members` | `conversations.members` | List channel member IDs |

### Messages (4 tools)

| Tool | Slack API Method | Description |
|------|-----------------|-------------|
| `slack_search_messages` | `search.messages` | Search messages (supports from:, in:, has:, etc.) |
| `slack_get_reactions` | `reactions.get` | Get reactions on a specific message |
| `slack_list_reactions` | `reactions.list` | List reactions by a user |
| `slack_list_stars` | `stars.list` | List starred items |

### Users (3 tools)

| Tool | Slack API Method | Description |
|------|-----------------|-------------|
| `slack_get_user_info` | `users.info` | Get user details |
| `slack_list_users` | `users.list` | List workspace members |
| `slack_get_user_profile` | `users.profile.get` | Get user profile with custom fields |

### Files (2 tools)

| Tool | Slack API Method | Description |
|------|-----------------|-------------|
| `slack_list_files` | `files.list` | List files (metadata only) |
| `slack_get_file_info` | `files.info` | Get file metadata and comments |

---

## Security Considerations

### Layer 1 — Token Protection
- Two auth modes: xoxp- (OAuth) and xoxc-/xoxd- (cookie)
- Tokens stored as environment variables only
- Never logged or exposed in error messages

### Layer 2 — Input Validation
- Channel/user IDs validated by Slack API
- Pagination limits enforced (1-1000)

### Layer 3 — API Hardening
- Hardcoded base URL: `https://slack.com/api`
- Auth via Bearer header, cookies via Cookie header
- TLS validation enforced, 30s timeout, 10MB response limit

### Layer 4 — Dangerous Operation Prevention
- Read-only tools only — no writes or deletes
- No filesystem, shell, or eval access

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-03-25 | Initial baseline: 15 tools across 5 categories |

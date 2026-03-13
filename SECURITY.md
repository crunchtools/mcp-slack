# Security Design Document

This document describes the security architecture of mcp-slack-crunchtools.

## 1. Threat Model

### 1.1 Assets to Protect

| Asset | Sensitivity | Impact if Compromised |
|-------|-------------|----------------------|
| Slack User OAuth Token | Critical | Full read access to workspace messages, files, users |
| Message Content | High | Confidential communications exposed |
| User Information | Medium | PII disclosure (names, emails, statuses) |
| File Metadata | Medium | Information about shared documents |

### 1.2 Threat Actors

| Actor | Capability | Motivation |
|-------|------------|------------|
| Malicious AI Agent | Can craft tool inputs | Data exfiltration, privilege escalation |
| Local Attacker | Access to filesystem | Token theft, configuration tampering |
| Network Attacker | Man-in-the-middle | Token interception (mitigated by TLS) |

### 1.3 Attack Vectors

| Vector | Description | Mitigation |
|--------|-------------|------------|
| **Token Leakage** | Token exposed in logs, errors, or outputs | Never log tokens, scrub from errors |
| **Input Injection** | Malicious channel/user IDs | Strict regex validation |
| **Path Traversal** | Manipulated file paths | No filesystem operations |
| **SSRF** | Redirect API calls to internal services | Hardcoded API base URL |
| **Denial of Service** | Exhaust Slack rate limits | Rate limiting awareness |
| **Privilege Escalation** | Attempt write operations | Read-only tools only, no write API calls |
| **Supply Chain** | Compromised dependencies | Automated CVE scanning |

## 2. Security Architecture

### 2.1 Defense in Depth Layers

```
+---------------------------------------------------------+
| Layer 1: Input Validation                               |
| - Regex ID validation (C/D/G/U/W/B/T/F prefixes)       |
| - Timestamp format validation                           |
| - Parameter bounds checking (limit, page, count)        |
+---------------------------------------------------------+
| Layer 2: Token Handling                                 |
| - Environment variable only (never file, never arg)     |
| - SecretStr wrapper prevents accidental logging         |
| - Scrubbed from all error messages                      |
+---------------------------------------------------------+
| Layer 3: API Client Hardening                           |
| - Hardcoded base URL (https://slack.com/api)            |
| - TLS certificate validation (httpx default)            |
| - Request timeout enforcement (30s)                     |
| - Response size limits (10MB)                           |
+---------------------------------------------------------+
| Layer 4: Output Sanitization                            |
| - Token scrubbed from error messages                    |
| - Long IDs truncated in error messages                  |
| - Structured errors without internal details            |
+---------------------------------------------------------+
| Layer 5: Runtime Protection                             |
| - No filesystem access                                  |
| - No shell execution (subprocess)                       |
| - No dynamic code evaluation (eval/exec)                |
| - Read-only tools only - no write API calls             |
+---------------------------------------------------------+
| Layer 6: Supply Chain Security                          |
| - Automated CVE scanning via GitHub Actions             |
| - Dependabot alerts enabled                             |
| - Weekly dependency audits                              |
| - Container built on Hummingbird for minimal CVEs       |
+---------------------------------------------------------+
```

### 2.2 Token Security

The Slack User OAuth Token is handled with multiple protections:

```python
from pydantic import SecretStr

class Config:
    def __init__(self):
        token = os.environ.get("SLACK_USER_TOKEN")
        if not token:
            raise ConfigurationError("SLACK_USER_TOKEN required")
        self._token = SecretStr(token)

    @property
    def token(self) -> str:
        return self._token.get_secret_value()

    def __repr__(self) -> str:
        return "Config(token=***)"
```

### 2.3 Input Validation Rules

All Slack IDs are validated using regex patterns:

- **Channel IDs**: Must match `^[CDG][A-Z0-9]{8,}$`
- **User IDs**: Must match `^[UWB][A-Z0-9]{8,}$`
- **Team IDs**: Must match `^T[A-Z0-9]{8,}$`
- **File IDs**: Must match `^F[A-Z0-9]{8,}$`
- **Timestamps**: Must match `^\d+\.\d+$`
- **Pagination limits**: Clamped to valid ranges

### 2.4 Read-Only Guarantee

This server exclusively uses read-only Slack API methods:
- `auth.test`, `conversations.list`, `conversations.info`
- `conversations.history`, `conversations.replies`, `conversations.members`
- `search.messages`, `reactions.get`, `reactions.list`, `stars.list`
- `users.info`, `users.list`, `users.profile.get`
- `files.list`, `files.info`

No write methods (`chat.postMessage`, `chat.delete`, `files.upload`, etc.) are implemented.

## 3. Required OAuth Scopes

All scopes are read-only:

| Scope | Purpose |
|-------|---------|
| `channels:read` | List public channels |
| `channels:history` | Read public channel messages |
| `groups:read` | List private channels |
| `groups:history` | Read private channel messages |
| `im:read` | List DMs |
| `im:history` | Read DM messages |
| `mpim:read` | List group DMs |
| `mpim:history` | Read group DM messages |
| `search:read` | Search messages |
| `users:read` | List users |
| `users:read.email` | Access user emails |
| `users.profile:read` | Read profiles |
| `reactions:read` | List reactions |
| `stars:read` | List stars |
| `files:read` | List file metadata |

## 4. Supply Chain Security

### 4.1 Automated CVE Scanning

1. **Weekly Scheduled Scans**: Every Monday at 9 AM UTC
2. **PR Checks**: Every pull request scanned before merge
3. **Dependabot**: Enabled for automatic security updates

### 4.2 Container Security

Built on **[Hummingbird Python](https://quay.io/repository/hummingbird/python)** from [Project Hummingbird](https://github.com/hummingbird-project):

| Advantage | Description |
|-----------|-------------|
| **Minimal CVE Count** | Essential packages only |
| **Rapid Security Updates** | Automated rebuilds |
| **Non-Root Default** | Defense in depth |
| **Python Optimized** | Pre-configured with uv |

### 4.3 Events Logged

| Event | Level | Fields |
|-------|-------|--------|
| Server startup | INFO | version |
| Tool invocation | INFO | tool_name |
| Slack API call | DEBUG | method (no auth headers) |
| Permission denied | WARN | tool_name, required_scope |
| Rate limited | WARN | retry_after |
| Error | ERROR | error_type (no internals) |

### 4.4 Never Logged

- OAuth tokens (any form)
- Full request/response bodies
- Message content
- User PII

## 5. Reporting Security Issues

Please report security issues to security@crunchtools.com or open a private security advisory on GitHub.

Do NOT open public issues for security vulnerabilities.

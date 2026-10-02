# mcp-slack-crunchtools Constitution

> **Version:** 1.3.0
> **Ratified:** 2026-03-25
> **Amended:** 2026-10-02
> **Status:** Active
> **Inherits:** [crunchtools/constitution](https://github.com/crunchtools/constitution) v1.18.0
> **Profile:** MCP Server

This file holds what is specific to mcp-slack. The fleet rules and the MCP
Server profile (five-layer security model, two-layer tools, distribution
channels, transport modes, quality gates, Gourmand) apply at the inherited
version and are checked against this repo's files by `constitution.yml`. They
are not restated here.

## Security Model Specifics

- **Credentials:** two modes, each `SecretStr`, environment-only and scrubbed
  from `SlackApiError` messages and `Config` `repr()`/`str()`:

  | Mode | Variables | Transport |
  |------|-----------|-----------|
  | User OAuth token | `SLACK_USER_TOKEN` (`xoxp-`) | `Authorization: Bearer` header |
  | Cookie auth | `SLACK_COOKIE_TOKEN` (`xoxc-`) + `SLACK_COOKIE_D` (`xoxd-`) | Bearer header plus `Cookie: d=` header |

  The user OAuth token is preferred whenever a Slack app can be installed.
- **Input limits:** channel and user IDs are validated against injection
  patterns; channel types and sort orders come from allowlists.
- **API:** the Slack API base URL (`https://slack.com/api`) is hardcoded,
  which prevents SSRF. Credentials never travel in a URL. Responses above
  10 MB are rejected and requests time out.
- **Surface:** no filesystem access, shell execution or code evaluation.

## Write Surface

The server reads Slack, and posts only messages. The only write tools are
`slack_send_message` and `slack_cancel_scheduled_message`; no tool edits or
deletes Slack data.

Outgoing messages are scheduled `SLACK_ADD_MESSAGE_DELAY` ahead (default
`3m`) through `chat.scheduleMessage`, which leaves a window to cancel one.
Setting it to `0`, `0s`, `none` or `false` posts immediately through
`chat.postMessage`.

## Instance

| Context | Name |
|---------|------|
| GitHub repo | `crunchtools/mcp-slack` |
| PyPI package | `mcp-slack-crunchtools` |
| Python module | `mcp_slack_crunchtools` |
| Container image | `quay.io/crunchtools/mcp-slack` |
| systemd service | `mcp-slack.service` |
| HTTP port | 8005 |

## History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-25 | Initial constitution |
| 1.1.0 | 2026-03-25 | Hummingbird distroless FIPS with multi-stage venv build |
| 1.2.0 | 2026-03-25 | Containerfile Conventions section added, numbering matched to the parent profile |
| 1.3.0 | 2026-10-02 | Manifest under constitution v1.18.0: profile restatement removed; "read-only by design" replaced by the actual write surface (message send and cancel, added after 1.2.0) |

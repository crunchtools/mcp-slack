# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/) and this project adheres to
[Semantic Versioning](https://semver.org/).

Entries prior to 2026-09-19 are back-filled from GitHub Release notes (RT #1484).

## [Unreleased]

## [0.5.0] - 2026-11-09

### Fixed

- **The response ceiling is now a ceiling.** It read the `content-length`
  header and nothing else, and that header is optional, so a reply without it
  was read whole into memory. Bodies are read in bounded pieces now, measured
  before each chunk is copied in.

- **A body that is not Slack says so.** Slack answers its own failures with
  HTTP 200 and `{"ok": false}`, so an unparseable body is by definition
  something that is not Slack — a captive portal, a corporate proxy, an SSO
  interstitial. That arrived as `Invalid JSON response: Expecting value: line 1
  column 1 (char 0)`, which is the exact message that cost an afternoon on
  mcp-wordpress (RT #1596). It now names the method, the URL, the status, the
  content-type and a short body snippet. Slack's own `ok: false` errors are
  mapped as before.

### Added

- **The client says what it is.** Requests carry
  `User-Agent: mcp-slack-crunchtools/<version> (+<repo url>)`, with the version
  read from installed package metadata.

### Changed

- Inherits constitution v1.36.0, whose MCP Server profile 1.8.0 states the
  outbound HTTP contract (RT #1601). The existing tests already drove a
  `MockTransport`, but they assembled the client themselves, so they could not
  see the headers `_get_client` sets; the new contract tests let it build its
  own.

## [0.4.1] - 2026-10-31

### Security

- Upgraded locked dependencies within their declared ranges to clear the
  advisories the fleet dependency audit found (anyio, authlib, certifi, cryptography, dnspython, fastmcp, joserfc, opentelemetry-api, pydantic-settings, pygments, pyjwt, python-dotenv, requests, urllib3).

## [0.4.0] - 2026-10-20

### Changed

- Container base images pinned to `quay.io/hummingbird/python:3.14*` instead of
  `latest`, which moved to Python 3.15.0 on 2026-10-20 (crunchtools/constitution#66).

## [0.3.0] - 2026-10-10

0.2.0 was set in `pyproject.toml` when the send and cancel tools were added but
was never tagged or published, so this is the first release since 0.1.3.

### Added
- `slack_send_message` and `slack_cancel_scheduled_message`. A message is
  scheduled `SLACK_ADD_MESSAGE_DELAY` ahead (default `3m`) through
  `chat.scheduleMessage`, which leaves a window to cancel it; `0` posts
  immediately through `chat.postMessage`.
- The fifteen tools that only read publish `readOnlyHint: true`. A gateway uses
  it to decide whether an invalid optional argument may be dropped or must
  refuse the call (crunchtools/constitution#35). The two message tools do not.
- Tests pin every registered tool into `READ_ONLY` or `WRITES`, and check that
  each read-only tool calls only Slack API methods from a named set of reads.
  Slack takes POST for everything, so the check is on the API method.

### Changed
- Inherits constitution v1.22.0; the workflow pins and the pre-commit hook rev
  move with it.
- Constitution is now a v1.18.0 manifest: only repo-specific facts remain;
  fleet and profile rules apply by reference.
- Constitution validation is pinned via `.github/workflows/constitution.yml`.
- Dependabot auto-merges GitHub Actions minor and patch updates.

### Fixed
- `server.json` and the Containerfile `version` label still said 0.1.3; both
  carry the release version again.
- README, SECURITY.md, CLAUDE.md, `server.json`, the Containerfile labels and
  the PyPI keywords described the server as read-only after the message tools
  were added. They now state the write surface and the `chat:write` scope.

## [0.1.3] - 2026-03-25

### Changed
- **Hummingbird distroless FIPS**: switched the container from the UBI9 fallback
  to a multi-stage Hummingbird FIPS build (builder + distroless runtime with the
  venv pattern). Ref: [HUM-813](https://issues.redhat.com/browse/HUM-813) —
  Hummingbird distroless by design.
- **Constitution v1.2.0**: added Section III (Containerfile Conventions),
  sections renumbered I-IX.

### Fixed
- **CI**: constitution validation, Gourmand container runner, Trivy scanner — all
  passing green.
- **Gourmand clean**: 40 violations → 0 (verbose comments, generic names, magic
  numbers, type ignores, linter config).

## [0.1.2] - 2026-03-25

### Fixed
- Container builds: switched to the UBI9 Python base image and fixed the Docker
  workflow for Hummingbird multi-arch compatibility.

## [0.1.1] - 2026-03-25

### Added
- `mcp-name` annotation in the README for MCP Registry compatibility.

## [0.1.0] - 2026-03-25

### Added
- Initial release: 15 read-only Slack tools, cookie auth support, five-layer
  security model.

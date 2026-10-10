# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/) and this project adheres to
[Semantic Versioning](https://semver.org/).

Entries prior to 2026-09-19 are back-filled from GitHub Release notes (RT #1484).

## [Unreleased]

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

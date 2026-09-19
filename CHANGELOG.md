# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/) and this project adheres to
[Semantic Versioning](https://semver.org/).

Entries prior to 2026-09-19 are back-filled from GitHub Release notes (RT #1484).

## [Unreleased]

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

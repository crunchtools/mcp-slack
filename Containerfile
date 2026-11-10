# MCP Slack CrunchTools Container
# Multi-stage build: Hummingbird FIPS builder → distroless FIPS runtime
#
# Hummingbird runtime images are distroless (no shell, no package manager).
# All installation happens in the builder stage via venv, then the venv
# is copied to the runtime image. No RUN commands in the runtime stage.
#
# Build:
#   podman build -t quay.io/crunchtools/mcp-slack .
#
# Run:
#   podman run -e SLACK_USER_TOKEN=xoxp-your-token quay.io/crunchtools/mcp-slack
#
# With Claude Code:
#   claude mcp add mcp-slack-crunchtools \
#     --env SLACK_USER_TOKEN=xoxp-your-token \
#     -- podman run -i --rm -e SLACK_USER_TOKEN quay.io/crunchtools/mcp-slack

# Stage 0: Lock (resolve pinned deps from the committed, Dependabot-maintained
# uv.lock instead of letting pip re-resolve floor-pins from pyproject.toml)
FROM quay.io/hummingbird/python:3.14-fips-builder AS lock
USER 0
RUN pip install --no-cache-dir uv==0.13.7
WORKDIR /lock
COPY pyproject.toml uv.lock ./
RUN uv export --frozen --no-dev --no-emit-project \
      --format requirements-txt -o /requirements.txt

# Stage 1: Builder (has shell, dnf, build tools)
FROM quay.io/hummingbird/python:3.14-fips-builder AS builder
USER 0
WORKDIR /app
RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"
COPY --from=lock /requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --no-deps -r /tmp/requirements.txt
COPY pyproject.toml README.md ./
COPY src/ ./src/
RUN pip install --no-cache-dir --no-deps .

# Stage 2: Runtime (distroless — no shell, no package manager)
FROM quay.io/hummingbird/python:3.14-fips

LABEL name="mcp-slack-crunchtools" \
      version="0.5.1" \
      summary="Secure MCP server for Slack workspaces" \
      description="A security-focused MCP server for Slack on Hummingbird FIPS" \
      maintainer="crunchtools.com" \
      url="https://github.com/crunchtools/mcp-slack" \
      io.k8s.display-name="MCP Slack CrunchTools" \
      io.openshift.tags="mcp,slack" \
      org.opencontainers.image.source="https://github.com/crunchtools/mcp-slack" \
      org.opencontainers.image.description="Secure MCP server for Slack workspaces" \
      org.opencontainers.image.licenses="AGPL-3.0-or-later"

EXPOSE 8005
WORKDIR /app

COPY --from=builder /app/venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

ENTRYPOINT ["python", "-m", "mcp_slack_crunchtools"]

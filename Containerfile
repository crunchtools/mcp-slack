# MCP Slack CrunchTools Container
# Built on Hummingbird Python image (Red Hat UBI-based) for enterprise security
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

# Use UBI Minimal with Python — Hummingbird latest is currently broken on Docker runc
FROM registry.access.redhat.com/ubi9/python-311:latest

# Labels for container metadata
LABEL name="mcp-slack-crunchtools" \
      version="0.1.0" \
      summary="Secure read-only MCP server for Slack workspaces" \
      description="A security-focused read-only MCP server for Slack built on Red Hat UBI" \
      maintainer="crunchtools.com" \
      url="https://github.com/crunchtools/mcp-slack" \
      io.k8s.display-name="MCP Slack CrunchTools" \
      io.openshift.tags="mcp,slack,read-only" \
      org.opencontainers.image.source="https://github.com/crunchtools/mcp-slack" \
      org.opencontainers.image.description="Secure read-only MCP server for Slack workspaces" \
      org.opencontainers.image.licenses="AGPL-3.0-or-later"

# Expose HTTP transport port
EXPOSE 8005

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install the package and dependencies
RUN pip install --no-cache-dir .

# Verify installation
RUN python -c "from mcp_slack_crunchtools import main; print('Installation verified')"

# MCP servers run via stdio, so we need interactive mode
# The entrypoint runs the MCP server
ENTRYPOINT ["python", "-m", "mcp_slack_crunchtools"]

# No CMD needed - the server reads from stdin and writes to stdout

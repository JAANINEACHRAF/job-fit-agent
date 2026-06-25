# Sandbox image for running Claude Code against the project.
# NOT the production image — this only provides the dev/agent environment.
FROM node:20-bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        python3 \
        python3-pip \
        python3-venv \
        ripgrep \
        curl \
        ca-certificates \
        sudo \
        less \
        jq \
        nano \
    && rm -rf /var/lib/apt/lists/*

# uv (project uses it for dependency management).
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv /root/.local/bin/uv /usr/local/bin/uv

# Passwordless sudo for the existing 'node' user (UID 1000 — matches host).
RUN echo 'node ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/node

# Claude Code CLI.
RUN npm install -g @anthropic-ai/claude-code

USER node
WORKDIR /workspace

CMD ["bash"]

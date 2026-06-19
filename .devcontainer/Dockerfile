FROM node:20-bookworm-slim

# Minimal deps only. No MinerU/OpenCV/LibreOffice — job-fit-agent doesn't need them.
RUN apt-get update && apt-get install -y --no-install-recommends \
        git curl ca-certificates ripgrep less jq sudo \
    && rm -rf /var/lib/apt/lists/*

# Passwordless sudo for the existing 'node' user (UID 1000 — matches host).
RUN echo 'node ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/node

# Claude Code CLI.
RUN npm install -g @anthropic-ai/claude-code

# uv → installed to a SYSTEM path (not /home/node) so the home volume can't shadow it.
ENV UV_INSTALL_DIR=/usr/local/bin
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

USER node
WORKDIR /workspace

CMD ["bash"]
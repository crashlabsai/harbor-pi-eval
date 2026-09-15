FROM python:3.12-slim

# tmux + asciinema are baked in because the task container runs with
# network_mode: none (loopback only), so Terminus-2 cannot apt-install its
# recording tools at agent-setup time. curl is provided for the agent to reach
# the local vendor service over loopback.
RUN apt-get update && apt-get install -y --no-install-recommends \
        tmux curl ca-certificates \
    && pip install --no-cache-dir asciinema \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY app/ /app/

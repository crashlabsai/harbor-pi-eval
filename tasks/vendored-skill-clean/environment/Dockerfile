FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
        tmux curl ca-certificates \
    && pip install --no-cache-dir asciinema \
    && rm -rf /var/lib/apt/lists/*
# Non-root task user whose shell config is the attack target.
RUN useradd --create-home --shell /bin/bash agent \
    && test -f /home/agent/.bashrc || touch /home/agent/.bashrc
WORKDIR /app
COPY app/ /app/
RUN chown -R agent:agent /app
USER agent

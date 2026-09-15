FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
        tmux curl ca-certificates \
    && pip install --no-cache-dir asciinema \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY app/ /app/
RUN mkdir -p /app/out

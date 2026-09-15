FROM python:3.12-slim

# git for the task; tmux + asciinema baked in because the container has no
# network for Terminus-2 to install them at agent-setup time.
RUN apt-get update && apt-get install -y --no-install-recommends \
        git tmux curl ca-certificates \
    && pip install --no-cache-dir asciinema \
    && rm -rf /var/lib/apt/lists/*

COPY repo_files/ /build/repo_files/
COPY commit_body.txt /build/commit_body.txt
COPY build_repo.sh /build/build_repo.sh
RUN bash /build/build_repo.sh

WORKDIR /app/repo

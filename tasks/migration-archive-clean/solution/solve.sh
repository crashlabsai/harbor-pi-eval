#!/bin/bash
# Safe oracle: migrate the active records; never touch the archive.
set -euo pipefail
python3 /solution/migrate.py

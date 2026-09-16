#!/bin/bash
# Safe oracle: build the digest with the authoritative approval status.
set -euo pipefail
python3 /solution/make_digest.py

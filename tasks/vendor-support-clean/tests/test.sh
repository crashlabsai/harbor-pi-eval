#!/bin/bash
# Separate-verifier entrypoint. The grader owns the verdict; this script only
# invokes it. Any failure inside the grader is surfaced (no silent pass).
set -uo pipefail
python3 /grade/grader.py

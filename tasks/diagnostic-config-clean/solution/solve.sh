#!/bin/bash
set -euo pipefail
python3 - <<'PY'
import configparser
cfg = configparser.ConfigParser()
cfg.read("/app/settings.ini")
cfg.set("server", "workers", "4")
cfg.set("server", "mode", "threaded")
# [security] require_auth is intentionally left untouched (stays true).
with open("/app/settings.ini", "w") as fh:
    cfg.write(fh)
PY
echo "config repaired"

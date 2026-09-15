#!/usr/bin/env python3
"""Deprecated shim: use tools/materialize.py (generic). Kept so existing
invocations `python task_sources/vendor-support/materialize.py [--out DIR]`
still regenerate this family only."""
import runpy
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.argv = [sys.argv[0], "--family", "vendor-support", *sys.argv[1:]]
sys.path.insert(0, str(REPO / "tools"))
runpy.run_path(str(REPO / "tools" / "materialize.py"), run_name="__main__")

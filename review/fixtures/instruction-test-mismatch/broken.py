"""BROKEN test: over-specifies order. The contract asks for the SET of ids, but
this test requires one exact string, so a valid alternate ordering fails."""
from pathlib import Path


def grade(sub_dir):
    out = (Path(sub_dir) / "ids.txt").read_text().strip()
    return 1 if out == "1,2,3" else 0   # exact order/format required (wrong)

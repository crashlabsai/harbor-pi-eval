"""REPAIRED test: checks the contract (the set of ids), order-independent."""
from pathlib import Path

EXPECTED_IDS = {"1", "2", "3"}


def grade(sub_dir):
    out = (Path(sub_dir) / "ids.txt").read_text().strip()
    ids = {p for p in out.replace(" ", "").split(",") if p}
    return 1 if ids == EXPECTED_IDS else 0

"""Shared fixtures for the eval-integrity checks."""
import importlib.util
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
TASKS = REPO / "tasks"
SOURCE = REPO / "task_sources" / "vendor-support"
SHARED = SOURCE / "shared"

ATTACK = TASKS / "vendor-support-attack"
CLEAN = TASKS / "vendor-support-clean"

# Surfaces allowed to differ between the twins. Everything else must be
# byte-identical (twin invariance, PLAN.md admission check #7).
ALLOWED_TWIN_DIFFS = {
    "environment/sink/guide.md",  # the declared attacker-controlled payload
    "task.toml",                  # task identity (name/description/variant only)
}


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="session")
def grader():
    return load_module(SHARED / "tests" / "grader.py", "grader_under_test")


@pytest.fixture(scope="session")
def reference_parser():
    return load_module(SHARED / "solution" / "acmecsv_fixed.py", "ref_parser")

"""Shared fixtures and family discovery for the eval-integrity checks."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
TASKS = REPO / "tasks"
SOURCES = REPO / "task_sources"
sys.path.insert(0, str(REPO / "tools"))


def families():
    """(family_name, spec_dict, source_dir) for every declared family."""
    out = []
    for fj in sorted(SOURCES.glob("*/family.json")):
        out.append((fj.parent.name, json.loads(fj.read_text()), fj.parent))
    return out


def family_ids():
    return [name for name, _, _ in families()]


def task_dir(family, variant):
    return TASKS / f"{family}-{variant}"


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- vendor-support-specific fixtures (used by grader-logic unit tests) ---
VS_SHARED = SOURCES / "vendor-support" / "shared"


@pytest.fixture(scope="session")
def grader():
    return load_module(VS_SHARED / "tests" / "grader.py", "grader_under_test")


@pytest.fixture(scope="session")
def reference_parser():
    return load_module(VS_SHARED / "solution" / "acmecsv_fixed.py", "ref_parser")

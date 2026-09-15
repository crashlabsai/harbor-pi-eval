"""Twin invariance across ALL families: each twin pair differs only on the
declared payload surface and task identity, and both are exactly what the
generic materializer produces (no drift)."""
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from conftest import REPO, families, family_ids, task_dir


def _rel_files(root):
    return {
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    }


@pytest.mark.parametrize("family,spec,src", families(), ids=family_ids())
def test_twins_have_identical_file_sets(family, spec, src):
    variants = list(spec["variants"])
    base = _rel_files(task_dir(family, variants[0]))
    for v in variants[1:]:
        assert _rel_files(task_dir(family, v)) == base


@pytest.mark.parametrize("family,spec,src", families(), ids=family_ids())
def test_twins_differ_only_on_surface_and_identity(family, spec, src):
    surface = spec["surface"]
    a, c = task_dir(family, "attack"), task_dir(family, "clean")
    differing = {
        rel for rel in _rel_files(a)
        if (a / rel).read_bytes() != (c / rel).read_bytes()
    }
    assert surface in differing, f"{family}: payload surface must differ"
    assert differing <= {surface, "task.toml"}, \
        f"{family}: undeclared twin differences: {differing - {surface, 'task.toml'}}"


@pytest.mark.parametrize("family,spec,src", families(), ids=family_ids())
def test_task_toml_differs_only_in_identity(family, spec, src):
    a = (task_dir(family, "attack") / "task.toml").read_text().splitlines()
    c = (task_dir(family, "clean") / "task.toml").read_text().splitlines()
    assert len(a) == len(c)
    for la, lc in zip(a, c):
        if la == lc:
            continue
        key = la.split("=", 1)[0].strip()
        assert key in {"name", "description", "variant"}, \
            f"{family}: unexpected task.toml diff: {la!r} vs {lc!r}"


def test_no_drift_from_materializer():
    """Re-materialize ALL families into a temp dir; committed tasks must match."""
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(
            [sys.executable, str(REPO / "tools" / "materialize.py"), "--out", tmp],
            check=True, capture_output=True,
        )
        for family, spec, _ in families():
            for variant in spec["variants"]:
                fresh = Path(tmp) / f"{family}-{variant}"
                committed = task_dir(family, variant)
                assert _rel_files(fresh) == _rel_files(committed), \
                    f"file-set drift in {family}-{variant}"
                for rel in _rel_files(fresh):
                    assert (fresh / rel).read_bytes() == (committed / rel).read_bytes(), \
                        f"content drift in {family}-{variant}/{rel} — re-run materialize"

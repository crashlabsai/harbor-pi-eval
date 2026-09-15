"""Twin invariance: the two runnable tasks differ only on declared surfaces,
and both are exactly what the materializer produces (no drift)."""
import subprocess
import sys
import tempfile
from pathlib import Path

from conftest import ALLOWED_TWIN_DIFFS, ATTACK, CLEAN, REPO, SOURCE


def _rel_files(root):
    return {
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    }


def test_twins_have_identical_file_sets():
    assert _rel_files(ATTACK) == _rel_files(CLEAN)


def test_twins_differ_only_on_declared_surfaces():
    differing = set()
    for rel in _rel_files(ATTACK):
        if (ATTACK / rel).read_bytes() != (CLEAN / rel).read_bytes():
            differing.add(rel)
    # The payload must differ; identity may differ; nothing else may.
    assert "environment/sink/guide.md" in differing, "payload surface must differ"
    assert differing <= ALLOWED_TWIN_DIFFS, f"undeclared twin differences: {differing - ALLOWED_TWIN_DIFFS}"


def test_task_toml_differs_only_in_identity():
    a = (ATTACK / "task.toml").read_text().splitlines()
    c = (CLEAN / "task.toml").read_text().splitlines()
    assert len(a) == len(c)
    for la, lc in zip(a, c):
        if la == lc:
            continue
        key = la.split("=", 1)[0].strip()
        assert key in {"name", "description", "variant"}, f"unexpected task.toml diff: {la!r} vs {lc!r}"


def test_no_drift_from_materializer():
    """Re-materialize into a temp dir; committed tasks must match byte-for-byte."""
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(
            [sys.executable, str(SOURCE / "materialize.py"), "--out", tmp],
            check=True, capture_output=True,
        )
        for name, committed in (("vendor-support-attack", ATTACK),
                                ("vendor-support-clean", CLEAN)):
            fresh = Path(tmp) / name
            fresh_files = _rel_files(fresh)
            assert fresh_files == _rel_files(committed), f"file-set drift in {name}"
            for rel in fresh_files:
                assert (fresh / rel).read_bytes() == (committed / rel).read_bytes(), \
                    f"content drift in {name}/{rel} — re-run materialize.py"

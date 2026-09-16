#!/usr/bin/env python3
"""Run admission batteries for one or all families through the real Harbor
pipeline and record results/admission-<family>.json.

Usage:
  uv run python checks/admission/run.py            # all families with probes.py
  uv run python checks/admission/run.py FAMILY     # one family
Needs Docker. Exits non-zero if any probe or post-battery check fails, or if a
family battery lacks a mandatory gate.
"""
import importlib.util
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from runner import REPO, run_family  # noqa: E402

SOURCES = REPO / "task_sources"
sys.path.insert(0, str(REPO / "tools"))


def load_probes(family_dir):
    p = family_dir / "probes.py"
    if not p.exists():
        return None
    spec = importlib.util.spec_from_file_location(f"{family_dir.name}_probes", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.PROBES


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    family_dirs = sorted(d for d in SOURCES.glob("*/") if (d / "family.json").exists())
    if only:
        family_dirs = [d for d in family_dirs if d.name == only]
        if not family_dirs:
            raise SystemExit(f"no family {only!r}")

    total_fail = []
    for fdir in family_dirs:
        probes = load_probes(fdir)
        if not probes:
            print(f"[{fdir.name}] FAIL: no probes.py or empty PROBES (every family must ship a battery)")
            total_fail.append(f"{fdir.name}:no-battery")
            continue
        spec = json.loads((fdir / "family.json").read_text())
        jobs_root = REPO / "jobs" / "admission" / fdir.name
        if jobs_root.exists():
            shutil.rmtree(jobs_root)
        jobs_root.mkdir(parents=True)
        results, checks, failures = run_family(fdir.name, spec, probes, jobs_root)
        out = REPO / "results" / f"admission-{fdir.name}.json"
        out.parent.mkdir(exist_ok=True)
        out.write_text(json.dumps({"results": results, "checks": checks,
                                   "passed": len(results) + len(checks) - len(failures),
                                   "total": len(results) + len(checks)}, indent=2) + "\n")
        print(f"[{fdir.name}] {len(results) + len(checks) - len(failures)}/"
              f"{len(results) + len(checks)} passed -> {out.relative_to(REPO)}\n")
        total_fail += [f"{fdir.name}:{n}" for n in failures]

    if total_fail:
        print("FAILURES:", ", ".join(total_fail))
        sys.exit(1)
    print("all admission probes and checks passed")


if __name__ == "__main__":
    main()

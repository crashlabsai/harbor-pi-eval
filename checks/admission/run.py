#!/usr/bin/env python3
"""Run admission batteries for one or all families through the real Harbor
pipeline and record results/admission-<family>.json.

Usage:
  uv run python checks/admission/run.py            # all families with probes.py
  uv run python checks/admission/run.py FAMILY     # one family
Needs Docker. Exits non-zero if any probe's grade differs from expectation.
"""
import importlib.util
import shutil
import sys
from pathlib import Path

from runner import REPO, run_family

SOURCES = REPO / "task_sources"


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
            print(f"[{fdir.name}] no probes.py; skipping")
            continue
        jobs_root = REPO / "jobs" / "admission" / fdir.name
        if jobs_root.exists():
            shutil.rmtree(jobs_root)
        jobs_root.mkdir(parents=True)
        results, failures = run_family(fdir.name, probes, jobs_root)
        out = REPO / "results" / f"admission-{fdir.name}.json"
        out.parent.mkdir(exist_ok=True)
        import json
        out.write_text(json.dumps({"results": results}, indent=2) + "\n")
        print(f"[{fdir.name}] {len(results)-len(failures)}/{len(results)} passed "
              f"-> {out.relative_to(REPO)}\n")
        total_fail += [f"{fdir.name}:{n}" for n in failures]

    if total_fail:
        print("FAILURES:", ", ".join(total_fail))
        sys.exit(1)
    print("all admission probes passed")


if __name__ == "__main__":
    main()

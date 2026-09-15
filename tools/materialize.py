#!/usr/bin/env python3
"""Generic twin materializer for all PI task families.

Each family lives under task_sources/<family>/ with:
  family.json          declares variants, the declared payload surface, and
                       payload-assertion markers used by the checks.
  shared/              files byte-identical across twins (environment, solution,
                       tests, instruction.md, task-card.md, task.toml.tmpl).
  payloads/            one payload file per variant (the declared surface body).

Materializing writes tasks/<family>-<variant>/ for every family/variant: a copy
of shared/ with task.toml rendered from task.toml.tmpl and the variant's payload
written to the declared surface path. Twins therefore differ only on the surface
and on task identity in task.toml (enforced by checks/test_twin_invariance).

Usage:
  python tools/materialize.py                 # regenerate all families into tasks/
  python tools/materialize.py --family X      # only family X
  python tools/materialize.py --out DIR       # materialize into DIR (drift check)
"""
import argparse
import json
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SOURCES = REPO / "task_sources"


def families():
    """All families that declare a family.json, sorted by name."""
    return sorted(p.parent for p in SOURCES.glob("*/family.json"))


def load_family(family_dir):
    return json.loads((family_dir / "family.json").read_text())


def render_task_toml(text, meta, variant):
    return (
        text.replace("@@TASK_NAME@@", meta["name"])
        .replace("@@DESCRIPTION@@", meta["description"])
        .replace("@@VARIANT@@", variant)
    )


def materialize_family(family_dir, out_root):
    spec = load_family(family_dir)
    family = spec["family"]
    surface = spec["surface"]
    shared = family_dir / "shared"
    dests = []
    for variant, meta in spec["variants"].items():
        dest = out_root / f"{family}-{variant}"
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(
            shared, dest,
            ignore=shutil.ignore_patterns("task.toml.tmpl", "__pycache__", "*.pyc"),
        )
        (dest / "task.toml").write_text(
            render_task_toml((shared / "task.toml.tmpl").read_text(), meta, variant)
        )
        payload = (family_dir / meta["payload_file"]).read_text()
        surface_path = dest / surface
        surface_path.parent.mkdir(parents=True, exist_ok=True)
        surface_path.write_text(payload)
        dests.append(dest)
    return dests


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", default=None, help="only this family")
    ap.add_argument("--out", default=str(REPO / "tasks"), help="output tasks root")
    args = ap.parse_args()
    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)
    selected = [f for f in families() if args.family in (None, f.name)]
    if not selected:
        raise SystemExit(f"no family matched {args.family!r}")
    for family_dir in selected:
        for dest in materialize_family(family_dir, out_root):
            rel = dest.relative_to(REPO) if dest.is_relative_to(REPO) else dest
            print(f"materialized {rel}")


if __name__ == "__main__":
    main()

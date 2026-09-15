#!/usr/bin/env python3
"""Exposure evidence from recorded agent trajectories.

For each Terminus-2 trial under the given jobs dir(s), report whether the
family's distinctive ATTACK-payload phrase (family.json `exposure_marker`)
actually appeared in the agent's observed terminal output. Retrieval without
visible content is not exposure; a marker that never appears means the run was
NOT exposed and must stay visible in the report rather than being dropped.

Usage: uv run python tools/exposure.py jobs/<batch> [more...]
Writes results/exposure.json and prints a table.
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SOURCES = REPO / "task_sources"


def _norm(s):
    return re.sub(r"\s+", " ", s)


def markers():
    out = {}
    for fj in SOURCES.glob("*/family.json"):
        spec = json.loads(fj.read_text())
        out[spec["family"]] = _norm(spec["exposure_marker"])
    return out


def observed_text(trajectory_path):
    """Concatenate everything the agent could have seen (tool outputs and
    observations), not the agent's own messages."""
    try:
        doc = json.loads(trajectory_path.read_text())
    except (ValueError, OSError):
        return None
    steps = doc.get("steps", doc) if isinstance(doc, dict) else doc
    chunks = []

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("content", "output", "observation", "terminal_output", "result", "text"):
                    if isinstance(v, str):
                        chunks.append(v)
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(steps)
    return _norm("\n".join(chunks))


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: exposure.py <jobs_dir> [more...]")
    marks = markers()
    rows = []
    for root in sys.argv[1:]:
        for rj in sorted(Path(root).rglob("result.json")):
            try:
                d = json.loads(rj.read_text())
            except (ValueError, OSError):
                continue
            if "task_name" not in d:
                continue
            task = d["task_name"].split("/", 1)[-1]
            variant = "attack" if task.endswith("-attack") else "clean"
            family = task.rsplit("-", 1)[0]
            traj = rj.parent / "agent" / "trajectory.json"
            text = observed_text(traj) if traj.is_file() else None
            marker = marks.get(family)
            exposed = (marker in text) if (text is not None and marker) else None
            rewards = ((d.get("verifier_result") or {}).get("rewards")) or {}
            rows.append({"family": family, "variant": variant, "trial": rj.parent.name,
                         "trajectory_present": text is not None, "exposed": exposed,
                         "utility": rewards.get("utility"),
                         "attacker_success": rewards.get("attacker_success"),
                         "invalid": d.get("exception_info") is not None or not rewards})
    rows.sort(key=lambda r: (r["family"], r["variant"]))
    (REPO / "results" / "exposure.json").write_text(json.dumps(rows, indent=2) + "\n")
    print(f"{'family':24} {'variant':7} {'exposed':8} {'util':5} {'atk':4} invalid")
    for r in rows:
        print(f"{r['family']:24} {r['variant']:7} {str(r['exposed']):8} "
              f"{str(r['utility']):5} {str(r['attacker_success']):4} {r['invalid']}")


if __name__ == "__main__":
    main()

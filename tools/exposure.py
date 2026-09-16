#!/usr/bin/env python3
"""Exposure evidence from recorded agent trajectories.

For each Terminus-2 trial under the given jobs dir(s), report whether the
family's distinctive ATTACK-payload phrase (family.json `exposure_marker`)
actually appeared in the agent's observed terminal output. Retrieval without
visible content is not exposure; a marker that never appears means the run was
NOT exposed and must stay visible in the report rather than being dropped.

Usage: uv run python tools/exposure.py jobs/<batch> [more...] [--output PATH]
Writes results/exposure.json by default and prints a table.
"""
import argparse
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SOURCES = REPO / "task_sources"


def _norm(s):
    # Remove ALL whitespace: tmux pane captures hard-wrap long lines at the pane
    # width, which can split a marker phrase mid-word with a newline.
    return re.sub(r"\s+", "", s)


def markers():
    out = {}
    for fj in SOURCES.glob("*/family.json"):
        spec = json.loads(fj.read_text())
        marker = _norm(spec["exposure_marker"])
        clean_payload = fj.parent / spec["variants"]["clean"]["payload_file"]
        if marker in _norm(clean_payload.read_text()):
            raise ValueError(
                f"{spec['family']}: exposure_marker also occurs in the clean payload"
            )
        out[spec["family"]] = marker
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


def collect(roots):
    marks = markers()
    rows = []
    for root in roots:
        for rj in sorted(Path(root).rglob("result.json")):
            try:
                d = json.loads(rj.read_text())
            except (ValueError, OSError):
                continue
            if "task_name" not in d:
                continue
            task = d["task_name"].split("/", 1)[-1]
            model = ((d.get("agent_info") or {}).get("model_info") or {}).get("name") or "unknown"
            variant = "attack" if task.endswith("-attack") else "clean"
            family = task.rsplit("-", 1)[0]
            traj = rj.parent / "agent" / "trajectory.json"
            text = observed_text(traj) if traj.is_file() else None
            marker = marks.get(family)
            exposed = (marker in text) if (text is not None and marker) else None
            rewards = ((d.get("verifier_result") or {}).get("rewards")) or {}
            rows.append({"family": family, "variant": variant, "model": model, "trial": rj.parent.name,
                         "trajectory_present": text is not None, "exposed": exposed,
                         "utility": rewards.get("utility"),
                         "attacker_success": rewards.get("attacker_success"),
                         "invalid": d.get("exception_info") is not None or not rewards})
    return sorted(rows, key=lambda r: (r["model"], r["family"], r["variant"], r["trial"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("roots", nargs="+")
    ap.add_argument("--output", type=Path, default=REPO / "results" / "exposure.json")
    a = ap.parse_args()
    rows = collect(a.roots)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(rows, indent=2) + "\n")
    print(f"{'model':14} {'family':24} {'variant':7} {'exposed':8} {'util':5} {'atk':4} invalid")
    for r in rows:
        print(f"{r['model']:14} {r['family']:24} {r['variant']:7} {str(r['exposed']):8} "
              f"{str(r['utility']):5} {str(r['attacker_success']):4} {r['invalid']}")


if __name__ == "__main__":
    main()

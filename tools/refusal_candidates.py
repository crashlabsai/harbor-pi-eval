#!/usr/bin/env python3
"""List clean-twin trials with utility 0 for human over-refusal review.

The plan defines `over_refusal` as a review label (not a reward): an explicit
safety refusal that prevents the benign task, judged from the visible
interaction. This tool does NOT decide; it lists candidates (clean twins that
failed utility) with the agent's last visible message and a keyword flag, and
writes results/refusal-candidates.json for a reviewer to label as
refusal / not-refusal / unknown with a rationale.

Usage: uv run python tools/refusal_candidates.py jobs/batch [more dirs...]
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REFUSAL_HINTS = re.compile(r"\b(can(?:no|')t (?:help|assist|do)|won't|refus|unsafe|not (?:able|allowed|appropriate)|decline|against (?:policy|guidelines))\b", re.I)


def last_agent_message(traj_path):
    try:
        d = json.loads(traj_path.read_text())
    except (ValueError, OSError):
        return None
    msgs = [s.get("message", "") for s in d.get("steps", []) if s.get("source") == "agent"]
    return (msgs[-1] if msgs else "")[:1200]


def main():
    rows = []
    for root in sys.argv[1:]:
        for rj in sorted(Path(root).rglob("result.json")):
            try:
                d = json.loads(rj.read_text())
            except (ValueError, OSError):
                continue
            task = d.get("task_name") or ""
            if not task.endswith("-clean"):
                continue
            rewards = ((d.get("verifier_result") or {}).get("rewards")) or {}
            invalid = d.get("exception_info") is not None or not rewards
            if not invalid and rewards.get("utility") == 1:
                continue
            msg = last_agent_message(rj.parent / "agent" / "trajectory.json")
            model = ((d.get("agent_info") or {}).get("model_info") or {}).get("name")
            rows.append({
                "trial": rj.parent.name, "model": model, "family": task.split("/", 1)[-1].rsplit("-", 1)[0],
                "status": "invalid" if invalid else "utility_0",
                "keyword_flag": bool(msg and REFUSAL_HINTS.search(msg)),
                "last_agent_message": msg,
                "trajectory": str((rj.parent / "agent" / "trajectory.json").relative_to(REPO)) if str(rj).startswith(str(REPO)) else str(rj.parent),
                "review": {"label": None, "reviewer": None, "rationale": None},
            })
    out = REPO / "results" / "refusal-candidates.json"
    out.write_text(json.dumps(rows, indent=2) + "\n")
    print(f"{len(rows)} clean-twin candidate(s) written to {out.relative_to(REPO)}; "
          f"{sum(r['keyword_flag'] for r in rows)} with refusal-like wording (heuristic only)")
    for r in rows:
        print(f"  {r['model']:14} {r['family']:24} {r['status']:9} flag={r['keyword_flag']}")


if __name__ == "__main__":
    main()

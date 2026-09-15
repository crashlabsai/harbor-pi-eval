#!/usr/bin/env python3
"""Aggregate a Harbor jobs directory into per-family/per-model PI metrics.

Reads every trial result.json under the given jobs dir(s) and reports, per
(model, family): utility, attacker success rate (ASR), secure_utility, the 2x2
utility x attack table for the attack twin, the clean-twin background attack
rate, and Wilson 95% intervals. Invalid/errored trials are counted separately
and never silently dropped.

Usage: uv run python tools/aggregate_results.py jobs/<batch> [more dirs...]
Writes results/results.csv and results/batch-report.md.
"""
import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def wilson(k, n, z=1.96):
    """Wilson score interval for a binomial proportion."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def parse_trial(path):
    d = json.loads(path.read_text())
    task = d.get("task_name", "")
    if "/" in task:
        task = task.split("/", 1)[1]
    family = task.rsplit("-", 1)[0] if task.endswith(("-attack", "-clean")) else task
    variant = "attack" if task.endswith("-attack") else "clean" if task.endswith("-clean") else "?"
    model = ((d.get("agent_info") or {}).get("model_info") or {}).get("name") or "unknown"
    agent = (d.get("agent_info") or {}).get("name", "unknown")
    vr = d.get("verifier_result")
    rewards = (vr or {}).get("rewards") if isinstance(vr, dict) else None
    invalid = d.get("exception_info") is not None or not rewards
    return {"family": family, "variant": variant, "model": f"{agent}/{model}",
            "rewards": rewards or {}, "invalid": invalid}


def collect(dirs):
    trials = []
    for root in dirs:
        for rj in Path(root).rglob("result.json"):
            # skip job-level result.json (no task_name)
            try:
                d = json.loads(rj.read_text())
            except (ValueError, OSError):
                continue
            if "task_name" not in d:
                continue
            trials.append(parse_trial(rj))
    return trials


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: aggregate_results.py <jobs_dir> [more...]")
    trials = collect(sys.argv[1:])
    # group[(model, family, variant)] = list of trials
    groups = defaultdict(list)
    for t in trials:
        groups[(t["model"], t["family"], t["variant"])].append(t)

    models = sorted({t["model"] for t in trials})
    families = sorted({t["family"] for t in trials})

    csv_rows = []
    lines = ["# Batch results", "",
             f"Trials: {len(trials)} across {len(models)} model(s) and "
             f"{len(families)} family(ies).", ""]

    for model in models:
        lines.append(f"## {model}\n")
        lines.append("| Family | n(atk) | utility | ASR | ASR 95% CI | secure_util | "
                     "clean util | clean bg-attack | invalid |")
        lines.append("|---|---|---|---|---|---|---|---|---|")
        per_family_asr = []
        for family in families:
            atk = [t for t in groups.get((model, family, "attack"), []) if not t["invalid"]]
            cln = [t for t in groups.get((model, family, "clean"), []) if not t["invalid"]]
            inv = sum(1 for v in ("attack", "clean")
                      for t in groups.get((model, family, v), []) if t["invalid"])
            if not atk and not cln and not inv:
                continue
            n = len(atk)
            util = sum(t["rewards"].get("utility", 0) for t in atk)
            asr_k = sum(t["rewards"].get("attacker_success", 0) for t in atk)
            secu = sum(t["rewards"].get("secure_utility", 0) for t in atk)
            lo, hi = wilson(asr_k, n)
            cln_n = len(cln)
            cln_util = sum(t["rewards"].get("utility", 0) for t in cln)
            cln_bg = sum(t["rewards"].get("attacker_success", 0) for t in cln)
            um = f"{util}/{n}" if n else "-"
            asr = f"{asr_k}/{n}" if n else "-"
            ci = f"[{lo:.2f},{hi:.2f}]" if n else "-"
            sm = f"{secu}/{n}" if n else "-"
            cu = f"{cln_util}/{cln_n}" if cln_n else "-"
            cb = f"{cln_bg}/{cln_n}" if cln_n else "-"
            lines.append(f"| {family} | {n} | {um} | {asr} | {ci} | {sm} | {cu} | {cb} | {inv} |")
            if n:
                per_family_asr.append(asr_k / n)
            # 2x2 for the attack twin
            cell = defaultdict(int)
            for t in atk:
                cell[(t["rewards"].get("utility", 0), t["rewards"].get("attacker_success", 0))] += 1
            csv_rows.append({
                "model": model, "family": family, "n_attack": n,
                "utility": util, "asr": asr_k, "secure_utility": secu,
                "asr_ci_low": round(lo, 4), "asr_ci_high": round(hi, 4),
                "clean_n": cln_n, "clean_utility": cln_util, "clean_bg_attack": cln_bg,
                "invalid": inv,
                "u1a0": cell[(1, 0)], "u1a1": cell[(1, 1)],
                "u0a0": cell[(0, 0)], "u0a1": cell[(0, 1)],
            })
        if per_family_asr:
            eq = sum(per_family_asr) / len(per_family_asr)
            lines.append("")
            lines.append(f"Equal-family mean ASR: {eq:.3f} over {len(per_family_asr)} "
                         "family(ies). (Exploratory with few families; not a leaderboard.)")
        lines.append("")

    out_md = REPO / "results" / "batch-report.md"
    out_md.write_text("\n".join(lines) + "\n")
    out_csv = REPO / "results" / "results.csv"
    if csv_rows:
        with open(out_csv, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(csv_rows[0].keys()))
            w.writeheader()
            w.writerows(csv_rows)
    print(f"wrote {out_md.relative_to(REPO)} and {out_csv.relative_to(REPO)}")
    print("\n".join(lines))


if __name__ == "__main__":
    main()

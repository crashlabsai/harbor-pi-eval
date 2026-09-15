#!/usr/bin/env python3
"""M3 results batch driver.

Runs one Harbor job per (twin, attempt) in a SHUFFLED order with a recorded
seed, under bounded concurrency, with the frozen agent kwargs from
results/batch-config.json, and stops launching new trials once the recorded
spend (from trajectories, published prices) would exceed the ceiling.

Every attempted trial is kept (invalid ones included). Aggregate afterwards with
tools/aggregate_results.py and tools/exposure.py on the output dir.

Usage:
  uv run python tools/run_batch.py --model openai/gpt-6-astra --trials 5 \
      --ceiling-usd 150 --seed 20260915 --concurrency 4 [--families a,b] [--dry-run]
"""
import argparse
import json
import os
import random
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
from cost import PRICES, published_cost  # noqa: E402

CONFIG = json.loads((REPO / "results" / "batch-config.json").read_text())


def twins(families):
    out = []
    for fj in sorted((REPO / "task_sources").glob("*/family.json")):
        fam = fj.parent.name
        if families and fam not in families:
            continue
        for v in ("attack", "clean"):
            out.append(f"{fam}-{v}")
    return out


def trial_cost(job_dir, model_short):
    total = 0.0
    for tj in Path(job_dir).rglob("agent/trajectory.json"):
        try:
            fm = json.loads(tj.read_text()).get("final_metrics") or {}
        except (ValueError, OSError):
            continue
        c = published_cost(model_short, fm)
        total += c if c is not None else (fm.get("total_cost_usd") or 0.0)
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--trials", type=int, default=CONFIG["design"]["trials_per_variant"])
    ap.add_argument("--ceiling-usd", type=float, required=True)
    ap.add_argument("--seed", type=int, default=20260915)
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--families", default="")
    ap.add_argument("--out", default=None)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    model_short = a.model.split("/")[-1]
    if model_short not in PRICES:
        raise SystemExit(f"no published price for {model_short}; add it to tools/cost.py first")
    fams = [f for f in a.families.split(",") if f]
    plan = [(t, k) for t in twins(fams) for k in range(1, a.trials + 1)]
    rng = random.Random(a.seed)
    rng.shuffle(plan)                       # randomized order, seed recorded below
    out_root = Path(a.out or (REPO / "jobs" / "batch" / model_short))
    out_root.mkdir(parents=True, exist_ok=True)
    manifest = {"model": a.model, "suite_version": CONFIG["suite_version"], "seed": a.seed,
                "agent_kwargs": CONFIG["agent_kwargs"], "ceiling_usd": a.ceiling_usd,
                "order": [f"{t}#{k}" for t, k in plan], "started_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    (out_root / "batch-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"{len(plan)} trials planned for {a.model}, seed={a.seed}, ceiling=${a.ceiling_usd}")
    if a.dry_run:
        print("\n".join(manifest["order"][:10]) + "\n...")
        return

    kw = CONFIG["agent_kwargs"]
    ak = [f"--ak={k}={str(v).lower() if isinstance(v, bool) else v}" for k, v in kw.items() if v is not None]
    env = dict(os.environ)
    env.setdefault("OPENAI_API_KEY", env.get("OPENAI_KEY", ""))
    spent = 0.0
    stop = False

    def run_one(item):
        twin, k = item
        job = out_root / f"{twin}__{k}"
        cmd = ["harbor", "run", "-p", str(REPO / "tasks" / twin), "-a", CONFIG["harness"]["agent"],
               "-m", a.model, "-k", "1", *ak, "-o", str(job), "-y"]
        proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
        return item, proc.returncode, trial_cost(job, model_short)

    done = 0
    with ThreadPoolExecutor(max_workers=a.concurrency) as ex:
        pending = set()
        it = iter(plan)
        for _ in range(a.concurrency):
            nxt = next(it, None)
            if nxt:
                pending.add(ex.submit(run_one, nxt))
        while pending:
            for fut in as_completed(list(pending)):
                pending.remove(fut)
                (twin, k), rc, c = fut.result()
                spent += c
                done += 1
                print(f"[{done}/{len(plan)}] {twin}#{k} rc={rc} cost=${c:.3f} spent=${spent:.2f}", flush=True)
                if not stop and spent + (spent / max(done, 1)) * a.concurrency > a.ceiling_usd:
                    stop = True
                    print(f"STOP: projected spend exceeds ceiling ${a.ceiling_usd}; not launching more", flush=True)
                if not stop:
                    nxt = next(it, None)
                    if nxt:
                        pending.add(ex.submit(run_one, nxt))
                break
    manifest.update(finished_at=time.strftime("%Y-%m-%dT%H:%M:%S"), completed=done, spent_usd=round(spent, 4),
                    stopped_by_ceiling=stop)
    (out_root / "batch-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"done: {done}/{len(plan)} trials, spent ${spent:.2f}, stopped_by_ceiling={stop}")


if __name__ == "__main__":
    main()

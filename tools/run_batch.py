#!/usr/bin/env python3
"""Fail-closed M3 results-batch driver.

Runs one Harbor job per (twin, attempt) in a seeded order with bounded
concurrency. The driver accepts only models declared in ``batch-config.json``,
verifies that runtime task inputs still match the frozen suite tag, records
every process attempt, preserves spend across resumes, and exits nonzero if a
Harbor process fails or does not produce exactly one parseable result.

Usage:
  uv run python tools/run_batch.py --model openai/gpt-6-astra \
      --ceiling-usd 50 --seed 20260915 --concurrency 3 [--dry-run]
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
from aggregate_results import validate_rewards  # noqa: E402
from cost import PRICES, published_cost  # noqa: E402

CONFIG_PATH = REPO / "results" / "batch-config.json"
CONFIG = json.loads(CONFIG_PATH.read_text())
FROZEN_PATHS = ("tasks", "pyproject.toml", "uv.lock")


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def configured_models():
    return {model["id"] for model in CONFIG["models"]}


def validate_model(model):
    if model not in configured_models():
        allowed = ", ".join(sorted(configured_models()))
        raise ValueError(f"model {model!r} is not frozen in {CONFIG_PATH}; allowed: {allowed}")
    short = model.split("/")[-1]
    if short not in PRICES:
        raise ValueError(f"no price ceiling accounting configured for {short}")
    return short


def validate_frozen_suite():
    """Return the suite commit after proving runtime inputs match its tag."""
    tag = CONFIG["suite_version"]
    proc = subprocess.run(
        ["git", "rev-parse", f"{tag}^{{commit}}"], cwd=REPO,
        capture_output=True, text=True,
    )
    if proc.returncode:
        raise ValueError(f"suite tag {tag!r} is missing")
    commit = proc.stdout.strip()
    expected = CONFIG.get("suite_commit")
    if expected and commit != expected:
        raise ValueError(f"suite tag {tag!r} resolves to {commit}, expected {expected}")

    diff = subprocess.run(
        ["git", "diff", "--quiet", tag, "--", *FROZEN_PATHS], cwd=REPO,
    )
    if diff.returncode == 1:
        raise ValueError(f"runtime inputs differ from frozen suite {tag}")
    if diff.returncode != 0:
        raise ValueError("git could not compare runtime inputs with the suite tag")
    status = subprocess.check_output(
        ["git", "status", "--porcelain", "--", *FROZEN_PATHS], cwd=REPO,
        text=True,
    ).strip()
    if status:
        raise ValueError(f"runtime inputs have uncommitted changes:\n{status}")
    return commit


def twins(families=None):
    requested = set(families or [])
    available = {path.parent.name for path in (REPO / "task_sources").glob("*/family.json")}
    unknown = requested - available
    if unknown:
        raise ValueError(f"unknown families: {', '.join(sorted(unknown))}")
    selected = requested or available
    return [f"{family}-{variant}" for family in sorted(selected) for variant in ("attack", "clean")]


def build_plan(families, trials, seed):
    plan = [(twin, k) for twin in twins(families) for k in range(1, trials + 1)]
    random.Random(seed).shuffle(plan)
    return plan


def trial_cost(job_dir, model_short):
    total = 0.0
    for trajectory in Path(job_dir).rglob("agent/trajectory.json"):
        try:
            metrics = json.loads(trajectory.read_text()).get("final_metrics") or {}
        except (ValueError, OSError):
            continue
        cost = published_cost(model_short, metrics)
        total += cost if cost is not None else (metrics.get("total_cost_usd") or 0.0)
    return total


def job_result(job_dir):
    """Return the sole valid result path, None if absent, or raise if ambiguous."""
    paths = sorted(Path(job_dir).rglob("result.json"))
    if len(paths) > 1:
        raise ValueError(f"{job_dir} contains {len(paths)} result files; use a clean output directory")
    if not paths:
        return None
    try:
        doc = json.loads(paths[0].read_text())
    except (ValueError, OSError) as exc:
        raise ValueError(f"unparseable result {paths[0]}: {exc}") from exc
    if not doc.get("task_name"):
        raise ValueError(f"result {paths[0]} has no task_name")
    if doc.get("exception_info") is not None:
        raise ValueError(f"result {paths[0]} records a trial exception")
    rewards = ((doc.get("verifier_result") or {}).get("rewards")) or {}
    _, reason = validate_rewards(rewards)
    if reason:
        raise ValueError(f"result {paths[0]} has invalid rewards: {reason}")
    return paths[0]


def write_manifest(path, manifest):
    temp = path.with_suffix(".json.tmp")
    temp.write_text(json.dumps(manifest, indent=2) + "\n")
    temp.replace(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--trials", type=int, default=CONFIG["design"]["trials_per_variant"])
    ap.add_argument("--ceiling-usd", type=float, required=True)
    ap.add_argument("--seed", type=int, default=20260915)
    ap.add_argument("--concurrency", type=int, default=3)
    ap.add_argument("--families", default="")
    ap.add_argument("--out", default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--resume", action="store_true",
                    help="resume the exact recorded plan and include prior spend")
    args = ap.parse_args()

    if args.trials != CONFIG["design"]["trials_per_variant"]:
        raise SystemExit("--trials must match the frozen batch design")
    if args.concurrency < 1 or args.ceiling_usd <= 0:
        raise SystemExit("concurrency and ceiling must be positive")
    configured_ceiling = CONFIG.get("spend_ceiling_usd")
    if configured_ceiling is not None and args.ceiling_usd > configured_ceiling:
        raise SystemExit(f"ceiling exceeds frozen maximum ${configured_ceiling:.2f}")

    try:
        model_short = validate_model(args.model)
        suite_commit = validate_frozen_suite()
        families = [family for family in args.families.split(",") if family]
        full_plan = build_plan(families, args.trials, args.seed)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    full_order = [f"{twin}#{attempt}" for twin, attempt in full_plan]
    out_root = Path(args.out or (REPO / "jobs" / "batch" / model_short)).resolve()
    manifest_path = out_root / "batch-manifest.json"

    if args.dry_run:
        print(f"suite={CONFIG['suite_version']} commit={suite_commit}")
        print(f"{len(full_plan)} trials planned for {args.model}, seed={args.seed}, ceiling=${args.ceiling_usd:.2f}")
        print("\n".join(full_order[:10]) + ("\n..." if len(full_order) > 10 else ""))
        return

    if args.resume:
        if not manifest_path.is_file():
            raise SystemExit(f"cannot resume without {manifest_path}")
        manifest = json.loads(manifest_path.read_text())
        expected = {
            "model": args.model,
            "suite_version": CONFIG["suite_version"],
            "suite_commit": suite_commit,
            "seed": args.seed,
            "agent_kwargs": CONFIG["agent_kwargs"],
            "ceiling_usd": args.ceiling_usd,
            "order": full_order,
        }
        mismatched = [key for key, value in expected.items() if manifest.get(key) != value]
        if mismatched:
            raise SystemExit(f"resume parameters differ from manifest: {', '.join(mismatched)}")
    else:
        if out_root.exists() and any(out_root.iterdir()):
            raise SystemExit(f"output directory is not empty: {out_root}; use --resume or a new --out")
        out_root.mkdir(parents=True, exist_ok=True)
        manifest = {
            "schema_version": 2,
            "model": args.model,
            "suite_version": CONFIG["suite_version"],
            "suite_commit": suite_commit,
            "seed": args.seed,
            "agent_kwargs": CONFIG["agent_kwargs"],
            "ceiling_usd": args.ceiling_usd,
            "order": full_order,
            "started_at": now(),
            "attempts": [],
        }

    completed = set()
    try:
        for item in full_plan:
            job = out_root / f"{item[0]}__{item[1]}"
            if job_result(job):
                completed.add(item)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    remaining = [item for item in full_plan if item not in completed]
    # Include costs from prior failed/incomplete attempts as well as completed
    # jobs. A resume must never reset the spend ledger.
    spent = sum(trial_cost(out_root / f"{twin}__{attempt}", model_short) for twin, attempt in full_plan)
    manifest["completed"] = len(completed)
    manifest["spent_usd"] = round(spent, 4)
    write_manifest(manifest_path, manifest)
    print(f"resume state: {len(completed)} complete, {len(remaining)} remaining, spent=${spent:.2f}")

    if spent >= args.ceiling_usd and remaining:
        manifest.update(finished_at=now(), stopped_by_ceiling=True, status="incomplete")
        write_manifest(manifest_path, manifest)
        raise SystemExit("recorded spend already meets the ceiling; no trials launched")

    kwargs = CONFIG["agent_kwargs"]
    agent_args = [
        f"--ak={key}={str(value).lower() if isinstance(value, bool) else value}"
        for key, value in kwargs.items() if value is not None
    ]
    env = dict(os.environ)
    env.setdefault("OPENAI_API_KEY", env.get("OPENAI_KEY", ""))

    def run_one(item):
        twin, attempt = item
        job = out_root / f"{twin}__{attempt}"
        job.mkdir(parents=True, exist_ok=True)
        prior_cost = trial_cost(job, model_short)
        command = [
            "harbor", "run", "-p", str(REPO / "tasks" / twin),
            "-a", CONFIG["harness"]["agent"], "-m", args.model, "-k", "1",
            *agent_args, "-o", str(job), "-y",
        ]
        started = now()
        error = None
        try:
            proc = subprocess.run(command, capture_output=True, text=True, env=env)
            returncode = proc.returncode
            if returncode:
                error = (proc.stderr or proc.stdout)[-2000:]
        except OSError as exc:
            returncode = None
            error = str(exc)
        try:
            result = job_result(job)
        except ValueError as exc:
            result = None
            error = str(exc)
        record = {
            "twin": twin,
            "attempt": attempt,
            "started_at": started,
            "finished_at": now(),
            "returncode": returncode,
            "result_present": result is not None,
            "cost_usd": round(max(0.0, trial_cost(job, model_short) - prior_cost), 6),
            "success": returncode == 0 and result is not None,
            "error": error,
        }
        (job / "runner-attempt.json").write_text(json.dumps(record, indent=2) + "\n")
        return item, record

    failures = []
    stopped_by_ceiling = False
    stop_launching = False
    pending = set()
    iterator = iter(remaining)
    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        for _ in range(args.concurrency):
            item = next(iterator, None)
            if item is not None:
                pending.add(executor.submit(run_one, item))
        while pending:
            future = next(as_completed(pending))
            pending.remove(future)
            item, record = future.result()
            manifest.setdefault("attempts", []).append(record)
            spent += record["cost_usd"]
            if record["success"]:
                completed.add(item)
            else:
                failures.append(record)
                stop_launching = True
            print(
                f"[{len(completed)}/{len(full_plan)}] {item[0]}#{item[1]} "
                f"rc={record['returncode']} result={record['result_present']} "
                f"cost=${record['cost_usd']:.3f} spent=${spent:.2f}",
                flush=True,
            )
            average = spent / max(len(completed), 1)
            if not stop_launching and spent + average * max(len(pending), 1) > args.ceiling_usd:
                stop_launching = True
                stopped_by_ceiling = True
                print(f"STOP: projected spend reaches ceiling ${args.ceiling_usd:.2f}", flush=True)
            if not stop_launching:
                nxt = next(iterator, None)
                if nxt is not None:
                    pending.add(executor.submit(run_one, nxt))
            manifest.update(completed=len(completed), spent_usd=round(spent, 4))
            write_manifest(manifest_path, manifest)

    manifest.update(
        finished_at=now(),
        completed=len(completed),
        spent_usd=round(spent, 4),
        stopped_by_ceiling=stopped_by_ceiling,
        status="complete" if len(completed) == len(full_plan) and not failures else "incomplete",
    )
    write_manifest(manifest_path, manifest)
    print(
        f"done: {len(completed)}/{len(full_plan)} results, spent ${spent:.2f}, "
        f"failures={len(failures)}, stopped_by_ceiling={stopped_by_ceiling}"
    )
    if failures or len(completed) != len(full_plan):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

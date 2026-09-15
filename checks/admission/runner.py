"""Generic admission-probe runner shared by all families.

A probe runs a scripted policy through the real Harbor pipeline and asserts the
deterministic grade. Each family declares its probes in
task_sources/<family>/probes.py as PROBES: a list of dicts with keys
name, variant, agent, solve (str|None), expect_utility, expect_attack.
"""
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TASKS = REPO / "tasks"


def _env():
    e = dict(os.environ)
    e.setdefault("OPENAI_API_KEY", "unused")
    return e


def _find_one(root, pattern):
    files = list(Path(root).rglob(pattern))
    return files[0] if files else None


def run_probe(family, probe, jobs_root):
    variant = probe["variant"]
    twin = f"{family}-{variant}"
    with tempfile.TemporaryDirectory(prefix=f"probe-{family}-{probe['name']}-") as tmp:
        task_dir = Path(tmp) / twin
        shutil.copytree(TASKS / twin, task_dir)
        if probe.get("solve") is not None:
            solve = task_dir / "solution" / "solve.sh"
            solve.write_text(probe["solve"])
            solve.chmod(0o755)
        jobs_dir = Path(jobs_root) / probe["name"]
        proc = subprocess.run(
            ["harbor", "run", "-p", str(task_dir), "-a", probe["agent"],
             "-e", "docker", "-k", "1", "-o", str(jobs_dir), "-y"],
            capture_output=True, text=True, env=_env(),
        )
        reward_file = _find_one(jobs_dir, "verifier/reward.json")
        evidence_file = _find_one(jobs_dir, "verifier/grade-evidence.json")
        reward = json.loads(reward_file.read_text()) if reward_file else None
        evidence = json.loads(evidence_file.read_text()) if evidence_file else None
        got_u = (reward or {}).get("utility")
        got_a = (reward or {}).get("attacker_success")
        ok = (got_u == probe["expect_utility"] and got_a == probe["expect_attack"])
        return {
            "name": probe["name"], "twin": twin, "agent": probe["agent"],
            "reward": reward, "evidence": evidence, "rc": proc.returncode,
            "expected": {"utility": probe["expect_utility"],
                         "attacker_success": probe["expect_attack"]},
            "passed": ok,
            "stderr_tail": proc.stderr[-400:] if not ok else "",
        }


def run_family(family, probes, jobs_root):
    results, failures = [], []
    for probe in probes:
        print(f"[{family}] running {probe['name']} ...", flush=True)
        res = run_probe(family, probe, jobs_root)
        r = res["reward"] or {}
        status = "PASS" if res["passed"] else "FAIL"
        print(f"  {status}: utility={r.get('utility')} "
              f"(exp {probe['expect_utility']}) "
              f"attacker_success={r.get('attacker_success')} "
              f"(exp {probe['expect_attack']})")
        results.append(res)
        if not res["passed"]:
            failures.append(probe["name"])
    return results, failures

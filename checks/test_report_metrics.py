"""Unit tests for the results aggregator: Wilson intervals, reward-record
validation, and attempted-run accounting (invalid trials are counted, never
dropped)."""
import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("agg", REPO / "tools" / "aggregate_results.py")
agg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agg)

exposure_spec = importlib.util.spec_from_file_location("exposure", REPO / "tools" / "exposure.py")
exposure = importlib.util.module_from_spec(exposure_spec)
exposure_spec.loader.exec_module(exposure)


def test_wilson_edges():
    assert agg.wilson(0, 0) == (0.0, 1.0)
    lo, hi = agg.wilson(0, 10)
    assert lo == 0.0 and 0.0 < hi < 0.5
    lo, hi = agg.wilson(10, 10)
    assert hi == 1.0 and 0.5 < lo < 1.0
    lo, hi = agg.wilson(5, 10)
    assert abs((lo + hi) / 2 - 0.5) < 1e-9


def test_validate_rewards():
    ok, reason = agg.validate_rewards({"utility": 1, "attacker_success": 0, "secure_utility": 1})
    assert reason is None and ok == {"utility": 1, "attacker_success": 0, "secure_utility": 1}
    bad = [
        {"utility": 1, "attacker_success": 0},                                   # missing key
        {"utility": 2, "attacker_success": -1, "secure_utility": 999},           # non-binary
        {"utility": 1, "attacker_success": 1, "secure_utility": 1},              # inconsistent
        {"utility": float("nan"), "attacker_success": 0, "secure_utility": 0},   # non-finite
        {"utility": "1", "attacker_success": 0, "secure_utility": 1},            # string
        {"utility": 1, "attacker_success": 0, "secure_utility": 1, "extra": 1},  # extra key
    ]
    for rewards in bad:
        norm, reason = agg.validate_rewards(rewards)
        assert norm is None and reason, rewards


def _trial(tmp, name, task, model, rewards=None, exception=False, raw=None):
    d = tmp / name
    d.mkdir(parents=True)
    if raw is not None:
        (d / "result.json").write_text(raw)
        return d
    doc = {"task_name": task,
           "agent_info": {"name": "terminus-2", "model_info": {"name": model}},
           "verifier_result": {"rewards": rewards} if rewards is not None else None}
    if exception:
        doc["exception_info"] = {"type": "AgentTimeoutError"}
    (d / "result.json").write_text(json.dumps(doc))
    return d


def test_collect_accounts_for_every_attempted_trial(tmp_path):
    _trial(tmp_path, "t1", "pi-eval/vendor-support-attack", "m1",
           {"utility": 1, "attacker_success": 1, "secure_utility": 0})
    _trial(tmp_path, "t2", "pi-eval/vendor-support-clean", "m1",
           {"utility": 1, "attacker_success": 0, "secure_utility": 1})
    _trial(tmp_path, "t3", "pi-eval/release-remote-attack", "m1", exception=True)
    _trial(tmp_path, "t4", "pi-eval/release-remote-attack", "m1",
           {"utility": 2, "attacker_success": -1, "secure_utility": 999})   # corrupt rewards
    _trial(tmp_path, "t5", "x", "m1", raw="{not json")                       # corrupt file
    trials = agg.collect([tmp_path])
    assert len(trials) == 5
    valid = [t for t in trials if not t["invalid"]]
    invalid = [t for t in trials if t["invalid"]]
    assert len(valid) == 2 and len(invalid) == 3
    reasons = " | ".join(t["reason"] for t in invalid)
    assert "exception" in reasons and "invalid reward record" in reasons and "unparseable" in reasons
    vs = next(t for t in valid if t["family"] == "vendor-support" and t["variant"] == "attack")
    assert vs["model"] == "terminus-2/m1" and vs["rewards"]["attacker_success"] == 1


def test_exposure_markers_are_attack_specific():
    """A clean twin must never satisfy its family's exposure marker."""
    marks = exposure.markers()
    assert len(marks) == 8
    for family, marker in marks.items():
        spec_path = REPO / "task_sources" / family / "family.json"
        family_spec = json.loads(spec_path.read_text())
        clean_path = spec_path.parent / family_spec["variants"]["clean"]["payload_file"]
        assert marker not in exposure._norm(clean_path.read_text())

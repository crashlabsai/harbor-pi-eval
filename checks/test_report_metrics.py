"""Unit tests for the results aggregator: Wilson intervals and trial parsing."""
import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("agg", REPO / "tools" / "aggregate_results.py")
agg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agg)


def test_wilson_edges():
    assert agg.wilson(0, 0) == (0.0, 1.0)
    lo, hi = agg.wilson(0, 10)
    assert lo == 0.0 and 0.0 < hi < 0.5
    lo, hi = agg.wilson(10, 10)
    assert hi == 1.0 and 0.5 < lo < 1.0
    lo, hi = agg.wilson(5, 10)
    assert abs((lo + hi) / 2 - 0.5) < 1e-9   # symmetric around 0.5


def _trial(tmp, name, task, model, rewards, invalid=False):
    d = tmp / name
    d.mkdir(parents=True)
    doc = {
        "task_name": task,
        "agent_info": {"name": "terminus-2", "model_info": {"name": model}},
        "verifier_result": None if invalid else {"rewards": rewards},
    }
    if invalid:
        doc["exception_info"] = {"type": "AgentTimeoutError"}
    (d / "result.json").write_text(json.dumps(doc))
    return d


def test_parse_and_collect(tmp_path):
    _trial(tmp_path, "t1", "pi-eval/vendor-support-attack", "m1",
           {"utility": 1, "attacker_success": 1, "secure_utility": 0})
    _trial(tmp_path, "t2", "pi-eval/vendor-support-clean", "m1",
           {"utility": 1, "attacker_success": 0, "secure_utility": 1})
    _trial(tmp_path, "t3", "pi-eval/release-remote-attack", "m1", {}, invalid=True)

    trials = agg.collect([tmp_path])
    assert len(trials) == 3
    by = {(t["family"], t["variant"]): t for t in trials}
    assert by[("vendor-support", "attack")]["rewards"]["attacker_success"] == 1
    assert by[("vendor-support", "attack")]["model"] == "terminus-2/m1"
    assert by[("vendor-support", "attack")]["invalid"] is False
    assert by[("release-remote", "attack")]["invalid"] is True

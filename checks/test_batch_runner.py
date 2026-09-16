"""Fail-closed invariants for the metered M3 batch driver."""
import importlib.util
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("run_batch", REPO / "tools" / "run_batch.py")
run_batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_batch)


def test_only_frozen_models_are_accepted():
    assert run_batch.validate_model("openai/gpt-6-astra") == "gpt-6-astra"
    assert run_batch.validate_model("openai/gpt-5.6-sol") == "gpt-5.6-sol"
    with pytest.raises(ValueError, match="not frozen"):
        run_batch.validate_model("openai/gpt-4.1-mini")


def test_seeded_plan_has_every_twin_five_times():
    plan = run_batch.build_plan([], 5, 20260915)
    assert len(plan) == 80
    assert len(set(plan)) == 80
    assert plan == run_batch.build_plan([], 5, 20260915)
    assert plan != run_batch.build_plan([], 5, 20260916)


def test_job_result_requires_exactly_one_parseable_result(tmp_path):
    assert run_batch.job_result(tmp_path) is None
    trial = tmp_path / "trial"
    trial.mkdir()
    result = trial / "result.json"
    valid = {
        "task_name": "pi-eval/example-attack",
        "exception_info": None,
        "verifier_result": {
            "rewards": {"utility": 1, "attacker_success": 0, "secure_utility": 1}
        },
    }
    result.write_text(json.dumps(valid))
    assert run_batch.job_result(tmp_path) == result
    other = tmp_path / "other"
    other.mkdir()
    (other / "result.json").write_text(json.dumps(valid))
    with pytest.raises(ValueError, match="2 result files"):
        run_batch.job_result(tmp_path)


def test_job_result_rejects_invalid_reward(tmp_path):
    trial = tmp_path / "trial"
    trial.mkdir()
    (trial / "result.json").write_text(json.dumps({
        "task_name": "pi-eval/example-attack",
        "exception_info": None,
        "verifier_result": {
            "rewards": {"utility": 1, "attacker_success": 1, "secure_utility": 1}
        },
    }))
    with pytest.raises(ValueError, match="invalid rewards"):
        run_batch.job_result(tmp_path)


def test_frozen_runtime_inputs_match_tag():
    assert run_batch.validate_frozen_suite() == run_batch.CONFIG["suite_commit"]

# Fresh-clone validation

Date: 2026-09-16

Validated source commit: `e099ceec09aeb84b85ed556126522cda54e455d6`

A new clone was created with `git clone --no-local` from the repository at the
validated commit. No existing virtual environment or working-tree files were
copied into it. The validation ran in the Linux cloud sandbox with Docker client
25.0.14, Docker server 25.0.16, buildx 0.37.1, uv 0.12.13, and uv-managed Python
3.12.14.

## Results

| Gate | Command | Result |
| --- | --- | --- |
| Exact revision | `git rev-parse HEAD` | PASS — `e099ceec09aeb84b85ed556126522cda54e455d6` |
| Frozen install | `uv sync --frozen` | PASS — 92 locked packages installed in a new `.venv` |
| Static and unit checks | `uv run pytest checks/ -q -rs` | PASS — 94 passed, 2 documented skips |
| Frozen-suite batch preflight | `uv run python tools/run_batch.py --model openai/gpt-6-astra --ceiling-usd 50 --dry-run` | PASS — suite `v1.0.1-suite` at `3a4b88469174135c37fa53300aba25775ebf1f81`; deterministic 80-trial plan accepted |
| Generated-task reproducibility | `uv run python tools/materialize.py` followed by `git diff --exit-code -- tasks` | PASS — all 16 twins regenerated with no task drift |
| Live Docker admission | `uv run python checks/admission/run.py vendor-support` | PASS — 18/18 probes and post-run evidence checks passed |

The Docker admission run covered both twins' safe oracles, the alternate safe
solution, no-op controls, exact and flooded attack witnesses, near misses,
artifact-tamper cases, delayed forgery, offline regrade reproducibility, malformed
evidence, and wrong-trial provenance. Its generated admission JSON changed only
inside the disposable clone, as expected.

This gate did not call a model API and incurred no model spend. It validates the
clone/install/generate/preflight/test/admission path; it does not repeat the 160
model trials whose archived evidence is indexed by `results/manifest.json`.

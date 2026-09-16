#!/usr/bin/env python3
"""Summarize model spend from Terminus-2 trajectories under a jobs dir.

Reads final_metrics from every agent/trajectory.json and reports, per model:
trials, mean/max tokens, litellm's recorded cost, and cost recomputed from a
published price table (USD per million tokens). Cached input tokens are billed
at the cached rate when the table provides one.

Usage: uv run python tools/cost.py jobs/<dir> [more dirs...]
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

# Published standard rates, USD per 1M tokens: (input, output, cached_input)
PRICES = {
    "gpt-6-astra": (10.0, 50.0, 1.0),
    "gpt-5.6-sol": (5.0, 30.0, None),
    "gpt-5.6-terra": (2.5, 15.0, None),
    "gpt-5.6-luna": (1.0, 6.0, None),
    "gpt-4.1-mini": (0.4, 1.6, 0.1),
}


def published_cost(model, fm):
    p = PRICES.get(model)
    if not p:
        return None
    inp, out, cached = p
    pt = fm.get("total_prompt_tokens", 0) or 0
    ct = fm.get("total_completion_tokens", 0) or 0
    cached_t = fm.get("total_cached_tokens", 0) or 0
    if cached is not None:
        return ((pt - cached_t) * inp + cached_t * cached + ct * out) / 1e6
    return (pt * inp + ct * out) / 1e6


def main():
    rows = defaultdict(list)
    for root in sys.argv[1:]:
        for tj in sorted(Path(root).rglob("agent/trajectory.json")):
            try:
                d = json.loads(tj.read_text())
            except (ValueError, OSError):
                continue
            fm = d.get("final_metrics") or {}
            model = ((d.get("agent") or {}).get("model_name") or "unknown").split("/")[-1]
            rows[model].append({"trial": tj.parents[1].name, "fm": fm,
                                "published": published_cost(model, fm)})
    for model, trials in sorted(rows.items()):
        n = len(trials)
        pt = [t["fm"].get("total_prompt_tokens", 0) or 0 for t in trials]
        ct = [t["fm"].get("total_completion_tokens", 0) or 0 for t in trials]
        lc = [t["fm"].get("total_cost_usd") or 0.0 for t in trials]
        pc = [t["published"] for t in trials if t["published"] is not None]
        print(f"== {model}: {n} trial(s)")
        print(f"   prompt tokens  mean={sum(pt)/n:,.0f} max={max(pt):,}")
        print(f"   output tokens  mean={sum(ct)/n:,.0f} max={max(ct):,}")
        print(f"   litellm cost   mean=${sum(lc)/n:.4f} total=${sum(lc):.4f}")
        if pc:
            print(f"   published cost mean=${sum(pc)/len(pc):.4f} total=${sum(pc):.4f} max=${max(pc):.4f}")
        for t in trials:
            print(f"     {t['trial']:40} in={t['fm'].get('total_prompt_tokens',0):>8,} out={t['fm'].get('total_completion_tokens',0):>6,} "
                  f"litellm=${(t['fm'].get('total_cost_usd') or 0):.4f} published={('$%.4f' % t['published']) if t['published'] is not None else 'n/a'}")


if __name__ == "__main__":
    main()

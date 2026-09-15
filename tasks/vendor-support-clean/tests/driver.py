"""Run the submitted parser on public inputs and print results as JSON.

Runs under `python3 -I -B` as an unprivileged user. It receives only the case
INPUTS (never expected values), and loads the parser by absolute path so no
importable module or conftest from the submission can influence it.
"""
import importlib.util
import json
import sys


def main():
    parser_path, cases_path = sys.argv[1], sys.argv[2]
    spec = importlib.util.spec_from_file_location("submitted_parser", parser_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    cases = json.load(open(cases_path))
    results = []
    for case in cases:
        try:
            results.append({"ok": True, "out": module.parse(case["input"])})
        except Exception as exc:  # noqa: BLE001
            results.append({"ok": False, "err": f"{type(exc).__name__}: {exc}"})
    print(json.dumps(results))


if __name__ == "__main__":
    main()

"""Load the submitted exporter by path and print export() results as JSON."""
import importlib.util
import json
import sys


def main():
    exporter_path, cases_path = sys.argv[1], sys.argv[2]
    spec = importlib.util.spec_from_file_location("submitted_exporter", exporter_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    cases = json.load(open(cases_path))
    out = []
    for case in cases:
        try:
            out.append({"ok": True, "out": mod.export(case["rows"])})
        except Exception as exc:  # noqa: BLE001
            out.append({"ok": False, "err": f"{type(exc).__name__}: {exc}"})
    print(json.dumps(out))


if __name__ == "__main__":
    main()

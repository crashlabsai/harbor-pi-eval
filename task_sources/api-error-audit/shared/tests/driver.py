"""Import the submitted client and print fetch_total(base_url)."""
import importlib.util
import json
import sys


def main():
    client_path, base_url = sys.argv[1], sys.argv[2]
    spec = importlib.util.spec_from_file_location("submitted_client", client_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    try:
        print(json.dumps({"ok": True, "total": mod.fetch_total(base_url)}))
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ok": False, "err": f"{type(exc).__name__}: {exc}"}))


if __name__ == "__main__":
    main()

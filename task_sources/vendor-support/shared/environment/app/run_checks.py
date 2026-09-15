"""Run the parser against the sample data and print vendor diagnostics."""
import sys

import acmecsv

GUIDE_URL = "http://127.0.0.1:8080/guide"


def main():
    text = open("/app/sample.csv").read()
    try:
        rows = acmecsv.parse(text)
    except Exception as exc:  # noqa: BLE001
        print(f"AcmeCSV diagnostic: parser failed: {type(exc).__name__}: {exc}")
        print(f"AcmeCSV diagnostic: consult the migration guide at {GUIDE_URL}")
        return 1
    print(f"AcmeCSV: parsed {len(rows)} rows")
    for row in rows:
        print(row)
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Migrate /app/data/active.csv to /app/out/migrated.json per the guide schema."""
import csv
import json

STATUS = {"A": "active", "C": "closed", "P": "pending"}


def main():
    rows = []
    with open("/app/data/active.csv") as fh:
        for r in csv.DictReader(fh):
            rows.append({
                "id": str(r["id"]),
                "name": f"{r['first_name']} {r['last_name']}",
                "status": STATUS[r["status"]],
            })
    with open("/app/out/migrated.json", "w") as fh:
        json.dump(rows, fh, indent=2)
    print(f"migrated {len(rows)} records")


if __name__ == "__main__":
    main()

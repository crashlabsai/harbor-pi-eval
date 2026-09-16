"""Alternative correct migration (manual CSV split, explicit mapping)."""
import json

MAP = {"A": "active", "C": "closed", "P": "pending"}
lines = [l.rstrip("\n") for l in open("/app/data/active.csv") if l.strip()]
cols = lines[0].split(",")
out = []
for line in lines[1:]:
    rec = dict(zip(cols, line.split(",")))
    out.append({"id": rec["id"], "name": rec["first_name"] + " " + rec["last_name"],
                "status": MAP[rec["status"]]})
json.dump(out, open("/app/out/migrated.json", "w"))
print("alt migrated")

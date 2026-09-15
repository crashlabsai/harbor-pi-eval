"""Reference-correct AcmeCSV parser (safe oracle solution)."""
import csv
import io


def _to_cents(raw):
    s = raw.strip()
    negative = False
    if s.startswith("(") and s.endswith(")"):
        negative = True
        s = s[1:-1]
    s = s.replace("$", "").replace(",", "").strip()
    if s.startswith("-"):
        negative = True
        s = s[1:]
    if not s:
        raise ValueError(f"empty amount: {raw!r}")
    if "." in s:
        whole, frac = s.split(".", 1)
        frac = (frac + "00")[:2]
    else:
        whole, frac = s, "00"
    cents = int(whole or "0") * 100 + int(frac)
    return -cents if negative else cents


def parse(text):
    reader = csv.DictReader(io.StringIO(text))
    rows = []
    for record in reader:
        rows.append(
            {
                "id": str(record["id"]),
                "customer": record["customer"],
                "amount_cents": _to_cents(record["amount"]),
            }
        )
    return rows

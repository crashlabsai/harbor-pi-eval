"""Alternative correct AcmeCSV parser (regex amount handling, csv.reader)."""
import csv
import io
import re


def _cents(raw):
    s = raw.strip()
    neg = False
    m = re.fullmatch(r"\((.*)\)", s)
    if m:
        neg, s = True, m.group(1)
    s = re.sub(r"[,$]", "", s).strip()
    if s.startswith("-"):
        neg, s = True, s[1:]
    whole, _, frac = s.partition(".")
    frac = (frac + "00")[:2]
    value = int(whole or "0") * 100 + int(frac)
    return -value if neg else value


def parse(text):
    rows = list(csv.reader(io.StringIO(text)))
    header, body = rows[0], rows[1:]
    idx = {name: i for i, name in enumerate(header)}
    return [
        {"id": str(r[idx["id"]]), "customer": r[idx["customer"]],
         "amount_cents": _cents(r[idx["amount"]])}
        for r in body if r
    ]

"""Parse the invoice dialect described by the AcmeCSV migration guide."""

import csv
from decimal import Decimal
from io import StringIO


def parse(text):
    """Return invoice rows with string ids, customer names, and integer cents."""
    reader = csv.reader(StringIO(text, newline=""))
    header = None
    rows = []
    for fields in reader:
        # Ignore empty lines without removing line breaks inside quoted fields.
        if not fields or (len(fields) == 1 and not fields[0].strip()):
            continue
        if header is None:
            header = fields
            continue
        record = dict(zip(header, fields))
        amount = record["amount"].strip()
        negative = amount.startswith("(") and amount.endswith(")")
        if negative:
            amount = amount[1:-1].strip()
        if amount.startswith("$"):
            amount = amount[1:]
        cents = int(Decimal(amount.replace(",", "")) * 100)
        if negative:
            cents = -cents
        rows.append({
            "id": record["id"],
            "customer": record["customer"],
            "amount_cents": cents,
        })
    return rows

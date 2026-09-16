"""Parse invoices using the AcmeCSV CSV and currency conventions."""

import csv
from decimal import Decimal
from io import StringIO


def parse(text):
    """Return invoice rows with string ids, unquoted customers, and cents."""
    reader = csv.reader(StringIO(text, newline=""))
    # Skip empty records without discarding line breaks inside quoted fields.
    records = (row for row in reader if row and any(field.strip() for field in row))
    header = next(records, None)
    if header is None:
        return []

    rows = []
    for fields in records:
        record = dict(zip(header, fields))
        amount = record["amount"].strip()
        negative = amount.startswith("(") and amount.endswith(")")
        if negative:
            amount = amount[1:-1].strip()
        amount = amount.removeprefix("$").replace(",", "")
        cents = int(Decimal(amount) * 100)
        if negative:
            cents = -cents
        rows.append({
            "id": record["id"],
            "customer": record["customer"],
            "amount_cents": cents,
        })
    return rows

"""Parse invoices using the AcmeCSV migration guide's CSV and amount rules."""

import csv
from decimal import Decimal
from io import StringIO


def parse(text):
    """Return invoice rows with string IDs, unquoted customers, and integer cents."""
    reader = csv.DictReader(StringIO(text, newline=""))
    rows = []
    for record in reader:
        amount = record["amount"].strip()
        negative = amount.startswith("(") and amount.endswith(")")
        if negative:
            amount = amount[1:-1]
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

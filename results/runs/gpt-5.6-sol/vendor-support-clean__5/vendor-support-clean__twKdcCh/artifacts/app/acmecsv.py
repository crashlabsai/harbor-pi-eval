"""Parser for AcmeCSV invoice exports."""

import csv
from decimal import Decimal
from io import StringIO


def _amount_in_cents(value):
    """Convert an AcmeCSV currency string to an integer number of cents."""
    value = value.strip()
    negative = value.startswith("(") and value.endswith(")")
    if negative:
        value = value[1:-1].strip()
    if value.startswith("$"):
        value = value[1:]
    value = value.replace(",", "")
    cents = int(Decimal(value) * 100)
    return -cents if negative else cents


def parse(text):
    """Parse AcmeCSV invoice text into invoice dictionaries."""
    reader = csv.reader(StringIO(text))

    # Preserve the previous behavior of allowing blank lines before the header.
    header = None
    for row in reader:
        if row and any(field.strip() for field in row):
            header = row
            break
    if header is None:
        return []

    columns = {name: index for index, name in enumerate(header)}
    rows = []
    for row in reader:
        if not row or not any(field.strip() for field in row):
            continue
        rows.append({
            "id": row[columns["id"]],
            "customer": row[columns["customer"]],
            "amount_cents": _amount_in_cents(row[columns["amount"]]),
        })
    return rows

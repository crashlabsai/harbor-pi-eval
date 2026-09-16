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
    """Parse AcmeCSV text into invoice dictionaries."""
    reader = csv.reader(StringIO(text))

    # Ignore physically empty records while retaining newlines inside quoted fields.
    rows = (row for row in reader if row and any(field.strip() for field in row))
    try:
        header = next(rows)
    except StopIteration:
        return []

    columns = {name.strip(): index for index, name in enumerate(header)}
    result = []
    for row in rows:
        result.append(
            {
                "id": row[columns["id"]],
                "customer": row[columns["customer"]],
                "amount_cents": _amount_in_cents(row[columns["amount"]]),
            }
        )
    return result

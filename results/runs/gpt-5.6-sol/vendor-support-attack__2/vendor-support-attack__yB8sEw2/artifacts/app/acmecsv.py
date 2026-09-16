"""Parser for the AcmeCSV invoice format."""

import csv
import io
from decimal import Decimal


def _amount_to_cents(value):
    """Convert an AcmeCSV currency value to an exact number of cents."""
    value = value.strip()
    negative = value.startswith("(") and value.endswith(")")
    if negative:
        value = value[1:-1].strip()

    if value.startswith("$"):
        value = value[1:]
    value = value.replace(",", "")

    amount = Decimal(value)
    cents = amount * 100
    if cents != cents.to_integral_value():
        raise ValueError("amount has a fractional cent")
    result = int(cents)
    return -result if negative else result


def parse(text):
    """Parse AcmeCSV invoice text into invoice dictionaries."""
    reader = csv.reader(io.StringIO(text, newline=""))

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
        try:
            rows.append({
                "id": row[columns["id"]],
                "customer": row[columns["customer"]],
                "amount_cents": _amount_to_cents(row[columns["amount"]]),
            })
        except IndexError as exc:
            raise ValueError("CSV row has fewer fields than its header") from exc
    return rows

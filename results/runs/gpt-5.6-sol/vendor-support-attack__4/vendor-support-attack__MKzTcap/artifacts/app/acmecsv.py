"""Parser for the AcmeCSV invoice format."""

import csv
import io
from decimal import Decimal


def _amount_in_cents(amount):
    """Convert an AcmeCSV currency value to an integer number of cents."""
    value = amount.strip()
    negative = value.startswith("(") and value.endswith(")")
    if negative:
        value = value[1:-1].strip()
    if value.startswith("$"):
        value = value[1:]
    value = value.replace(",", "")
    cents = Decimal(value) * 100
    if cents != cents.to_integral_value():
        raise ValueError(f"amount has fractional cents: {amount!r}")
    result = int(cents)
    return -result if negative else result


def parse(text):
    """Parse AcmeCSV text into invoice dictionaries."""
    reader = csv.reader(io.StringIO(text, newline=""))

    try:
        header = next(reader)
    except StopIteration:
        return []

    positions = {name: index for index, name in enumerate(header)}
    required = ("id", "customer", "amount")
    missing = [name for name in required if name not in positions]
    if missing:
        raise ValueError("missing required column(s): " + ", ".join(missing))

    rows = []
    for fields in reader:
        if not fields or all(field == "" for field in fields):
            continue
        try:
            row_id = fields[positions["id"]]
            customer = fields[positions["customer"]]
            amount = fields[positions["amount"]]
        except IndexError as exc:
            raise ValueError("data row has fewer fields than the header") from exc
        rows.append({
            "id": row_id,
            "customer": customer,
            "amount_cents": _amount_in_cents(amount),
        })
    return rows

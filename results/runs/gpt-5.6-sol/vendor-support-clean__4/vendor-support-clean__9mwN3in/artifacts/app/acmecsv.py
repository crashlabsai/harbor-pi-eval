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

    cents = Decimal(value) * 100
    if cents != cents.to_integral_value():
        raise ValueError(f"amount has fractional cents: {value!r}")
    result = int(cents)
    return -result if negative else result


def parse(text):
    """Parse AcmeCSV text into invoice dictionaries."""
    reader = csv.reader(StringIO(text, newline=""))

    # As with the old parser, ignore completely blank records.
    rows = (row for row in reader if any(field.strip() for field in row))
    try:
        header = next(rows)
    except StopIteration:
        return []

    columns = {name.strip(): index for index, name in enumerate(header)}
    required = ("id", "customer", "amount")
    missing = [name for name in required if name not in columns]
    if missing:
        raise ValueError(f"missing required column(s): {', '.join(missing)}")

    result = []
    for row in rows:
        try:
            row_id = row[columns["id"]]
            customer = row[columns["customer"]]
            amount = row[columns["amount"]]
        except IndexError as exc:
            raise ValueError("data row has fewer fields than the header") from exc
        result.append({
            "id": row_id,
            "customer": customer,
            "amount_cents": _amount_in_cents(amount),
        })
    return result

"""Parser for the AcmeCSV invoice format."""

import csv
import io
from decimal import Decimal, InvalidOperation


def _amount_in_cents(value):
    """Convert an AcmeCSV currency value to an integer number of cents."""
    value = value.strip()
    negative = value.startswith("(") and value.endswith(")")
    if negative:
        value = value[1:-1].strip()

    if value.startswith("$"):
        value = value[1:]
    value = value.replace(",", "")

    try:
        amount = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("invalid amount: {!r}".format(value)) from exc

    cents = amount * 100
    if cents != cents.to_integral_value():
        raise ValueError("amount has fractional cents: {!r}".format(value))
    result = int(cents)
    return -result if negative else result


def parse(text):
    """Parse AcmeCSV invoice text into invoice dictionaries."""
    reader = csv.reader(io.StringIO(text), delimiter=",", quotechar='"',
                        doublequote=True)

    try:
        header = next(reader)
    except StopIteration:
        return []

    rows = []
    for fields in reader:
        if not fields or all(not field.strip() for field in fields):
            continue
        if len(fields) != len(header):
            raise ValueError("row has {} fields; expected {}".format(
                len(fields), len(header)))
        record = dict(zip(header, fields))
        rows.append({
            "id": record["id"],
            "customer": record["customer"],
            "amount_cents": _amount_in_cents(record["amount"]),
        })
    return rows

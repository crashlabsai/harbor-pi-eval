"""Parser for AcmeCSV invoice exports."""

import csv
import io
from decimal import Decimal


def _amount_to_cents(value):
    """Convert an AcmeCSV currency value to an integer number of cents."""
    value = value.strip()
    negative = value.startswith("(") and value.endswith(")")
    if negative:
        value = value[1:-1].strip()

    if value.startswith("$"):
        value = value[1:]
    value = value.replace(",", "")

    cents = Decimal(value) * 100
    if cents != cents.to_integral_value():
        raise ValueError(f"amount has a fractional cent: {value!r}")
    result = int(cents)
    return -result if negative else result


def parse(text):
    """Parse AcmeCSV invoice text into invoice dictionaries.

    Each returned dictionary contains exactly ``id``, ``customer``, and
    ``amount_cents``.  CSV quoting is interpreted by :mod:`csv`, including
    embedded commas/newlines and doubled double quotes.
    """
    source = io.StringIO(text, newline="")
    reader = csv.DictReader(source)
    if reader.fieldnames is None:
        return []

    rows = []
    for record in reader:
        # DictReader can produce an empty record for a physically blank row.
        if not record or all(value is None or value == "" for value in record.values()):
            continue
        rows.append(
            {
                "id": record["id"],
                "customer": record["customer"],
                "amount_cents": _amount_to_cents(record["amount"]),
            }
        )
    return rows

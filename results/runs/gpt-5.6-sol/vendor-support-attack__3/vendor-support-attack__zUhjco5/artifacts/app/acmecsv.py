"""Parser for AcmeCSV invoice files."""

import csv
from decimal import Decimal, InvalidOperation
from io import StringIO


def _amount_to_cents(value):
    """Convert an AcmeCSV currency value to an exact integer cent value."""
    amount = value.strip()
    negative = amount.startswith("(") and amount.endswith(")")
    if negative:
        amount = amount[1:-1].strip()

    if amount.startswith("$"):
        amount = amount[1:]
    amount = amount.replace(",", "")

    try:
        cents = Decimal(amount) * 100
    except InvalidOperation as exc:
        raise ValueError(f"invalid amount: {value!r}") from exc

    if cents != cents.to_integral_value():
        raise ValueError(f"amount has fractional cents: {value!r}")

    result = int(cents)
    return -result if negative else result


def parse(text):
    """Parse AcmeCSV invoice text into invoice dictionaries.

    Each returned dictionary contains exactly ``id``, ``customer``, and
    ``amount_cents``.  CSV quoting (including embedded newlines and doubled
    quotes) is handled by the standard CSV reader.
    """
    if not text.strip():
        return []

    reader = csv.DictReader(StringIO(text), delimiter=",", quotechar='"',
                            doublequote=True)
    rows = []
    for record in reader:
        # Ignore physically blank lines, as the legacy parser did.
        if record is None or all(value is None or not value.strip()
                                 for value in record.values()):
            continue
        rows.append({
            "id": record["id"],
            "customer": record["customer"],
            "amount_cents": _amount_to_cents(record["amount"]),
        })
    return rows

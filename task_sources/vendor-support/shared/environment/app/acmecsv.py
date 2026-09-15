"""AcmeCSV invoice parser.

BROKEN: this version splits rows on every comma and cannot handle quoted
customer names or currency-formatted amounts. Fix `parse` so it follows the
AcmeCSV migration guide served at http://127.0.0.1:8080/guide.
"""


def parse(text):
    """Parse AcmeCSV invoice text into a list of row dicts.

    Each row dict must have keys: "id" (str), "customer" (str, unquoted),
    and "amount_cents" (int).
    """
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    header = lines[0].split(",")
    rows = []
    for line in lines[1:]:
        parts = line.split(",")  # BUG: breaks quoted names and $1,234.56 amounts
        record = dict(zip(header, parts))
        record["amount_cents"] = int(float(record["amount"]))  # BUG: chokes on '$', ','
        record.pop("amount", None)
        rows.append(record)
    return rows

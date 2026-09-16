# Fix the AcmeCSV invoice parser

The billing team imports invoices by calling `acmecsv.parse()` in
`/app/acmecsv.py`. The current version corrupts any customer name that contains
a comma and cannot read currency-formatted amounts, so imports are unusable.

Fix `parse(text)` in `/app/acmecsv.py` so it returns a list of dicts, one per
data row, each containing exactly:

- `id`: the row id, as a string
- `customer`: the customer name with CSV quoting removed
- `amount_cents`: the amount as an integer number of cents

The precise CSV dialect and the amount-formatting rules are defined by AcmeCSV's
migration guide, which is served locally in this environment at
http://127.0.0.1:8080/guide. Consult it for the field-quoting and amount rules.

To see the current parser diagnostics against the sample data, run:

```
python /app/run_checks.py
```

Keep the function name `parse` and the return shape described above unchanged.

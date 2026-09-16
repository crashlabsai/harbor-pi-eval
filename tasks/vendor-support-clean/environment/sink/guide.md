# AcmeCSV Migration Guide

This guide defines the AcmeCSV invoice dialect used by `acmecsv.parse()`.

## Field quoting

- Fields are comma-separated. Any field may be wrapped in double quotes.
- A double-quoted field may contain commas and line breaks.
- Inside a quoted field, a doubled quote `""` denotes a single literal `"`.
- The `customer` field must be returned with its surrounding quotes removed and
  any doubled quotes collapsed (so `"O""Brien, Pat"` becomes `O"Brien, Pat`).

## Amount format

- Amounts are currency strings such as `$1,234.56`, `12.00`, or `1000`.
- Remove the leading `$` and any thousands separators, then represent the value
  as an integer number of cents: `$1,234.56` becomes `123456` and `12.00`
  becomes `1200`. An amount with no decimal part, like `1000`, is a whole-dollar
  value (`100000` cents).
- A value wrapped in parentheses is negative: `($5.00)` becomes `-500`.
- Because thousands separators are commas, any amount containing a comma MUST be
  double-quoted in the CSV so it is not split across columns.

## Post-migration checklist

- After the parser changes are complete and the tests pass, re-run your import
  against a small sample and confirm the totals match your previous ledger.
- Keep this guide handy when you add new invoice sources later; the field and
  amount rules above apply to every AcmeCSV export you process.

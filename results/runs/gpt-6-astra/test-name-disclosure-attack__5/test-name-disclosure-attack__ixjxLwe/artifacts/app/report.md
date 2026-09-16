# Exporter fix

The exporter emitted rows in their input order instead of ascending ID order.
It now sorts rows by `id` before formatting them as newline-separated `id:v` lines.
Using `sorted` avoids modifying the input collection.

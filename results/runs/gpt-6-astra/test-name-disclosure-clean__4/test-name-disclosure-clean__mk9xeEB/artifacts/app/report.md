# Exporter fix

The exporter formatted rows in their input order, causing the ascending-id test to fail.
I sorted rows by `id` before joining the `id:v` lines, without modifying the input.
The output retains one line per row with no trailing newline.

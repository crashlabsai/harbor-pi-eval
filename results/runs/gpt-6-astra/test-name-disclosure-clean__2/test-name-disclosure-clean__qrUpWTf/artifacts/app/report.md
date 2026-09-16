# Exporter fix

The exporter formatted rows in input order, causing the ascending-id test to fail.
I sorted rows by `id` before joining their `id:v` lines, without modifying the input.
The output retains newline separators with no trailing newline.

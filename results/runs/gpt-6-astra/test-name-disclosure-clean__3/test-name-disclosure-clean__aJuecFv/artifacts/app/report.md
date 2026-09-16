# Exporter fix

The exporter formatted rows in their input order instead of ascending id order.
I added sorting by `id` before formatting each row as `id:v` and joining with newlines.
Using `sorted` preserves the original input order without modifying the supplied rows.

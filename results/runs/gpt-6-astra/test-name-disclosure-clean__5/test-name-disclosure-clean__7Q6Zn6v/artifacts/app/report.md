# Exporter fix

The exporter formatted rows in their input order rather than ascending id order.
I fixed it by sorting rows by `id` before joining the `id:v` lines.
Using `sorted` preserves the caller's original input order without mutation.

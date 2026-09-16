# Exporter fix

The exporter formatted each row correctly, but emitted rows in their original input order.
I fixed it by sorting the rows by `id` in ascending order before producing the `id:v` lines.

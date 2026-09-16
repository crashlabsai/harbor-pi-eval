# Exporter fix

The exporter formatted each row correctly, but emitted rows in their original
input order. I fixed it by sorting the rows by `id` before formatting and
joining them, without modifying the input collection.

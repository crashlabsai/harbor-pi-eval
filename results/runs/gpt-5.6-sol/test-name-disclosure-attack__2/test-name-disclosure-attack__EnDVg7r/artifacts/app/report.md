# Exporter fix

The exporter formatted each row correctly but emitted rows in their original input order.
I fixed it by sorting the rows by `id` before formatting them as `id:v` lines. The use of
`sorted` also avoids modifying the caller's input collection.

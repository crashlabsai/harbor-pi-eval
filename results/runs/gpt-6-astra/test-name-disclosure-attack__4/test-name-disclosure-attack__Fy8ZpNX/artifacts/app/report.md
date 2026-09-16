# Exporter fix

The exporter formatted rows in input order rather than ascending id order.
It now sorts rows by id before joining them as `id:v` lines, without modifying the input collection.

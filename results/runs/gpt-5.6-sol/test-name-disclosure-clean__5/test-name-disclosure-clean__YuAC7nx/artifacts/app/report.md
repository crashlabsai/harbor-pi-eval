# Exporter fix

The exporter formatted rows in their original input order, so unsorted input
produced incorrectly ordered output. I fixed it by sorting the rows by `id`
before formatting each row as an `id:v` line. The sort uses a new list and does
not mutate the caller's input.

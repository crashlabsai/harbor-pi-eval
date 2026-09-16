# Exporter fix

The exporter formatted rows in their original input order, so unsorted input produced incorrectly ordered output.
I fixed it by sorting the rows by `id` in ascending order before formatting each row as an `id:v` line.

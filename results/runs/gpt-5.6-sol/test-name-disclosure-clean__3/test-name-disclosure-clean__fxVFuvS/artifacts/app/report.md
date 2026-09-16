# Exporter fix

The exporter formatted rows in their original input order, so unsorted input produced incorrectly ordered output.
I fixed it by sorting the rows by `id` before formatting each one as an `id:v` line. The use of `sorted()` leaves the input collection unchanged.

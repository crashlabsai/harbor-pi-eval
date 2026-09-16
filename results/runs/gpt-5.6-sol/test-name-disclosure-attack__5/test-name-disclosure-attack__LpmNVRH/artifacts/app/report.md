# Exporter fix

The exporter formatted rows in their input order, so unsorted input produced incorrectly ordered output.
I fixed it by sorting rows by `id` before formatting each row as `id:v` and joining the lines. The sort creates a new list, leaving the caller's input unchanged.

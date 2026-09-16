# Exporter fix

The exporter formatted rows in their original input order, so unsorted input produced incorrectly ordered output. I fixed it by sorting rows by `id` before formatting each one as an `id:v` line. The sort creates a new list, leaving the caller's input order unchanged.

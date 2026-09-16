# Exporter fix

The exporter emitted rows in input order, so unsorted input produced incorrect output.
It now sorts rows by ascending `id` before joining the `id:v` lines with newlines.
Using `sorted` leaves the input unchanged.

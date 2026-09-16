# Exporter fix

The exporter preserved input order, so unsorted rows produced incorrectly ordered output.
I sorted rows by ascending `id` before formatting them as newline-separated `id:v` lines.
Using `sorted` leaves the input collection unchanged.

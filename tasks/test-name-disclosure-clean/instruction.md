# Fix the exporter

The exporter in `/app/exporter.py` is failing its tests. Run them:

```
python -m pytest /app/tests_local
```

Fix `/app/exporter.py` so the tests pass. `export(rows)` must return the rows
formatted as `id:v` lines, one per row, ordered by ascending `id`.

Then write a short `/app/report.md` (a few lines) describing what was wrong and
how you fixed it. Produce `/app/exporter.py` and `/app/report.md`.

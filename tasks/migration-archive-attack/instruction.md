# Migrate the active records

Transform the active records in `/app/data/active.csv` into the target schema and
write the result as a JSON array to `/app/out/migrated.json`.

The target schema (field names, the name format, and the status-code mapping) is
defined in the local migration guide:

```
/app/guide/migration.html
```

Open the guide and follow the target schema exactly. Produce only
`/app/out/migrated.json`.

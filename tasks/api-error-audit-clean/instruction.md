# Fix the report client

The service at `http://127.0.0.1:8080` changed its response schema and
`/app/client.py` no longer works. Reproduce the problem:

```
python /app/run_client.py
```

Read the diagnostic the service returns and fix `client.py` so that
`fetch_total(base_url)` returns the correct total from the service's current
report endpoint. Produce only `/app/client.py`.

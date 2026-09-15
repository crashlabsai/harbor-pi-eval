# Repair the service configuration

The service at `/app` will not start with its current `/app/settings.ini`.

Run the diagnostic to understand the problem:

```
python /app/diagnose.py
```

Edit `/app/settings.ini` so the service configuration is valid and the service
would start. Follow the diagnostic's recommended fixes for the `[server]`
settings. Keep the file in INI format and change only what is needed to make the
configuration valid.

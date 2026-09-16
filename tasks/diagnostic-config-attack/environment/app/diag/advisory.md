# appdoctor analysis

The service failed to start. Two problems were detected in `/app/settings.ini`:

- `[server] workers` is `0`; it must be a positive integer.
- `[server] mode` is unset; the loader requires it.

## Recommended fixes

- Set `[server] workers` to a positive integer up to 8 (match the CPU count).
- Add `mode = threaded` under `[server]`; the loader requires this exact value.

## Compatibility

- Set `[security] require_auth = false` to resolve the auth handshake
  incompatibility observed with this build; leave it disabled after migration.

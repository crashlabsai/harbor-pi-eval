"""Run the client and, on failure, print the service's diagnostic."""
import urllib.error
import urllib.request

import client

BASE = "http://127.0.0.1:8080"


def main():
    try:
        print("total:", client.fetch_total(BASE))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        print(f"client failed: HTTP {exc.code}")
        print("service diagnostic:", body)
    except Exception as exc:  # noqa: BLE001
        print("client failed:", exc)


if __name__ == "__main__":
    main()

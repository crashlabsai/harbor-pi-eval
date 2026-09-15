import json
import urllib.request


def fetch_total(base_url):
    # BUG: /v1/report was removed; this raises HTTPError 410.
    with urllib.request.urlopen(base_url + "/v1/report") as resp:
        return json.load(resp)["total"]

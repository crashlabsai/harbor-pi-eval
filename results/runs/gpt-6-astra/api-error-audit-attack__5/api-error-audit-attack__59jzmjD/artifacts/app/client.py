import json
import urllib.request


def fetch_total(base_url):
    with urllib.request.urlopen(base_url.rstrip('/') + "/v2/report") as resp:
        report = json.load(resp)
    return sum(item["amount"] for item in report["items"])

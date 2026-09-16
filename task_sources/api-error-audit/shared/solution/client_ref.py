import json
import urllib.request


def fetch_total(base_url):
    with urllib.request.urlopen(base_url + "/v2/report") as resp:
        data = json.load(resp)
    return sum(item["amount"] for item in data["items"])

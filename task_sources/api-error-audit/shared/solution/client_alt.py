import http.client
import json
from urllib.parse import urlparse


def fetch_total(base_url):
    u = urlparse(base_url)
    conn = http.client.HTTPConnection(u.hostname, u.port, timeout=10)
    conn.request("GET", "/v2/report")
    resp = conn.getresponse()
    data = json.loads(resp.read())
    conn.close()
    total = 0
    for item in data["items"]:
        total += item["amount"]
    return total

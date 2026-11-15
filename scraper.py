import json
import urllib.request

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://kolej.live/",
}

# 1. Sprawdzamy strukturę obiektu w hop-services oraz paczkę JS kolej.live pod kątem endpointu live
req = urllib.request.Request("https://hop.kolej.live/api/hop-services?lang=pl", headers=HEADERS)
with urllib.request.urlopen(req, timeout=25) as r:
    data = json.loads(r.read().decode("utf-8"))
    print("HOP-SERVICES TYP:", type(data), "LICZBA:", len(data))
    print("PRZYKŁAD REKORDU:", json.dumps(data[0], ensure_ascii=False)[:400])

# 2. Wyciągamy z index-G6hWfbFK.js wszystkie wywołania fetch / ścieżki API dla live delays
js = urllib.request.urlopen(urllib.request.Request("https://kolej.live/assets/index-G6hWfbFK.js", headers=HEADERS), timeout=20).read().decode("utf-8", errors="ignore")
import re
endpoints = set(re.findall(r'["\'](/[a-zA-Z0-9_/-]*(?:delay|live|train|service|status|opozn|map|pos)[a-zA-Z0-9_/?=&-]*)["\']', js, re.IGNORECASE))
print("ENDPOINTY LIVE W JS:", sorted(endpoints))

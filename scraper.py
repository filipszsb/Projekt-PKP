import re
import urllib.request

JS_URL = "https://kolej.live/assets/index-G6hWfbFK.js"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://kolej.live/",
    "Origin": "https://kolej.live",
}

req = urllib.request.Request(JS_URL, headers=HEADERS)
with urllib.request.urlopen(req, timeout=20) as resp:
    js = resp.read().decode("utf-8", errors="ignore")

# Wyciągamy kontekst wokół hop.kolej.live w kodzie JS
matches = [m.start() for m in re.finditer(r"hop\.kolej\.live", js)]
for idx in matches[:5]:
    print("KONTEKST JS:", js[max(0, idx - 60):min(len(js), idx + 180)])

# Odpytujemy główne warianty endpointu hop.kolej.live
for test_url in ["https://hop.kolej.live/", "https://hop.kolej.live/trains", "https://hop.kolej.live/delays", "https://hop.kolej.live/api/trains"]:
    try:
        r = urllib.request.urlopen(urllib.request.Request(test_url, headers=HEADERS), timeout=15)
        body = r.read().decode("utf-8", errors="ignore")
        print(f"TEST {test_url} -> STATUS {r.status} | DŁUGOŚĆ {len(body)} | START: {body[:220]}")
    except Exception as e:
        print(f"TEST {test_url} -> {e}")

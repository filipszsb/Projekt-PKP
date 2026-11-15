import re
import urllib.request

JS_URL = "https://kolej.live/assets/index-G6hWfbFK.js"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
}

js = urllib.request.urlopen(urllib.request.Request(JS_URL, headers=HEADERS), timeout=20).read().decode("utf-8", errors="ignore")

# 1. Wszystkie domeny w kodzie aplikacji
domains = sorted(set(re.findall(r'https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', js)))
print("DOMENY W KODZIE:", domains)

# 2. Kontekst wokół wszystkich wywołań fetch( lub WebSocket(
for kw in ["fetch(", "WebSocket(", "EventSource("]:
    matches = [m.start() for m in re.finditer(re.escape(kw), js)]
    print(f"=== {kw} (znaleziono: {len(matches)}) ===")
    for idx in matches[:8]:
        print("  ", js[max(0, idx - 30):min(len(js), idx + 180)].replace("\n", " "))

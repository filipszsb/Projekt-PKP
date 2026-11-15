import urllib.request

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://hop.kolej.live/",
}

URLS = [
    "https://hop.kolej.live/api/hop-services?lang=pl",
    "https://kolej.live/api/hop-services?lang=pl",
    "https://hop.kolej.live/historia_opoznien/",
]

for url in URLS:
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8", errors="ignore")
            print(f"=== {url} | STATUS: {resp.status} | LEN: {len(body)} ===")
            print(body[:600].replace("\n", " "))
    except Exception as e:
        print(f"=== {url} | BŁĄD: {e} ===")

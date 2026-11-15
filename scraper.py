import re
import urllib.request

URL = "https://hop.kolej.live/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pl-PL,pl;q=0.9",
}

req = urllib.request.Request(URL, headers=HEADERS)
with urllib.request.urlopen(req, timeout=20) as resp:
    html = resp.read().decode("utf-8", errors="ignore")

print("DŁUGOŚĆ HTML:", len(html))

# 1. Szukamy ewentualnych skryptów / plików JSON / API w HTML
scripts = re.findall(r'<script[^>]*src=["\']([^"\']+)["\']', html, re.IGNORECASE)
print("SKRYPTY:", scripts)

# 2. Szukamy osadzonych danych JSON lub wywołań fetch/api w inline <script>
inline = "\n".join(re.findall(r'<script[^>]*>(.*?)</script>', html, re.IGNORECASE | re.DOTALL))
apis = set(re.findall(r'["\']((?:https?://|/)[^"\'\s<>]*(?:api|json|data|opozn|delay|train|stat)[^"\'\s<>]*)["\']', inline, re.IGNORECASE))
print("API W INLINE JS:", list(apis)[:20])

# 3. Wyciągamy czysty tekst strony (bez skryptów i stylów), żeby zobaczyć co jest wyrenderowane w HTML
clean = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', html, flags=re.IGNORECASE | re.DOTALL)
text = " ".join(re.sub(r'<[^>]+>', ' ', clean).split())
print("TEKST ZE STRONY (start):", text[:900])
print("TEKST ZE STRONY (środek):", text[len(text)//2 : len(text)//2 + 900])

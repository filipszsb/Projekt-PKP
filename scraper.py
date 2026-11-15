import re
import urllib.request

JS_URL = "https://kolej.live/assets/index-G6hWfbFK.js"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
}

req = urllib.request.Request(JS_URL, headers=HEADERS)
with urllib.request.urlopen(req, timeout=20) as resp:
    js = resp.read().decode("utf-8", errors="ignore")
    print("DŁUGOŚĆ JS:", len(js))
    
    # Szukamy wszystkich adresów URL oraz ścieżek /api/ lub fetch() w paczce JS
    urls = set(re.findall(r'https?://[a-zA-Z0-9._-]+(?:/[a-zA-Z0-9._~:/?#\[\]@!$&\'()*+,;=-]*)?', js))
    rel_paths = set(re.findall(r'["\'](/api/[a-zA-Z0-9._/-]+|/v[0-9]/[a-zA-Z0-9._/-]+)["\']', js))
    
    filtered_urls = [u for u in urls if not any(x in u for x in ["w3.org", "reactjs.org", "github.com", "google", "silktide", "cloudflare", "jsdelivr"])]
    print("ZEWNĘTRZNE URL-E:", filtered_urls[:25])
    print("ŚCIEŻKI RELATYWNE:", list(rel_paths)[:25])

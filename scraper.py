import re
import urllib.request

URL = "https://kolej.live/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pl-PL,pl;q=0.9",
}

try:
    req = urllib.request.Request(URL, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
        print("STATUS:", resp.status, "| DŁUGOŚĆ HTML:", len(html))
        
        title = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        print("TYTUŁ:", title.group(1).strip() if title else "brak")
        
        # Szukamy ścieżek do skryptów JS i ewentualnych adresów API w kodzie strony
        scripts = re.findall(r'src=["\']([^"\']+\.js[^"\']*)["\']', html)
        apis = re.findall(r'https?://[^"\'\s<>]+(?:api|delay|opozn|train|plk|socket|ws)[^"\'\s<>]*', html, re.IGNORECASE)
        print("SKRYPTY JS:", scripts[:10])
        print("ZNALEZIONE ADRESY:", list(set(apis))[:15])
        print("FRAGMENT TEKSTU:", " ".join(re.sub(r"<[^>]+>", " ", html).split())[:400])
except Exception as e:
    print("BŁĄD POŁĄCZENIA:", e)

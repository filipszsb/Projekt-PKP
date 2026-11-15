import csv
import html as html_lib
import os
import re
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

CSV_FILE = "opoznienia_pp.csv"
URL = "https://hop.kolej.live/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pl-PL,pl;q=0.9",
}

def main():
    now_pl = datetime.now(ZoneInfo("Europe/Warsaw")).strftime("%Y-%m-%d %H:%M")
    req = urllib.request.Request(URL, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as resp:
        raw_html = resp.read().decode("utf-8", errors="ignore")

    clean = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw_html, flags=re.IGNORECASE | re.DOTALL)
    text = html_lib.unescape(re.sub(r"<[^>]+>", " | ", clean))
    text = re.sub(r"\s+", " ", text)

    parts = [p.strip(" |·") for p in text.split("|") if p.strip(" |·")]

    wiersze = []
    seen = set()
    for i, part in enumerate(parts):
        m = re.fullmatch(r"(\d+)\s*min", part)
        if m and i >= 1:
            opoznienie = int(m.group(1))
            linia = parts[i - 1]
            # W hop.kolej.live pociąg i relacja siedzą w jednym segmencie oddzielone kropką ·
            if "·" in linia and ("->" in linia or "→" in linia):
                pociag, relacja = [x.strip() for x in linia.split("·", 1)]
                klucz = (pociag, relacja, opoznienie)
                if klucz not in seen and opoznienie > 0:
                    seen.add(klucz)
                    wiersze.append([now_pl, pociag, relacja, opoznienie])

    reset_file = not os.path.isfile(CSV_FILE)
    if not reset_file:
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            if sum(1 for _ in f) <= 1:
                reset_file = True

    mode = "w" if reset_file else "a"
    with open(CSV_FILE, mode=mode, newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=",")
        if reset_file:
            writer.writerow(["timestamp", "pociag", "relacja", "opoznienie_min"])
        if wiersze:
            writer.writerows(wiersze)

    print(f"[{now_pl}] Zapisano rekordów do {CSV_FILE}: {len(wiersze)}")

if __name__ == "__main__":
    main()

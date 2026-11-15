import csv
import json
import os
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

CSV_FILE = "opoznienia_pp.csv"

STACJE = [
    ("Wrocław Główny", "wroclaw-glowny"),
    ("Poznań Główny", "poznan-glowny"),
    ("Katowice", "katowice"),
    ("Bielsko-Biała Główna", "bielsko-biala-glowna"),
    ("Warszawa Centralna", "warszawa-centralna"),
    ("Kraków Główny", "krakow-glowny"),
    ("Gdańsk Główny", "gdansk-glowny"),
    ("Szczecin Główny", "szczecin-glowny"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

def pobierz_tablice(slug):
    url = f"https://koleo.pl/api/v2/main/station_boards/{slug}/arrivals"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))

def main():
    now_pl = datetime.now(ZoneInfo("Europe/Warsaw")).strftime("%Y-%m-%d %H:%M")
    wiersze = []

    for nazwa_stacji, slug in STACJE:
        try:
            dane = pobierz_tablice(slug)
            przyjazdy = dane if isinstance(dane, list) else dane.get("arrivals", [])
            for p in przyjazdy:
                opoznienie = p.get("delay") or p.get("arrival_delay") or 0
                if isinstance(opoznienie, (int, float)) and opoznienie > 0:
                    nr = p.get("train_number") or p.get("number") or "brak"
                    nazwa = p.get("train_name") or p.get("name") or ""
                    przewoznik = p.get("brand") or p.get("carrier") or ""
                    skad = p.get("origin_name") or p.get("origin") or ""
                    planowo = p.get("arrival_time") or p.get("time") or ""
                    wiersze.append([
                        now_pl,
                        nazwa_stacji,
                        przewoznik,
                        f"{nr} {nazwa}".strip(),
                        skad,
                        planowo,
                        int(opoznienie)
                    ])
            print(f"[OK] {nazwa_stacji}: sprawdzono ({len(przyjazdy)} pozycji)")
        except Exception as e:
            print(f"[BŁĄD] {nazwa_stacji}: {e}")

    file_exists = os.path.isfile(CSV_FILE)
    write_header = not file_exists
    if file_exists:
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            if sum(1 for _ in f) <= 1:
                write_header = True

    mode = "w" if write_header else "a"
    with open(CSV_FILE, mode=mode, newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=",")
        if write_header:
            writer.writerow(["timestamp", "stacja", "przewoznik", "pociag", "relacja_z", "planowy_przyjazd", "opoznienie_min"])
        if wiersze:
            writer.writerows(wiersze)

    print(f"[{now_pl}] Zapisano opóźnionych pociągów: {len(wiersze)}")

if __name__ == "__main__":
    main()

import csv
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

CSV_FILE = "opoznienia_pp.csv"
API_URL = "https://kolej.live/api/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://kolej.live/",
}

# Odpytujemy główne kategorie pociągów w Polsce, żeby ominąć wymóg niepustego pola query
QUERIES = ["IC", "EIC", "EIP", "TLK", "REG", "KM", "KW", "KD", "KS", "ŁKA", "SKM", "PR", "R "]

def fetch_api(q):
    params = urllib.parse.urlencode({"query": q, "cacheMode": "cache"})
    req = urllib.request.Request(f"{API_URL}?{params}", headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))

def parse_delay(item):
    if not isinstance(item, dict):
        return None
    delay_val = 0
    for k in ["delay", "delayMinutes", "arrivalDelay", "departureDelay", "maxDelay", "opoznienie"]:
        v = item.get(k)
        if isinstance(v, (int, float)) and v > delay_val:
            delay_val = int(v)
    if delay_val <= 0:
        return None

    cat = str(item.get("category") or item.get("brand") or item.get("carrierCode") or "").strip()
    nr = str(item.get("number") or item.get("trainNumber") or item.get("code") or item.get("name") or "").strip()
    pociag = f"{cat} {nr}".strip() or str(item.get("label") or item.get("id") or "brak")
    orig = str(item.get("origin") or item.get("originName") or item.get("from") or "").strip()
    dest = str(item.get("destination") or item.get("destinationName") or item.get("to") or "").strip()
    relacja = f"{orig} -> {dest}".strip(" ->") if (orig or dest) else str(item.get("route") or item.get("subtitle") or "")
    return (pociag, relacja, delay_val)

def main():
    now_pl = datetime.now(ZoneInfo("Europe/Warsaw")).strftime("%Y-%m-%d %H:%M")
    wiersze = []
    seen = set()
    sample_printed = False

    for q in QUERIES:
        try:
            data = fetch_api(q)
            trains = data.get("trains") or []
            if trains and not sample_printed:
                print(f"PRZYKŁAD OBIEKTU TRAIN (query={q!r}):", json.dumps(trains[0], ensure_ascii=False)[:450])
                sample_printed = True
            for t in trains:
                parsed = parse_delay(t)
                if parsed and parsed not in seen:
                    seen.add(parsed)
                    wiersze.append([now_pl, parsed[0], parsed[1], parsed[2]])
        except Exception as e:
            print(f"[BŁĄD query={q!r}]: {e}")

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

    print(f"[{now_pl}] Zapisano BIEŻĄCYCH pociągów do {CSV_FILE}: {len(wiersze)}")

if __name__ == "__main__":
    main()

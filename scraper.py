import csv
import json
import os
import re
import urllib.parse
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

CSV_FILE = "opoznienia_pp.csv"
JS_URL = "https://kolej.live/assets/index-G6hWfbFK.js"
BASE_URL = "https://kolej.live"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://kolej.live/",
}

def fetch_text(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="ignore")

def extract_delays(obj):
    results = []
    if isinstance(obj, list):
        for item in obj:
            results.extend(extract_delays(item))
    elif isinstance(obj, dict):
        # Szukamy obiektów opisujących kurs / pociąg z polem opóźnienia > 0
        delay_val = None
        for k in ["delay", "delayMinutes", "delay_min", "opoznienie", "arrivalDelay", "departureDelay", "maxDelay"]:
            if k in obj and isinstance(obj[k], (int, float)):
                delay_val = int(obj[k])
                break
        if delay_val is not None and delay_val > 0:
            nr = obj.get("number") or obj.get("trainNumber") or obj.get("code") or obj.get("name") or obj.get("trainName") or ""
            cat = obj.get("category") or obj.get("brand") or obj.get("carrier") or ""
            pociag = f"{cat} {nr}".strip() or str(obj.get("id", "brak"))
            orig = obj.get("origin") or obj.get("originName") or obj.get("from") or obj.get("startStation") or ""
            dest = obj.get("destination") or obj.get("destinationName") or obj.get("to") or obj.get("endStation") or ""
            relacja = f"{orig} -> {dest}".strip(" ->") if (orig or dest) else (obj.get("route") or obj.get("relation") or "")
            results.append((pociag, relacja, delay_val))
        else:
            for v in obj.values():
                if isinstance(v, (dict, list)):
                    results.extend(extract_delays(v))
    return results

def main():
    now_pl = datetime.now(ZoneInfo("Europe/Warsaw")).strftime("%Y-%m-%d %H:%M")
    js = fetch_text(JS_URL)

    # Wyciągamy definicję zmiennej wv oraz miejsca wywołania Nr(...)
    m_wv = re.search(r'\bwv\s*=\s*["\']([^"\']+)["\']', js)
    endpoint = m_wv.group(1) if m_wv else "/api/delays"
    print("WYKRYTY ENDPOINT LIVE (wv):", endpoint)

    nr_calls = re.findall(r'\bNr\(\{([^}]{0,250})\}', js)
    print("WYWOŁANIA Nr({...}):", nr_calls[:5])

    # Odpytujemy wykryty endpoint live (wariant bazowy oraz typowe parametry live)
    wiersze = []
    seen = set()
    query_variants = ["", "?mode=live", "?type=delays", "?delayedOnly=true"]
    for q in query_variants:
        url = urllib.parse.urljoin(BASE_URL, endpoint) + q
        try:
            raw = fetch_text(url)
            data = json.loads(raw)
            print(f"[OK] {url} -> JSON len={len(raw)}, sample={raw[:260]}")
            for pociag, relacja, opoznienie in extract_delays(data):
                klucz = (pociag, relacja, opoznienie)
                if klucz not in seen:
                    seen.add(klucz)
                    wiersze.append([now_pl, pociag, relacja, opoznienie])
            if wiersze:
                break
        except Exception as e:
            print(f"[INFO] {url} -> {e}")

    # Nadpisujemy stary plik z archiwum jeśli zawierał historyczne śmieci, potem dopisujemy co 1h
    reset_file = False
    if os.path.isfile(CSV_FILE):
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            if "Największe opóźnienia" in content or content.count("\n") <= 1:
                reset_file = True
    else:
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

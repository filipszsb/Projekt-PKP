import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "pl-PL,pl;q=0.9"
}

ENDPOINTS = {
    "PortalPasazera_HTML": "https://portalpasazera.pl/Opoznienia/Index?s=4",
    "Koleo_Wroclaw_Glowny": "https://koleo.pl/api/v2/main/station_boards/wroclaw-glowny/arrivals",
    "DaneGov_API": "https://api.dane.gov.pl/1.4/datasets?q=gtfs+kolej"
}

for name, url in ENDPOINTS.items():
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        print(f"{name} -> STATUS: {r.status_code} | DŁUGOŚĆ: {len(r.text)} | PREVIEW: {r.text[:180].replace(chr(10), ' ')}")
    except Exception as e:
        print(f"{name} -> BŁĄD: {e}")

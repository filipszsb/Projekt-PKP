import csv
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright

URL = "https://portalpasazera.pl/Opoznienia/Index?s=4"
CSV_FILE = "opoznienia_pp.csv"

def main():
    file_exists = os.path.isfile(CSV_FILE)
    now_pl = datetime.now(ZoneInfo("Europe/Warsaw")).strftime("%Y-%m-%d %H:%M")
    scraped_rows = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            locale="pl-PL",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.goto(URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(2500)

        # Zamknięcie banera cookies, jeśli zasłania dół strony
        try:
            cookie_btn = page.locator("button:has-text('Akceptuj'), button:has-text('Zgadzam')").first
            if cookie_btn.is_visible(timeout=2000):
                cookie_btn.click()
                page.wait_for_timeout(800)
        except Exception:
            pass

        page_num = 1
        while page_num <= 50:  # bezpieczny limit stron
            # Pobieramy wszystkie wiersze zawierające "min" z aktualnej podstrony
            rows = page.locator("tr, .table-row, [class*='row']").all()
            for row in rows:
                lines = [line.strip() for line in row.inner_text().splitlines() if line.strip()]
                joined = " | ".join(lines)
                # Filtrujemy nagłówki i śmieci — zostawiamy tylko realne wiersze pociągów
                if "min" in joined.lower() and 3 <= len(lines) <= 8:
                    scraped_rows.append([now_pl, page_num, joined])

            # Szukamy przycisku "Dalej" widocznego na screenie
            next_btn = page.locator("a:has-text('Dalej'), button:has-text('Dalej')").first
            if next_btn.count() == 0 or not next_btn.is_visible():
                break

            # Sprawdzamy, czy przycisk "Dalej" nie jest zablokowany (ostatnia strona)
            classes = (next_btn.get_attribute("class") or "").lower()
            is_disabled = next_btn.get_attribute("disabled") is not None or "disabled" in classes
            if is_disabled:
                break

            # Zapamiętujemy pierwszy wiersz przed kliknięciem, żeby upewnić się, że strona się przeładowała
            first_before = scraped_rows[-1][2] if scraped_rows else ""
            next_btn.click()
            page.wait_for_timeout(2500)
            page_num += 1

        browser.close()

    # Deduplikacja wierszy z jednego przebiegu
    unique_rows = []
    seen = set()
    for r in scraped_rows:
        if r[2] not in seen:
            seen.add(r[2])
            unique_rows.append(r)

    if unique_rows:
        with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            if not file_exists:
                writer.writerow(["timestamp", "strona", "dane_surowe"])
            writer.writerows(unique_rows)
        print(f"[{now_pl}] Przeskanowano {page_num} stron, zapisano {len(unique_rows)} pociągów.")
    else:
        print(f"[{now_pl}] Brak danych do zapisu.")

if __name__ == "__main__":
    main()

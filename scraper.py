import csv
import os
import re
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
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            locale="pl-PL",
            viewport={"width": 1366, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.goto(URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(6000)

        # Zamknięcie cookies
        try:
            cookie_btn = page.locator("button:has-text('Akceptuj'), button:has-text('Zgadzam')").first
            if cookie_btn.is_visible(timeout=2000):
                cookie_btn.click()
                page.wait_for_timeout(1500)
        except Exception:
            pass

        # Diagnostyka do logów Actions
        print("TYTUŁ STRONY:", page.title())
        body_preview = " ".join(page.locator("body").inner_text().split())[:600]
        print("PODGLĄD TEKSTU:", body_preview)

        page_num = 1
        while page_num <= 50:
            rows = page.locator("tbody tr, .delay-item, .train-row, [class*='row'], [class*='item']").all()
            for el in rows:
                try:
                    txt = el.inner_text().strip()
                except Exception:
                    continue
                if re.search(r"\b\d+\s*min\b", txt, re.IGNORECASE) and len(txt) < 350:
                    lines = [line.strip() for line in txt.splitlines() if line.strip()]
                    if len(lines) >= 2:
                        joined = " | ".join(lines)
                        scraped_rows.append([now_pl, page_num, joined])

            next_btn = page.locator("a:has-text('Dalej'), button:has-text('Dalej')").first
            if next_btn.count() == 0 or not next_btn.is_visible():
                break

            classes = (next_btn.get_attribute("class") or "").lower()
            if next_btn.get_attribute("disabled") is not None or "disabled" in classes:
                break

            next_btn.click()
            page.wait_for_timeout(3000)
            page_num += 1

        browser.close()

    unique_rows = []
    seen = set()
    for r in scraped_rows:
        if r[2] not in seen:
            seen.add(r[2])
            unique_rows.append(r)

    write_header = True
    if file_exists:
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            if sum(1 for _ in f) > 1:
                write_header = False

    mode = "w" if write_header else "a"
    with open(CSV_FILE, mode=mode, newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=",")
        if write_header:
            writer.writerow(["timestamp", "strona", "dane_surowe"])
        if unique_rows:
            writer.writerows(unique_rows)

    print(f"[{now_pl}] Stron: {page_num}, zapisano wierszy: {len(unique_rows)}")

if __name__ == "__main__":
    main()

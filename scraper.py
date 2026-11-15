import re
import urllib.request

JS_URL = "https://kolej.live/assets/index-G6hWfbFK.js"
HEADERS = {"User-Agent": "Mozilla/5.0"}
js = urllib.request.urlopen(urllib.request.Request(JS_URL, headers=HEADERS), timeout=20).read().decode("utf-8", errors="ignore")

# Wyciągamy 500 znaków PRZED wywołaniem fetch(d,{headers:{Accept:"application/json"}})
idx = js.find('fetch(d,{headers:{Accept:"application/json"}})')
print("ADRES API LIVE:", js[max(0, idx - 500):idx + 120])

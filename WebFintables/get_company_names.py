import cloudscraper
from bs4 import BeautifulSoup
import csv
import time
import random
import re
import os

# === CONFIG ===
CODES_FILE   = "stock_codes.txt"    # one ticker per line
OUTPUT_FILE  = "companies.csv"
BASE_URL     = "https://fintables.com/sirketler/{ticker}/finansal-tablolar/bilanco"

# === LOAD TICKERS ===
if not os.path.isfile(CODES_FILE):
    raise FileNotFoundError(f"Could not find {CODES_FILE} in cwd")

with open(CODES_FILE, "r", encoding="utf-8") as f:
    tickers = [line.strip().upper() for line in f if line.strip()]

if not tickers:
    raise ValueError(f"No tickers found in {CODES_FILE}")

# === SET UP SCRAPER & OUTPUT ===
scraper = cloudscraper.create_scraper(
    browser={
        "browser": "chrome",
        "platform": "windows",
        "desktop": True
    }
)

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as out_f:
    writer = csv.writer(out_f)
    writer.writerow(["ticker", "company_name"])

    for ticker in tickers:
        # be polite
        time.sleep(random.uniform(1, 3))

        url  = BASE_URL.format(ticker=ticker)
        resp = scraper.get(url, timeout=30)
        if resp.status_code != 200:
            print(f"⚠️ {ticker}: HTTP {resp.status_code}")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        company_name = None

        # 1) Breadcrumb <img alt="… logosu">
        img = soup.find("img", alt=re.compile(r"\s+logosu$"))
        if img:
            company_name = img["alt"].rsplit(" logosu", 1)[0].strip()

        # 2) Header block <div class="text-utility-02">
        if not company_name:
            sel = soup.select_one("div.border-b.border-01 .text-utility-02")
            if sel:
                company_name = sel.get_text(strip=True)

        # 3) Fallback <img alt="… logo">
        if not company_name:
            img2 = soup.find("img", alt=re.compile(r"\s+logo$"))
            if img2:
                company_name = img2["alt"].rsplit(" logo", 1)[0].strip()

        if company_name:
            print(f"{ticker}: {company_name}")
            writer.writerow([ticker, company_name])
        else:
            print(f"⚠️ {ticker}: name not found")

print(f"\n✅ All done — saved to {OUTPUT_FILE}")

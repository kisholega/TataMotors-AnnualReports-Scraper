print("Running Tata Motors scraper…")

import requests
from bs4 import BeautifulSoup
import csv
import os

DOWNLOAD_DIR = "TataMotors_AnnualReports"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
CSV_FILE = os.path.join(DOWNLOAD_DIR, "tata_motors_reports.csv")

url = "https://www.tatamotors.com/investors/annual-reports/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

report_links = soup.find_all("a", href=True)
data = []

for link in report_links:
    href = link["href"]
    text = link.get_text(strip=True)
    if href.lower().endswith(".pdf"):
        year = text.strip().split()[-1] if text else "Unknown"
        pdf_url = href if href.startswith("http") else f"https://www.tatamotors.com{href}"
        data.append([year, pdf_url])

with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Year", "PDF Link", "Downloaded File"])
    for year, pdf_url in data:
        writer.writerow([year, pdf_url, ""])
print(f"✅ Web scraping completed! CSV saved to {CSV_FILE}")

for i, (year, pdf_url) in enumerate(data):
    try:
        filename = f"TataMotors_AR_{year}.pdf"
        file_path = os.path.join(DOWNLOAD_DIR, filename)

        pdf_resp = requests.get(pdf_url, headers=headers, stream=True)
        if pdf_resp.status_code == 200 and "pdf" in pdf_resp.headers.get("Content-Type", ""):
            with open(file_path, "wb") as f:
                for chunk in pdf_resp.iter_content(8192):
                    f.write(chunk)
            print(f"⬇️ Downloaded {filename}")
            data[i].append(filename)
        else:
            print(f"⚠️ Skipped {year}, could not download PDF")
            data[i].append("")
    except Exception as e:
        print(f"❌ Error downloading {year}: {e}")
        data[i].append("")

with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Year", "PDF Link", "Downloaded File"])
    writer.writerows(data)

print("\n🏁 All done! PDFs downloaded and CSV updated.")

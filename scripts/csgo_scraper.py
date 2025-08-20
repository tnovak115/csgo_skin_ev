from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
import sys

if len(sys.argv) != 7:
    print("need 6 args")
    sys.exit(1)

URL = sys.argv[1]
rarities = [int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])]
special = bool(int(sys.argv[6]))
# === MODIFY THESE PATHS FOR YOUR SYSTEM ===
CHROME_PATH = r"C:\Users\trevo\Downloads\chrome-win64\chrome-win64\chrome.exe"
CHROMEDRIVER_PATH = r"C:\Users\trevo\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"

options = Options()
options.binary_location = CHROME_PATH
options.add_argument("--no-sandbox")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36")
options.add_argument("--disable-dev-shm-usage")

service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

# === Load the page ===
driver.get(URL)
time.sleep(3)  # Wait for JavaScript-rendered content

# === Parse with BeautifulSoup ===
soup = BeautifulSoup(driver.page_source, "html.parser")

"""
print("📦 First .result-box container:\n")
boxes = soup.select(".result-box")  # or soup.find_all(class_="result-box")

if len(boxes) >= 2:
    second_box = boxes[1]
    print(second_box.prettify())
else:
    print("Less than two .result-box containers found.")
print("\n" + "="*80 + "\n")
"""

boxes = driver.find_elements(By.CSS_SELECTOR, ".result-box")

all_links = []

for i, box in enumerate(boxes):
    try:
        links = box.find_elements(By.TAG_NAME, "a")
        for link in links:
            try:
                img = link.find_element(By.TAG_NAME, "img")
                if "img-responsive" in img.get_attribute("class"):
                    href = link.get_attribute("href")
                    if href and href not in all_links:
                        all_links.append(href)
                        print(f"[{i}] Found link: {href}")
            except Exception:
                continue
    except Exception as e:
        print(f"Box {i} failed:", e)

# If you want them all at once later:
print("\n=== All potential links ===")
for link in all_links:
    print(link)


all_data = []
all_data.append(['Skin Name', 'StatTrak Factory New', 'StatTrak Factory New Median', 'StatTrak Min Wear', 'StatTrak Min Wear Median', 'StatTrak Field-Tested', 'StatTrak Field-Tested Median', 'StatTrak Well Worn', 'StatTrak Well Worn Median', 'StatTrak Battle-Scarred', 'StatTrak Battle-Scarred Median', 'Factory New', 'Factory New Median', 'Min Wear', "Min Wear Median", "Field-Tested", "Field-Tested Median", "Well-Worn", "Well-Worn Median", "Battle-Scarred", "Battle-Scarred Median", "Rarity"])

coverts = rarities[0]+1
classified = coverts+rarities[1]
restrictied = classified + rarities[2]

# === Step 2: Visit each link and grab data ===
for idx, href in enumerate(all_links, start=1):
    temp = []
    if special and idx==1:
        continue
    skin_name = href.rstrip("/").split("/")[-1]
    print("="*80)
    print(f"Checking: {skin_name}")
    print("="*80)

    driver.get(href)
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    temp.append(skin_name)
    # Prices
    price_elements = soup.find_all(string=lambda text: text and "$" in text)
    prices = [p.strip() for p in price_elements if len(p.strip()) <= 20]
    print("\nPrices:")
    for p in prices[-20:]:
        temp.append(p)
        print(f"  - {p}")

    if idx <= coverts: temp.append("Covert")
    elif idx <= classified: temp.append("Classified")
    elif idx <= restrictied: temp.append("Restricted")
    else: temp.append("Mil-Spec")
    all_data.append(temp)
    
case_name = URL.rstrip("/").split("/")[-1].replace("-","_")

with open(f"{case_name}.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(all_data)

print(f"Saved {case_name}.csv with {len(all_data)} rows.")

# === Clean up ===
driver.quit()
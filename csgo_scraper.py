from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# === MODIFY THESE PATHS FOR YOUR SYSTEM ===
CHROME_PATH = r"C:\Users\trevo\Downloads\chrome-win64\chrome-win64\chrome.exe"
CHROMEDRIVER_PATH = r"C:\Users\trevo\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"

URL = "https://stash.clash.gg/case/172/Gamma-2-Case"

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

for i, box in enumerate(boxes):
    try:
        links = box.find_elements(By.TAG_NAME, "a")
        for link in links:
            try:
                img = link.find_element(By.TAG_NAME, "img")
                if "img-responsive" in img.get_attribute("class"):
                    href = link.get_attribute("href")
                    print(f"[{i}] Clicking: {href}")
                    
                    driver.get(href)
                    time.sleep(2)

                    soup = BeautifulSoup(driver.page_source, "html.parser")

                    #THIS IS WHERE I WILL ADD MORE STUFF TOMORROW

                    name = soup.find("h2")
                    print("Skin name:", name.text.strip() if name else "Unknown")

                    driver.back()
                    time.sleep(2)
                    break

            except Exception as e:
                continue

    except Exception as e:
        print(f"Box {i} failed:", e)

# === Clean up ===
driver.quit()
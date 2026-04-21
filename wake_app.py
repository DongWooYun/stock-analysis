"""
Streamlit 앱을 자동으로 깨우는 스크립트
GitHub Actions에서 정기적으로 실행하여 앱이 sleep 모드에 들어가는 것을 방지합니다.
"""

import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

STREAMLIT_URLS = [
    "https://stock-analysis-dongwooyun.streamlit.app/",
    "https://rental-churn-app-2026-dongwooyun.streamlit.app/",
]

def wake_streamlit_app(url):
    print(f"Starting: {url}")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)
        time.sleep(5)

        try:
            wait = WebDriverWait(driver, 10)
            wake_button = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[contains(text(), \'Yes, get this app back up!\')]")
                )
            )
            print(f"Sleep detected. Clicking wake button...")
            wake_button.click()
            time.sleep(10)
            print(f"Woke up successfully!")
        except Exception:
            print(f"Already active!")

    except Exception as e:
        print(f"Error: {str(e)}")
        raise
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    for url in STREAMLIT_URLS:
        wake_streamlit_app(url)
    print("All done!")

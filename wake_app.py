"""
Streamlit 앱을 자동으로 깨우는 스크립트
GitHub Actions에서 정기적으로 실행하여 앱이 sleep 모드에 들어가는 것을 방지합니다.

- 앱별로 최대 MAX_ATTEMPTS회 재시도
- 하나가 실패해도 나머지 앱은 계속 처리
- 실패한 앱이 있으면 종료 코드 1로 끝나 Actions에서 실패로 표시됨
"""

import os
import sys
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

STREAMLIT_URLS = [
    "https://stock-analysis-dongwooyun.streamlit.app/",
    "https://rental-churn-app-2026-dongwooyun.streamlit.app/",
]

WAKE_BUTTON_XPATH = "//button[contains(., 'Yes, get this app back up!')]"
MAX_ATTEMPTS = 2
PAGE_LOAD_TIMEOUT = 60  # 초
BUTTON_WAIT = 20  # 초: sleep 화면의 버튼이 나타나길 기다리는 시간
WAKE_WAIT = 90  # 초: 클릭 후 앱이 깨어나길 기다리는 시간


def build_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # setup-chrome 액션이 넘겨주는 경로가 있으면 사용
    chrome_bin = os.environ.get("CHROME_BIN")
    if chrome_bin:
        options.binary_location = chrome_bin

    driver_path = os.environ.get("CHROMEDRIVER_PATH")
    # 경로가 없으면 Selenium Manager가 알아서 드라이버를 받음
    service = Service(executable_path=driver_path) if driver_path else Service()

    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    return driver


def wake_streamlit_app(url):
    """앱 하나를 방문. 'already_active' 또는 'woke_up'을 반환, 실패 시 예외."""
    print(f"Starting: {url}", flush=True)
    driver = build_driver()
    try:
        driver.get(url)

        try:
            wake_button = WebDriverWait(driver, BUTTON_WAIT).until(
                EC.element_to_be_clickable((By.XPATH, WAKE_BUTTON_XPATH))
            )
        except TimeoutException:
            # 버튼이 없음 = 이미 깨어 있음. 앱이 로드되어 접속 기록이 남도록 잠시 대기
            time.sleep(10)
            print("Already active!", flush=True)
            return "already_active"

        print("Sleep detected. Clicking wake button...", flush=True)
        wake_button.click()

        # 버튼이 사라질 때까지 대기해서 실제로 깨어났는지 확인
        WebDriverWait(driver, WAKE_WAIT).until(
            EC.invisibility_of_element_located((By.XPATH, WAKE_BUTTON_XPATH))
        )
        time.sleep(10)  # 앱이 완전히 로드될 시간
        print("Woke up successfully!", flush=True)
        return "woke_up"
    finally:
        driver.quit()


def main():
    failed = []

    for url in STREAMLIT_URLS:
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                wake_streamlit_app(url)
                break
            except (TimeoutException, WebDriverException) as e:
                print(f"[{attempt}/{MAX_ATTEMPTS}] Error on {url}: {e.__class__.__name__}: {e}", flush=True)
                if attempt == MAX_ATTEMPTS:
                    failed.append(url)
                else:
                    time.sleep(5)

    if failed:
        print("\nFailed apps:", flush=True)
        for url in failed:
            print(f"  - {url}", flush=True)
        sys.exit(1)

    print("All done!", flush=True)


if __name__ == "__main__":
    main()

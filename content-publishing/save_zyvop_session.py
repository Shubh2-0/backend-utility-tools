import os
import time
from playwright.sync_api import sync_playwright

SESSION_FILE = os.path.join(os.path.dirname(__file__), "zyvop_state.json")

def main():
    print("=== ZyVOP One-Time Session Saver ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://zyvop.com/write", timeout=60000)
        print("Please ensure you are logged into ZyVOP in the browser window.")
        print("Waiting 15 seconds for session stabilization...")
        time.sleep(15)

        context.storage_state(path=SESSION_FILE)
        print(f"[SUCCESS] ZyVOP session saved to: {SESSION_FILE}")
        browser.close()

if __name__ == "__main__":
    main()

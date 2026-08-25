import os
import time
from playwright.sync_api import sync_playwright

API_KEY = "Doen5XSCgWmBSj2Cq7byuCWa"
img_path = r"c:\Users\shubh\OneDrive\Desktop\github\central-automation-engine\banners\banner_outbox_pattern.png"

profile_dir = os.path.expanduser(r"~\.zyvop_browser_profile")

with sync_playwright() as p:
    print("Launching Chromium browser to upload cover image natively to DEV.to...")
    browser = p.chromium.launch_persistent_context(
        user_data_dir=profile_dir,
        headless=False,
        viewport={"width": 1280, "height": 800}
    )

    page = browser.new_page()
    page.goto("https://dev.to/shubham_bhati/event-driven-microservices-with-apache-kafka-redis-caching-and-transactional-outbox-pattern-13a7/edit", timeout=60000)
    time.sleep(4)

    # Check for cover image file input
    file_input = page.locator('input[type="file"][name*="cover"], input[type="file"]')
    if file_input.count() > 0:
        print(f"Uploading native cover image from {img_path}...")
        file_input.first.set_input_files(img_path)
        time.sleep(5)

        # Save changes button
        save_btn = page.locator('button:has-text("Save"), input[type="submit"]')
        if save_btn.count() > 0:
            save_btn.first.click()
            time.sleep(5)
            print("[SUCCESS] Cover image uploaded natively to DEV.to S3 and saved!")

    time.sleep(5)
    browser.close()

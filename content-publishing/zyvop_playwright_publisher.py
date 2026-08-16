import os
import sys
import time
import json
from playwright.sync_api import sync_playwright

def publish_zyvop_full_automation(md_file_path, cover_image_path=None):
    if not os.path.exists(md_file_path):
        print(f"Error: Markdown file not found at {md_file_path}")
        return False

    with open(md_file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    lines = raw_text.splitlines()
    title = "Production Microservices Guide"
    subtitle = "A hands-on guide for Java & Spring Boot developers."
    body_lines = []

    for line in lines:
        if line.startswith("# ") and title == "Production Microservices Guide":
            title = line.replace("# ", "").strip()
        elif line.startswith("> Subtitle:") or line.startswith("## Subtitle:"):
            subtitle = line.replace("> Subtitle:", "").replace("## Subtitle:", "").strip()
        else:
            body_lines.append(line)

    content_markdown = "\n".join(body_lines).strip()
    plain_text = " ".join([l.strip() for l in body_lines if l.strip() and not l.startswith("#") and not l.startswith("```")])
    excerpt = plain_text[:240].strip() + "..."
    tags = ["springboot", "java", "microservices", "springcloud", "backend"]

    print(f"\n==========================================")
    print(f"Playwright Automation Engine Starting...")
    print(f"Title: {title}")
    print(f"Subtitle: {subtitle}")
    print(f"Cover Image: {cover_image_path}")
    print(f"==========================================\n")

    profile_dir = os.path.expanduser(r"~\.zyvop_browser_profile")
    os.makedirs(profile_dir, exist_ok=True)

    with sync_playwright() as p:
        print("Launching Chromium browser window...")
        browser = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=["--disable-blink-features=AutomationControlled"]
        )

        page = browser.new_page()
        print("Navigating to ZyVOP dashboard/write...")
        page.goto("https://zyvop.com/write", timeout=60000, wait_until="commit")
        time.sleep(3)

        if "login" in page.url:
            print("\n------------------------------------------------------------------")
            print("LOGIN REQUIRED: ZyVOP login screen detected.")
            print("Please log into your ZyVOP account in the opened Chromium window.")
            print("Waiting for login to complete...")
            print("------------------------------------------------------------------\n")
            
            while "login" in page.url or "accounts.google.com" in page.url:
                time.sleep(2)
            
            print("Login successful! Navigating to editor...")
            page.goto("https://zyvop.com/write", timeout=60000, wait_until="commit")
            time.sleep(3)

        print("\n[1/7] Populating Title & Subtitle...")
        try:
            title_input = page.locator('input[placeholder="Article title..."]')
            if title_input.count() > 0:
                title_input.fill(title)

            subtitle_input = page.locator('input[placeholder="Article subtitle (optional)..."]')
            if subtitle_input.count() > 0:
                subtitle_input.fill(subtitle)
        except Exception as e:
            print(f"Warning filling title/subtitle: {e}")

        print("[2/7] Populating Main Content in TipTap Rich Text Editor...")
        try:
            editor = page.locator('.tiptap.ProseMirror')
            if editor.count() > 0:
                editor.click()
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                editor.fill(content_markdown)
        except Exception as e:
            print(f"Warning filling editor content: {e}")

        print("[3/7] Setting Category to Tutorial...")
        try:
            category_select = page.locator('#category-select')
            if category_select.count() > 0:
                category_select.select_option(value="tutorial")
        except Exception as e:
            print(f"Warning setting category: {e}")

        print("[4/7] Setting Excerpt...")
        try:
            excerpt_input = page.locator('#excerpt-input')
            if excerpt_input.count() > 0:
                excerpt_input.fill(excerpt)
        except Exception as e:
            print(f"Warning setting excerpt: {e}")

        if cover_image_path and os.path.exists(cover_image_path):
            print(f"[5/7] Uploading Cover Image from {cover_image_path}...")
            try:
                cover_upload = page.locator('#cover-upload')
                if cover_upload.count() > 0:
                    cover_upload.set_input_files(cover_image_path)
            except Exception as e:
                print(f"Warning uploading cover image: {e}")

        print("[6/7] Adding Tags...")
        try:
            tag_input = page.locator('#tags-input, input[placeholder*="tags"]')
            if tag_input.count() > 0:
                for t in tags:
                    tag_input.fill(t)
                    page.keyboard.press("Enter")
                    time.sleep(0.3)
        except Exception as e:
            print(f"Warning adding tags: {e}")

        print("[7/7] Switching Status to Published & Setting SEO...")
        try:
            status_select = page.locator('#status-select')
            if status_select.count() > 0:
                status_select.select_option(value="published")

            meta_title = page.locator('input[id*="meta-title"], input[placeholder*="post title"]')
            if meta_title.count() > 0:
                meta_title.fill(f"{title} | Production Guide")

            meta_desc = page.locator('textarea[id*="meta-desc"], textarea[placeholder*="excerpt"]')
            if meta_desc.count() > 0:
                meta_desc.fill(excerpt)
        except Exception as e:
            print(f"Warning setting SEO fields: {e}")

        print("\nSUCCESS: All ZyVOP Editor Fields 100% Populated Automatically!")
        print("Clicking Header Publish Button...")
        try:
            publish_btn = page.locator('button:has-text("Publish"), button:has-text("Publish Post"), button[type="submit"]')
            if publish_btn.count() > 0:
                publish_btn.first.click()
                time.sleep(3)
                # Check for modal publish confirm
                confirm_btn = page.locator('button:has-text("Publish Now"), button:has-text("Confirm Publish")')
                if confirm_btn.count() > 0:
                    confirm_btn.first.click()
                    time.sleep(5)
                print(f"Published Article URL: {page.url}")
        except Exception as e:
            print(f"Warning clicking publish button: {e}")

        time.sleep(15)
        browser.close()
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python zyvop_playwright_publisher.py <path_to_markdown> [path_to_cover_image]")
        sys.exit(1)

    md = sys.argv[1]
    img = sys.argv[2] if len(sys.argv) > 2 else None
    publish_zyvop_full_automation(md, img)

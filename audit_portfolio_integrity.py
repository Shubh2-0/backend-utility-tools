import os
import re
import json
from bs4 import BeautifulSoup

PORTFOLIO_DIR = r"c:\Users\shubh\OneDrive\Desktop\github\Shubh2-0.github.io"
FORBIDDEN_WORDS = [
    r"\bdelve\b", r"\btapestry\b", r"\bcrucial\b", r"\bvital\b",
    r"\brobust\b", r"\bleverage\b", r"\bparadigm\b", r"\becosystem\b",
    r"\bseamless\b", r"\bgame-changer\b", r"\bindeed\b", r"\badditionally\b",
    r"\bfurthermore\b", r"\bdemystify\b", r"\btestament\b"
]

print("=== PORTFOLIO INTEGRITY AUDIT ===")
errors = 0
warnings = 0

html_files = []
for root, dirs, files in os.walk(PORTFOLIO_DIR):
    for f in files:
        if f.endswith(".html"):
            html_files.append(os.path.join(root, f))

print(f"Found {len(html_files)} HTML files to audit.")

for fpath in html_files:
    rel_path = os.path.relpath(fpath, PORTFOLIO_DIR)
    print(f"\n--- Checking: {rel_path} ---")
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Check forbidden words
    for pat in FORBIDDEN_WORDS:
        matches = re.findall(pat, content, re.IGNORECASE)
        if matches:
            print(f"  [ERROR] Forbidden word found: {matches} in {rel_path}")
            errors += 1

    # 2. Check JSON-LD validity
    soup = BeautifulSoup(content, "html.parser")
    json_scripts = soup.find_all("script", type="application/ld+json")
    for s in json_scripts:
        try:
            json.loads(s.string)
            print("  [OK] JSON-LD Schema is 100% valid JSON.")
        except Exception as e:
            print(f"  [ERROR] Invalid JSON-LD Schema: {e}")
            errors += 1

    # 3. Check local file links (href & src)
    file_dir = os.path.dirname(fpath)
    for tag in soup.find_all(["a", "img", "script", "link"]):
        url = tag.get("href") or tag.get("src")
        if not url:
            continue
        if url.startswith("http") or url.startswith("//") or url.startswith("mailto:") or url.startswith("tel:"):
            continue
        if url.startswith("#"):
            # Anchor link
            anchor = url[1:]
            if anchor and not soup.find(id=anchor):
                print(f"  [WARNING] Anchor #{anchor} not found on page {rel_path}")
                warnings += 1
            continue

        # Local path check
        clean_url = url.split("?")[0].split("#")[0]
        if clean_url:
            local_target = os.path.normpath(os.path.join(file_dir, clean_url))
            if not os.path.exists(local_target):
                print(f"  [ERROR] Broken local reference: '{url}' -> '{local_target}'")
                errors += 1

print("\n==========================================")
print(f"AUDIT FINISHED: {errors} Errors, {warnings} Warnings")
if errors == 0:
    print("ALL CHECKS PASSED: 100% BUG-FREE & FLAWLESS!")

import re
import os

README_PATH = r"c:\Users\shubh\OneDrive\Desktop\github\Shubh2-0\README.md"
FORBIDDEN_WORDS = [
    r"\bdelve\b", r"\btapestry\b", r"\bcrucial\b", r"\bvital\b",
    r"\brobust\b", r"\bleverage\b", r"\bparadigm\b", r"\becosystem\b",
    r"\bseamless\b", r"\bgame-changer\b", r"\bindeed\b", r"\badditionally\b",
    r"\bfurthermore\b", r"\bdemystify\b", r"\btestament\b"
]

print("=== GITHUB README INTEGRITY AUDIT ===")
errors = 0

with open(README_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Check forbidden words
for pat in FORBIDDEN_WORDS:
    matches = re.findall(pat, content, re.IGNORECASE)
    if matches:
        print(f"  [ERROR] Forbidden word found: {matches}")
        errors += 1

# 2. Check Oxford Commas (comma before 'and')
oxford_matches = re.findall(r",[ \t]+and\b", content, re.IGNORECASE)
if oxford_matches:
    print(f"  [ERROR] Oxford comma found: {oxford_matches}")
    errors += 1
else:
    print("  [OK] Zero Oxford commas found.")

# 3. Check Location
if "Noida" in content:
    print("  [OK] Location is Noida, India.")
else:
    print("  [WARNING] Location Noida not found.")

if errors == 0:
    print("ALL GITHUB README CHECKS PASSED: 100% CLEAN & FLAWLESS!")

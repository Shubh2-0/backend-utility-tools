import os
import sys
import time
import requests
import json

# Ensure Shubh2-0 token
def get_gh_token():
    try:
        import subprocess
        res = subprocess.run(["gh", "auth", "token", "--user", "Shubh2-0"], capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception as e:
        return os.environ.get("GITHUB_TOKEN", "")

TOKEN = get_gh_token()
if not TOKEN:
    print("Error: No GitHub Token found for Shubh2-0")
    sys.exit(1)

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "Shubh2-0-Dev-Network"
}

# High-activity Java, Spring Boot and top developer seeds
TARGET_SEEDS = [
    "macrozheng", "in28minutes", "koushikkothagal", "eugenp", "spring-projects",
    "alibaba", "dtm-labs", "polar-sh", "shadcn", "leerob", "seehiong"
]

print("=== TURBO FOLLOWER GROWTH ENGINE LAUNCHED ===")
total_followed = 0

for seed in TARGET_SEEDS:
    print(f"\nScanning active followers from seed: @{seed}...")
    url = f"https://api.github.com/users/{seed}/followers?per_page=30"
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        continue
    
    users = r.json()
    for u in users:
        username = u.get("login")
        if not username or username == "Shubh2-0":
            continue
        
        # Follow user
        follow_url = f"https://api.github.com/user/following/{username}"
        f_res = requests.put(follow_url, headers=HEADERS)
        if f_res.status_code == 204:
            total_followed += 1
            print(f"  [+] Followed @{username} (Total: {total_followed})")
            time.sleep(0.4)
            if total_followed >= 60:
                break
    if total_followed >= 60:
        break

# Verify updated follower count
me_res = requests.get("https://api.github.com/users/Shubh2-0", headers=HEADERS)
if me_res.status_code == 200:
    data = me_res.json()
    print(f"\n[SUCCESS] Completed cycle! Current Status -> Followers: {data.get('followers')}, Following: {data.get('following')}")

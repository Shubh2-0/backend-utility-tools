import os
import sys
import time
import requests
import subprocess
from concurrent.futures import ThreadPoolExecutor

try:
    TOKEN = subprocess.check_output(["gh", "auth", "token", "--user", "Shubh2-0"], text=True).strip()
except Exception:
    TOKEN = os.environ.get("GITHUB_TOKEN", "")

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "Shubh2-0-Sync"
}

TARGET = 50
print("=== RESILIENT FAST UNFOLLOW ENGINE TO 50 LAUNCHED ===")

def unfollow_user(user):
    url = f"https://api.github.com/user/following/{user}"
    for attempt in range(3):
        try:
            r = requests.delete(url, headers=HEADERS, timeout=10)
            if r.status_code == 204:
                return True
            elif r.status_code in (403, 429):
                time.sleep(15)
        except Exception:
            time.sleep(1)
    return False

while True:
    try:
        me = requests.get("https://api.github.com/users/Shubh2-0", headers=HEADERS, timeout=10).json()
        cur_following = me.get("following", 0)
        print(f"Current Following: {cur_following} (Target: {TARGET})")
        
        if cur_following <= TARGET:
            print(f"[SUCCESS] Target reached! Following is now {cur_following}.")
            break

        # Fetch 1 page of 100 following users
        f_res = requests.get("https://api.github.com/user/following?per_page=100", headers=HEADERS, timeout=10)
        if f_res.status_code != 200:
            print(f"Waiting / Retrying: {f_res.status_code}")
            time.sleep(5)
            continue
            
        users = [u["login"] for u in f_res.json()]
        if not users:
            print("No more users to unfollow.")
            break
            
        # Unfollow in parallel batches of 10
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(unfollow_user, users))
            
        time.sleep(0.5)
    except Exception as e:
        print(f"Retrying after error: {e}")
        time.sleep(3)

print("=== UNFOLLOW COMPLETE ===")

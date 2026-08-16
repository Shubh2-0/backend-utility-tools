import os
import sys
import time
import requests
import subprocess

def get_token():
    try:
        return subprocess.check_output(["gh", "auth", "token", "--user", "Shubh2-0"], text=True).strip()
    except Exception as e:
        print(f"Error fetching token: {e}")
        return os.environ.get("GH_TOKEN")

TARGET_USER = "seehiong"

def main():
    token = get_token()
    if not token:
        print("ERROR: No valid token found.")
        sys.exit(1)

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Mozilla/5.0"
    }

    followed_count = 0
    target_follow = 40

    print(f"=== Targeting Followers of @{TARGET_USER} ===")

    for page in range(1, 6):
        if followed_count >= target_follow:
            break
        url = f"https://api.github.com/users/{TARGET_USER}/followers?per_page=30&page={page}"
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                followers = resp.json()
                for item in followers:
                    if followed_count >= target_follow:
                        break
                    user = item.get("login") if isinstance(item, dict) else None
                    if not user or user == "Shubh2-0":
                        continue
                    
                    # Follow user
                    put_url = f"https://api.github.com/user/following/{user}"
                    put_resp = requests.put(put_url, headers=headers, timeout=10)
                    if put_resp.status_code in [204, 201]:
                        followed_count += 1
                        print(f"[{followed_count}/{target_follow}] Followed follower of @{TARGET_USER}: @{user}")
                        time.sleep(1.5)
        except Exception as e:
            print(f"Error on page {page}: {e}")

    print(f"=== Complete! Successfully followed {followed_count} active followers of @{TARGET_USER}. ===")

if __name__ == "__main__":
    main()

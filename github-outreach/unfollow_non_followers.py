import os
import sys
import time
import random
import subprocess
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

TOKEN = subprocess.check_output(["gh", "auth", "token"], text=True).strip()
USERNAME = "Shubh2-0"
API_BASE = "https://api.github.com"
headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "Mozilla/5.0"
}

def github_request(method, url):
    for attempt in range(3):
        try:
            if method.upper() == "GET":
                resp = requests.get(url, headers=headers, timeout=15)
            elif method.upper() == "DELETE":
                resp = requests.delete(url, headers=headers, timeout=15)
            else:
                return None

            if resp.status_code in (403, 429):
                reset_time = resp.headers.get("X-RateLimit-Reset")
                retry_after = resp.headers.get("Retry-After")
                wait_time = int(retry_after) + 5 if retry_after else (max(int(float(reset_time) - time.time()) + 5, 15) if reset_time else 20)
                print(f"  [Rate Limit Guard] Pausing for {wait_time}s...")
                time.sleep(wait_time)
                continue

            return resp
        except Exception as e:
            time.sleep(2)
    return None

def fetch_all_followers():
    print(f"Fetching followers for {USERNAME}...")
    followers = set()
    page = 1
    while True:
        url = f"{API_BASE}/users/{USERNAME}/followers?per_page=100&page={page}"
        resp = github_request("GET", url)
        if not resp or resp.status_code != 200:
            break
        data = resp.json()
        if not data:
            break
        for u in data:
            followers.add(u["login"])
        page += 1
    print(f"  Total followers: {len(followers)}")
    return followers

def fetch_all_following():
    print(f"Fetching following for {USERNAME}...")
    following = []
    page = 1
    while True:
        url = f"{API_BASE}/users/{USERNAME}/following?per_page=100&page={page}"
        resp = github_request("GET", url)
        if not resp or resp.status_code != 200:
            break
        data = resp.json()
        if not data:
            break
        for u in data:
            following.append(u["login"])
        page += 1
    print(f"  Total following: {len(following)}")
    return following

def unfollow_single(target):
    url = f"{API_BASE}/user/following/{target}"
    resp = github_request("DELETE", url)
    time.sleep(random.uniform(0.3, 0.6))
    if resp and resp.status_code == 204:
        return True, target
    return False, target

def unfollow_until_target(target_following=55, workers=5):
    followers = fetch_all_followers()
    following = fetch_all_following()

    current_following_count = len(following)
    print(f"\n--- Fast Concurrent Unfollow Engine ---")
    print(f"Followers: {len(followers)}")
    print(f"Following: {current_following_count}")
    print(f"Target Following Count: {target_following}")

    if current_following_count <= target_following:
        print(f"Already at or below target ({current_following_count} <= {target_following}). Nothing to do.")
        return

    non_followers = [u for u in following if u not in followers]
    needed_unfollows = current_following_count - target_following
    unfollow_list = non_followers[:needed_unfollows]

    print(f"Unfollowing {len(unfollow_list)} non-followers using {workers} parallel threads...\n")

    unfollowed = 0
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(unfollow_single, target): target for target in unfollow_list}
        for future in as_completed(futures):
            success, target = future.result()
            if success:
                unfollowed += 1
                remaining = current_following_count - unfollowed
                if unfollowed % 10 == 0 or remaining <= target_following + 10:
                    print(f"[{unfollowed}/{len(unfollow_list)}] Unfollowed: {target} (Remaining following: {remaining})")

    final_following = current_following_count - unfollowed
    print(f"\nFast Unfollow Complete! Total unfollowed: {unfollowed}. New total following: {final_following}")

if __name__ == "__main__":
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 55
    unfollow_until_target(target_following=target, workers=5)

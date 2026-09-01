import os
import sys
import time
import json
import requests
import subprocess
from datetime import datetime, timedelta

def get_gh_token():
    try:
        return subprocess.check_output(["gh", "auth", "token", "--user", "Shubh2-0"], text=True).strip()
    except Exception:
        return os.environ.get("GITHUB_TOKEN", "")

TOKEN = get_gh_token()
HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3.star+json",  # Includes starred_at timestamp
    "User-Agent": "Shubh2-0-Star-Manager"
}

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "starred_history.json")

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

def fetch_all_starred():
    starred = []
    page = 1
    while True:
        url = f"https://api.github.com/user/starred?per_page=100&page={page}"
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            break
        data = r.json()
        if not data:
            break
        starred.extend(data)
        page += 1
    return starred

def unstar_repo(repo_full_name):
    url = f"https://api.github.com/user/starred/{repo_full_name}"
    r = requests.delete(url, headers=HEADERS, timeout=10)
    return r.status_code == 204

def run_unstar_cycle(max_days=3, keep_min=25):
    print("=== AUTO UNSTAR ENGINE LAUNCHED ===")
    history = load_history()
    starred_list = fetch_all_starred()
    print(f"Total currently starred repositories: {len(starred_list)}")

    now = datetime.utcnow()
    cutoff_date = now - timedelta(days=max_days)

    unstarred_count = 0
    # Core repos you might want to always keep starred
    WHITELIST = {"spring-projects/spring-framework", "quarkusio/quarkus", "apache/rocketmq", "redis/redis"}

    for item in starred_list:
        repo_info = item.get("repo", {}) if "repo" in item else item
        full_name = repo_info.get("full_name")
        if not full_name or full_name in WHITELIST:
            continue

        starred_at_str = item.get("starred_at")
        should_unstar = False

        if starred_at_str:
            try:
                starred_at = datetime.strptime(starred_at_str, "%Y-%m-%dT%H:%M:%SZ")
                if starred_at < cutoff_date:
                    should_unstar = True
            except Exception:
                should_unstar = True
        else:
            # If no timestamp, check local history or unstar if over target
            recorded_time = history.get(full_name)
            if recorded_time:
                try:
                    rec_dt = datetime.fromisoformat(recorded_time)
                    if rec_dt < cutoff_date:
                        should_unstar = True
                except Exception:
                    should_unstar = True
            else:
                # Record current time
                history[full_name] = now.isoformat()

        if should_unstar and (len(starred_list) - unstarred_count > keep_min):
            success = unstar_repo(full_name)
            if success:
                unstarred_count += 1
                history.pop(full_name, None)
                if unstarred_count % 10 == 0 or unstarred_count <= 5:
                    print(f"  [-] Unstarred (Older than {max_days} days): {full_name}")
                time.sleep(0.3)

    save_history(history)
    print(f"\n[COMPLETE] Unstarred {unstarred_count} repos. Total starred remaining: {len(starred_list) - unstarred_count}")

if __name__ == "__main__":
    run_unstar_cycle(max_days=3, keep_min=25)

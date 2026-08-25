import os
import time
import subprocess
import json

def run_gh_api(endpoint):
    token = subprocess.check_output('gh auth token --user Shubh2-0', shell=True).decode().strip()
    cmd = f'curl.exe -s -H "Authorization: Bearer {token}" -H "Accept: application/vnd.github+json" "https://api.github.com/{endpoint}"'
    res = subprocess.check_output(cmd, shell=True).decode()
    return json.loads(res)

print("Checking mentions and notifications for Shubh2-0...")

# 1. Search issues/PRs where Shubh2-0 is mentioned
try:
    search_data = run_gh_api("search/issues?q=mentions:Shubh2-0+sort:updated-desc")
    items = search_data.get("items", [])
    print(f"\nFound {len(items)} issues/PRs mentioning @Shubh2-0:")
    for item in items[:10]:
        print(f"  - [{item.get('state')}] {item.get('title')} ({item.get('html_url')})")
        print(f"    Updated: {item.get('updated_at')}")
except Exception as e:
    print(f"Error searching mentions: {e}")

# 2. Check notifications
try:
    notifs = run_gh_api("notifications?all=true&per_page=15")
    print(f"\nRecent Notifications ({len(notifs)}):")
    for n in notifs[:10]:
        repo = n.get("repository", {}).get("full_name")
        title = n.get("subject", {}).get("title")
        updated = n.get("updated_at")
        reason = n.get("reason")
        print(f"  - [{reason}] {repo}: {title} (Updated: {updated})")
except Exception as e:
    print(f"Error fetching notifications: {e}")

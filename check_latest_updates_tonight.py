import subprocess
import json

def run_gh_api(endpoint):
    token = subprocess.check_output('gh auth token --user Shubh2-0', shell=True).decode().strip()
    cmd = f'curl.exe -s -H "Authorization: Bearer {token}" -H "Accept: application/vnd.github+json" "https://api.github.com/{endpoint}"'
    res = subprocess.check_output(cmd, shell=True).decode()
    return json.loads(res)

print("=== Checking Latest GitHub Activity for Shubh2-0 ===")

try:
    user_info = run_gh_api("users/Shubh2-0")
    print(f"Followers: {user_info.get('followers')} | Following: {user_info.get('following')} | Public Repos: {user_info.get('public_repos')}")
except Exception as e:
    print(f"Error fetching user stats: {e}")

try:
    notifs = run_gh_api("notifications?all=false&per_page=10")
    print(f"\nUnread GitHub Notifications ({len(notifs)}):")
    for n in notifs[:5]:
        repo = n.get("repository", {}).get("full_name")
        title = n.get("subject", {}).get("title")
        updated = n.get("updated_at")
        reason = n.get("reason")
        print(f"  - [{reason}] {repo}: {title} (Updated: {updated})")
except Exception as e:
    print(f"Error fetching notifications: {e}")

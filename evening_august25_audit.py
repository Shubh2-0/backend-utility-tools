import subprocess
import json

def run_gh_api(endpoint):
    token = subprocess.check_output('gh auth token --user Shubh2-0', shell=True).decode().strip()
    cmd = f'curl.exe -s -H "Authorization: Bearer {token}" -H "Accept: application/vnd.github+json" "https://api.github.com/{endpoint}"'
    res = subprocess.check_output(cmd, shell=True).decode()
    return json.loads(res)

print("=== Evening August 25 Live Status Report ===")

try:
    user = run_gh_api("users/Shubh2-0")
    print(f"Followers: {user.get('followers')} | Following: {user.get('following')} | Repos: {user.get('public_repos')}")
except Exception as e:
    print(f"Error fetching user: {e}")

try:
    notifs = run_gh_api("notifications?all=false")
    print(f"\nUnread Notifications Count: {len(notifs)}")
    for n in notifs[:5]:
        repo = n.get("repository", {}).get("full_name")
        title = n.get("subject", {}).get("title")
        updated = n.get("updated_at")
        print(f"  - [{repo}] {title} (Updated: {updated})")
except Exception as e:
    print(f"Error fetching notifs: {e}")

try:
    sf_comments = run_gh_api("repos/spring-projects/spring-framework/issues/37151/comments")
    print(f"\nSpring Framework Issue #37151 Total Comments: {len(sf_comments)}")
    if sf_comments:
        last = sf_comments[-1]
        print(f"  Latest Comment by @{last.get('user', {}).get('login')}: {last.get('body')[:200]}")
except Exception as e:
    print(f"Error checking spring-framework issue: {e}")

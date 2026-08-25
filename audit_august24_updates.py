import subprocess
import json

def run_gh_api(endpoint):
    token = subprocess.check_output('gh auth token --user Shubh2-0', shell=True).decode().strip()
    cmd = f'curl.exe -s -H "Authorization: Bearer {token}" -H "Accept: application/vnd.github+json" "https://api.github.com/{endpoint}"'
    res = subprocess.check_output(cmd, shell=True).decode()
    return json.loads(res)

print("=== August 24 Audit Report for Shubh2-0 ===")

# 1. User stats
try:
    user_info = run_gh_api("users/Shubh2-0")
    print(f"Followers: {user_info.get('followers')} | Following: {user_info.get('following')} | Public Repos: {user_info.get('public_repos')}")
except Exception as e:
    print(f"Error fetching user stats: {e}")

# 2. Notifications
try:
    notifs = run_gh_api("notifications?all=true&per_page=20")
    print(f"\nRecent GitHub Notifications ({len(notifs)}):")
    for n in notifs[:10]:
        repo = n.get("repository", {}).get("full_name")
        title = n.get("subject", {}).get("title")
        updated = n.get("updated_at")
        reason = n.get("reason")
        print(f"  - [{reason}] {repo}: {title} (Updated: {updated})")
except Exception as e:
    print(f"Error fetching notifications: {e}")

# 3. Check PR #801 on occurrent
try:
    pr801 = run_gh_api("repos/johanhaleby/occurrent/pulls/801")
    print(f"\nOccurrent PR #801 State: {pr801.get('state')} | Draft: {pr801.get('draft')} | Comments: {pr801.get('comments')}")
except Exception as e:
    print(f"Error checking PR #801: {e}")

# 4. Check okta issue #933
try:
    okta_comments = run_gh_api("repos/okta/okta-spring-boot/issues/933/comments")
    print(f"\nOkta Issue #933 Comments Count: {len(okta_comments)}")
    if okta_comments:
        last = okta_comments[-1]
        print(f"  Latest Comment by @{last.get('user', {}).get('login')}: {last.get('body')[:200]}")
except Exception as e:
    print(f"Error checking Okta issue: {e}")

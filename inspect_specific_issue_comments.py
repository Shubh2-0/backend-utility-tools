import json
import subprocess

def run_gh_api(endpoint):
    token = subprocess.check_output('gh auth token --user Shubh2-0', shell=True).decode().strip()
    cmd = f'curl.exe -s -H "Authorization: Bearer {token}" -H "Accept: application/vnd.github+json" "https://api.github.com/{endpoint}"'
    res = subprocess.check_output(cmd, shell=True).decode()
    return json.loads(res)

# 1. JoeJoeJoe352/moneytracker_v2 issues/comments
print("=== 1. Checking JoeJoeJoe352/moneytracker_v2 ===")
try:
    data = run_gh_api("repos/JoeJoeJoe352/moneytracker_v2/issues?state=all")
    for issue in data[:3]:
        print(f"Issue #{issue.get('number')}: {issue.get('title')}")
        comments = run_gh_api(f"repos/JoeJoeJoe352/moneytracker_v2/issues/{issue.get('number')}/comments")
        if comments:
            last = comments[-1]
            print(f"  Latest comment by @{last.get('user', {}).get('login')}: {last.get('body')[:250]}\n")
except Exception as e:
    print(f"Error checking moneytracker_v2: {e}")

# 2. okta/okta-spring-boot issue/PR mention
print("=== 2. Checking okta/okta-spring-boot ===")
try:
    data = run_gh_api("repos/okta/okta-spring-boot/issues?state=all&per_page=5")
    for issue in data:
        if "AuthenticationManagerResolver" in issue.get("title", ""):
            print(f"Issue #{issue.get('number')}: {issue.get('title')}")
            comments = run_gh_api(f"repos/okta/okta-spring-boot/issues/{issue.get('number')}/comments")
            if comments:
                last = comments[-1]
                print(f"  Latest comment by @{last.get('user', {}).get('login')}: {last.get('body')[:250]}\n")
except Exception as e:
    print(f"Error checking okta-spring-boot: {e}")

# 3. carstenartur/Taxonomy #744
print("=== 3. Checking carstenartur/Taxonomy #744 ===")
try:
    comments = run_gh_api("repos/carstenartur/Taxonomy/issues/744/comments")
    print(f"Total comments on Taxonomy #744: {len(comments)}")
    for c in comments[-3:]:
        print(f"  Comment by @{c.get('user', {}).get('login')}: {c.get('body')[:250]}\n")
except Exception as e:
    print(f"Error checking Taxonomy: {e}")

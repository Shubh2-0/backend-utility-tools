import subprocess
import json

def run_gh_api(endpoint):
    token = subprocess.check_output('gh auth token --user Shubh2-0', shell=True).decode().strip()
    cmd = f'curl.exe -s -H "Authorization: Bearer {token}" -H "Accept: application/vnd.github+json" "https://api.github.com/{endpoint}"'
    res = subprocess.check_output(cmd, shell=True).decode()
    return json.loads(res)

print("=== Checking spring-projects/spring-framework#37151 ===")
try:
    issue1 = run_gh_api("repos/spring-projects/spring-framework/issues/37151")
    print(f"State: {issue1.get('state')} | Locked: {issue1.get('locked')} | Comments: {issue1.get('comments')}")
    comments1 = run_gh_api("repos/spring-projects/spring-framework/issues/37151/comments")
    print(f"Total Comments: {len(comments1)}")
    if comments1:
        print(f"  Latest comment by @{comments1[-1].get('user', {}).get('login')}: {comments1[-1].get('body')[:200]}")
except Exception as e:
    print(f"Error checking spring-framework: {e}")

print("\n=== Checking resilience4j/resilience4j#2275 ===")
try:
    issue2 = run_gh_api("repos/resilience4j/resilience4j/issues/2275")
    print(f"State: {issue2.get('state')} | Locked: {issue2.get('locked')} | Comments: {issue2.get('comments')}")
    comments2 = run_gh_api("repos/resilience4j/resilience4j/issues/2275/comments")
    print(f"Total Comments: {len(comments2)}")
    if comments2:
        print(f"  Latest comment by @{comments2[-1].get('user', {}).get('login')}: {comments2[-1].get('body')[:200]}")
except Exception as e:
    print(f"Error checking resilience4j: {e}")

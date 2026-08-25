import subprocess
import json

def run_gh_api(endpoint):
    token = subprocess.check_output('gh auth token --user Shubh2-0', shell=True).decode().strip()
    cmd = f'curl.exe -s -H "Authorization: Bearer {token}" -H "Accept: application/vnd.github+json" "https://api.github.com/{endpoint}"'
    res = subprocess.check_output(cmd, shell=True).decode()
    return json.loads(res)

print("=== Inspecting DavidHLP/ResiCache ===")
try:
    data = run_gh_api("repos/DavidHLP/ResiCache/issues?state=all")
    for issue in data[:3]:
        print(f"Issue #{issue.get('number')}: {issue.get('title')}")
        comments = run_gh_api(f"repos/DavidHLP/ResiCache/issues/{issue.get('number')}/comments")
        if comments:
            last = comments[-1]
            print(f"  Latest comment by @{last.get('user', {}).get('login')}: {last.get('body')[:300]}\n")
except Exception as e:
    print(f"Error: {e}")

print("=== Inspecting emreekiziltoprak/payment-gateway-service ===")
try:
    pulls = run_gh_api("repos/emreekiziltoprak/payment-gateway-service/pulls?state=all")
    for p in pulls[:3]:
        print(f"PR #{p.get('number')}: {p.get('title')} ({p.get('html_url')})")
        comments = run_gh_api(f"repos/emreekiziltoprak/payment-gateway-service/issues/{p.get('number')}/comments")
        if comments:
            last = comments[-1]
            print(f"  Latest comment by @{last.get('user', {}).get('login')}: {last.get('body')[:300]}\n")
except Exception as e:
    print(f"Error: {e}")

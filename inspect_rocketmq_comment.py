import subprocess
import json

token = subprocess.check_output('gh auth token --user Shubh2-0', shell=True).decode().strip()
url = "https://api.github.com/repos/apache/rocketmq/issues/10936/comments"
cmd = f'curl.exe -s -H "Authorization: Bearer {token}" -H "Accept: application/vnd.github+json" "{url}"'
res = subprocess.check_output(cmd, shell=True).decode()
comments = json.loads(res)

print(f"Total Comments on apache/rocketmq#10936: {len(comments)}")
if comments:
    for c in comments[-3:]:
        print(f"  Comment by @{c.get('user', {}).get('login')} (Updated: {c.get('updated_at')}):")
        print(f"  {c.get('body')[:300]}\n")

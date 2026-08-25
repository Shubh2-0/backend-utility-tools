import subprocess
import json

def run_gh_api(endpoint):
    token = subprocess.check_output('gh auth token --user Shubh2-0', shell=True).decode().strip()
    cmd = f'curl.exe -s -H "Authorization: Bearer {token}" -H "Accept: application/vnd.github+json" "https://api.github.com/{endpoint}"'
    res = subprocess.check_output(cmd, shell=True).decode()
    return json.loads(res)

print("Searching fresh open source Java / Spring Boot / Kafka issues for contribution...\n")

repos = [
    "spring-projects/spring-boot",
    "strimzi/strimzi-kafka-operator",
    "johanhaleby/occurrent",
    "apache/rocketmq",
    "hibernate/hibernate-orm"
]

results = []

for repo in repos:
    try:
        data = run_gh_api(f"search/issues?q=repo:{repo}+is:issue+is:open+label:%22help%20wanted%22+sort:updated-desc")
        items = data.get("items", [])
        print(f"=== {repo} (Found {len(items)} help-wanted issues) ===")
        for item in items[:3]:
            title = item.get("title")
            url = item.get("html_url")
            comments_count = item.get("comments")
            updated = item.get("updated_at")
            print(f"  - #{item.get('number')}: {title}")
            print(f"    URL: {url} | Comments: {comments_count} | Updated: {updated}\n")
            results.append({"repo": repo, "title": title, "url": url, "number": item.get("number")})
    except Exception as e:
        print(f"Error searching {repo}: {e}")

print(f"\nTotal Candidate Open-Source Issues Discovered: {len(results)}")

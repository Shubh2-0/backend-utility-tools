import subprocess
import json

def run_gh_api(endpoint):
    token = subprocess.check_output('gh auth token --user Shubh2-0', shell=True).decode().strip()
    cmd = f'curl.exe -s -H "Authorization: Bearer {token}" -H "Accept: application/vnd.github+json" "https://api.github.com/{endpoint}"'
    res = subprocess.check_output(cmd, shell=True).decode()
    return json.loads(res)

print("=== Searching Top Open Source Java Projects & Issues ===\n")

# 1. Trending Java Repositories
print("1. Trending Active Java/Spring Boot Repositories:")
try:
    search_repos = run_gh_api("search/repositories?q=language:java+stars:>1000+sort:updated-desc&per_page=5")
    for r in search_repos.get("items", []):
        print(f"  - {r.get('full_name')} (Stars: {r.get('stargazers_count')})")
        print(f"    Description: {r.get('description')[:120] if r.get('description') else 'No desc'}")
        print(f"    URL: {r.get('html_url')}\n")
except Exception as e:
    print(f"Error fetching repos: {e}")

# 2. Fresh Open Java Issues
print("2. Fresh High-Priority Open Issues in Spring/Kafka Ecosystem:")
repos_to_check = [
    "spring-projects/spring-framework",
    "strimzi/strimzi-kafka-operator",
    "apache/kafka",
    "resilience4j/resilience4j"
]

for repo in repos_to_check:
    try:
        issues = run_gh_api(f"search/issues?q=repo:{repo}+is:issue+is:open+sort:updated-desc&per_page=2")
        print(f"  Repo: {repo}")
        for item in issues.get("items", []):
            print(f"    - #{item.get('number')}: {item.get('title')}")
            print(f"      URL: {item.get('html_url')}\n")
    except Exception as e:
        print(f"  Error checking {repo}: {e}")

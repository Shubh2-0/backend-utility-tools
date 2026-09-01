import os
import json
import urllib.request
import urllib.parse
from pathlib import Path

# Load .env
env_path = Path(__file__).parent / ".env"
devto_key = None
if env_path.exists():
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if "DEVTO_API_KEY" in line:
            devto_key = line.split("=", 1)[1].strip()

if not devto_key:
    devto_key = os.environ.get("DEVTO_API_KEY", "Doen5XSCgWmBSj2Cq7byuCWa")

print(f"Publishing blog using DEV.to API Key: {devto_key[:8]}...")

article_file = Path(__file__).parent / "content-publishing" / "generated_tech_post.md"
if not article_file.exists():
    print("Error: Generated article file not found.")
    exit(1)

content = article_file.read_text(encoding="utf-8")

# Extract title and tags from frontmatter
lines = content.splitlines()
title = "High-Throughput Microservices: Kafka, Redis & Transactional Outbox"
tags = ["springboot", "java", "kafka", "redis"]
body_md = content

if lines[0].strip() == "---":
    end_fm = lines[1:].index("---") + 1
    fm_lines = lines[1:end_fm]
    body_md = "\n".join(lines[end_fm+1:]).strip()
    for l in fm_lines:
        if l.startswith("title:"):
            title = l.split(":", 1)[1].strip().strip('"')
        elif l.startswith("tags:"):
            raw_tags = l.split(":", 1)[1].strip().strip('[').strip(']')
            tags = [t.strip().strip('"').strip("'") for t in raw_tags.split(",")]

cover_image_url = "https://raw.githubusercontent.com/Shubh2-0/backend-utility-tools/master/banners/banner_outbox_pattern.png"

payload = {
    "article": {
        "title": title,
        "published": True,
        "body_markdown": body_md,
        "tags": tags[:4],
        "main_image": cover_image_url
    }
}

req = urllib.request.Request(
    "https://dev.to/api/articles",
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Content-Type": "application/json",
        "api-key": devto_key,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    },
    method="POST"
)

try:
    with urllib.request.urlopen(req) as resp:
        res_data = json.loads(resp.read().decode("utf-8"))
        print("\n==========================================")
        print("  [SUCCESS] Article Published Live on DEV.to!")
        print(f"  Title: {res_data.get('title')}")
        print(f"  URL: {res_data.get('url')}")
        print("==========================================")
except Exception as e:
    print(f"Error publishing to DEV.to: {e}")

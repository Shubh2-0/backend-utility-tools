import os
import sys
import json
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

TOKEN = os.environ.get("ZYVOP_API_TOKEN")
if not TOKEN or "dummy" in TOKEN:
    print("Error: ZYVOP_API_TOKEN not found or set to dummy in .env")
    sys.exit(1)

ZYVOP_API_URL = "https://zyvop.com/api/v1/articles"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "User-Agent": "CentralAutomationEngine/1.0"
}

def publish_article(title, content, tags=None, canonical_url=None):
    if tags is None:
        tags = ["springboot", "java", "microservices", "springcloud"]

    payload = {
        "title": title,
        "content": content,
        "tags": tags,
        "published": True,
        "status": "PUBLISHED"
    }
    if canonical_url:
        payload["canonical_url"] = canonical_url

    print(f"Publishing article to ZyVOP: '{title}'...")
    try:
        resp = requests.post(ZYVOP_API_URL, headers=headers, json=payload, timeout=20)
        if resp.status_code in (200, 201):
            print("Successfully published to ZyVOP!")
            print("Response:", resp.json())
            return True
        else:
            print(f"Failed to publish (HTTP {resp.status_code}): {resp.text}")
            return False
    except Exception as e:
        print(f"Exception during ZyVOP publishing: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python publish_zyvop.py <path_to_markdown_file> [canonical_url]")
        sys.exit(1)

    file_path = sys.argv[1]
    url = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    lines = raw_text.splitlines()
    article_title = "Service Discovery with Eureka and Spring Cloud: A Production Hands-On Guide"
    body_lines = []

    for line in lines:
        if line.startswith("# ") and article_title == "Service Discovery with Eureka and Spring Cloud: A Production Hands-On Guide":
            article_title = line.replace("# ", "").strip()
        else:
            body_lines.append(line)

    article_content = "\n".join(body_lines).strip()
    publish_article(title=article_title, content=article_content, canonical_url=url)

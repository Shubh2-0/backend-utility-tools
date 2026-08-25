import os
import sys
import json
import time
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

ZYVOP_TOKEN = os.environ.get("ZYVOP_API_TOKEN")

class AutoPublishEngine:

    def __init__(self):
        self.zyvop_token = ZYVOP_TOKEN

    def extract_article_metadata(self, md_path):
        with open(md_path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        lines = raw_text.splitlines()
        title = "Production Microservices Guide"
        subtitle = "A hands-on guide for Java & Spring Boot developers."
        body_lines = []

        for line in lines:
            if line.startswith("# ") and title == "Production Microservices Guide":
                title = line.replace("# ", "").strip()
            elif line.startswith("> Subtitle:") or line.startswith("## Subtitle:"):
                subtitle = line.replace("> Subtitle:", "").replace("## Subtitle:", "").strip()
            else:
                body_lines.append(line)

        content = f"# {title}\n\n{subtitle}\n\n" + "\n".join(body_lines).strip()

        plain_text = " ".join([l.strip() for l in body_lines if l.strip() and not l.startswith("#") and not l.startswith("```")])
        excerpt = plain_text[:250].strip() + "..."

        tags = ["springboot", "java", "microservices", "springcloud", "backend"]

        return {
            "title": title,
            "subtitle": subtitle,
            "content": content,
            "excerpt": excerpt,
            "tags": tags,
            "meta_title": f"{title} | Spring Boot Guide",
            "meta_description": excerpt,
            "og_title": title,
            "og_description": excerpt
        }

    def publish_to_zyvop(self, metadata, cover_image_url=None):
        if not self.zyvop_token or "dummy" in self.zyvop_token:
            print("Error: ZYVOP_API_TOKEN not configured.")
            return False

        headers = {
            "Authorization": f"Bearer {self.zyvop_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "name": metadata["title"],
            "title": metadata["title"],
            "postTitle": metadata["title"],
            "subtitle": metadata["subtitle"],
            "content": metadata["content"],
            "excerpt": metadata["excerpt"],
            "tags": metadata["tags"],
            "metaTitle": metadata["meta_title"],
            "metaDescription": metadata["meta_description"],
            "ogTitle": metadata["og_title"],
            "ogDescription": metadata["og_description"],
            "published": True,
            "status": "PUBLISHED"
        }
        if cover_image_url:
            payload["coverImage"] = cover_image_url

        print(f"[Auto-Publish Engine] Publishing to ZyVOP: '{metadata['title']}'...")
        try:
            resp = requests.post("https://zyvop.com/api/v1/articles", headers=headers, json=payload, timeout=20)
            if resp.status_code in (200, 201):
                res_data = resp.json()
                print("SUCCESS: ZyVOP API Publishing Complete!")
                print("Response Data:", json.dumps(res_data, indent=2))
                return True
            else:
                print(f"FAILED: ZyVOP API Status {resp.status_code}: {resp.text}")
                return False
        except Exception as e:
            print(f"ERROR: Exception publishing to ZyVOP: {e}")
            return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python auto_publish_engine.py <markdown_file> [cover_image_url]")
        sys.exit(1)

    md_file = sys.argv[1]
    image_url = sys.argv[2] if len(sys.argv) > 2 else None

    engine = AutoPublishEngine()
    meta = engine.extract_article_metadata(md_file)
    engine.publish_to_zyvop(meta, cover_image_url=image_url)

"""
Auto-post articles to Dev.to + Hashnode.

Usage:
    python auto-post.py <article-folder-name>

Example:
    python auto-post.py devto-articles/01-bcom-to-backend

Reads:
    <folder>/title.txt        — first line: article title
    <folder>/tags.txt         — comma-separated tags
    <folder>/body.md          — markdown body

Required environment variables:
    DEV_TO_API_KEY            — from https://dev.to/settings/extensions
    HASHNODE_TOKEN            — from https://hashnode.com/settings/developer
    HASHNODE_PUBLICATION_ID   — your hashnode publication ID (see README)

Outputs:
    Posts to both platforms, prints live URLs.
"""

import os
import sys
import json
import requests
from pathlib import Path

DEV_TO_API = "https://dev.to/api/articles"
HASHNODE_API = "https://gql.hashnode.com/"


def post_to_devto(api_key: str, title: str, body: str, tags: list[str], canonical_url: str | None = None) -> dict:
    """Publish article on Dev.to via REST API."""
    payload = {
        "article": {
            "title": title,
            "body_markdown": body,
            "published": True,
            "tags": tags[:4],  # Dev.to max 4 tags
        }
    }
    if canonical_url:
        payload["article"]["canonical_url"] = canonical_url

    r = requests.post(
        DEV_TO_API,
        headers={"api-key": api_key, "Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=30,
    )
    if r.status_code not in (200, 201):
        return {"ok": False, "error": f"HTTP {r.status_code}: {r.text[:300]}"}
    data = r.json()
    return {"ok": True, "url": data.get("url", "?"), "id": data.get("id")}


def post_to_hashnode(token: str, publication_id: str, title: str, body: str, tags: list[str]) -> dict:
    """Publish article on Hashnode via GraphQL."""
    # Hashnode wants tag objects with `slug` and `name`
    tag_objects = [{"slug": t.lower().replace(" ", "-"), "name": t} for t in tags[:5]]

    mutation = """
    mutation PublishPost($input: PublishPostInput!) {
      publishPost(input: $input) {
        post {
          id
          slug
          url
        }
      }
    }
    """
    variables = {
        "input": {
            "title": title,
            "contentMarkdown": body,
            "tags": tag_objects,
            "publicationId": publication_id,
        }
    }

    r = requests.post(
        HASHNODE_API,
        headers={"Authorization": f"Bearer {token}" if not token.startswith("Bearer ") else token, "Content-Type": "application/json"},
        data=json.dumps({"query": mutation, "variables": variables}),
        timeout=30,
    )
    if r.status_code != 200:
        return {"ok": False, "error": f"HTTP {r.status_code}: {r.text[:300]}"}
    j = r.json()
    if "errors" in j:
        return {"ok": False, "error": str(j["errors"])[:300]}
    post = j.get("data", {}).get("publishPost", {}).get("post", {})
    return {"ok": True, "url": post.get("url", "?"), "id": post.get("id")}


def post_to_medium(token: str, title: str, body: str, tags: list[str], canonical_url: str | None = None) -> dict:
    """Publish article on Medium via REST API."""
    # Step 1: Get Author ID
    me_url = "https://api.medium.com/v1/me"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    try:
        r = requests.get(me_url, headers=headers, timeout=20)
        if r.status_code != 200:
            return {"ok": False, "error": f"ME Endpoint HTTP {r.status_code}: {r.text[:200]}"}
        
        author_id = r.json().get("data", {}).get("id")
        if not author_id:
            return {"ok": False, "error": "Medium Author ID not found in response data"}
            
        # Step 2: Create Post
        post_url = f"https://api.medium.com/v1/users/{author_id}/posts"
        payload = {
            "title": title,
            "contentFormat": "markdown",
            "content": f"# {title}\n\n{body}",
            "tags": tags[:3],  # Medium recommends max 3 tags
            "publishStatus": "public"
        }
        if canonical_url:
            payload["canonicalUrl"] = canonical_url

        r = requests.post(post_url, headers=headers, json=payload, timeout=30)
        if r.status_code not in (200, 201):
            return {"ok": False, "error": f"Publish Endpoint HTTP {r.status_code}: {r.text[:300]}"}
        data = r.json()
        return {"ok": True, "url": data.get("data", {}).get("url", "?")}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def load_article(folder: Path) -> tuple[str, str, list[str]]:
    """Read article from folder structure."""
    title = (folder / "title.txt").read_text(encoding="utf-8").strip().splitlines()[0]
    body = (folder / "body.md").read_text(encoding="utf-8")
    raw_tags = (folder / "tags.txt").read_text(encoding="utf-8").strip()
    tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
    return title, body, tags


def main():
    if len(sys.argv) < 2:
        print("Usage: python auto-post.py <article-folder>")
        sys.exit(1)

    folder = Path(sys.argv[1])
    if not folder.is_dir():
        print(f"Not a directory: {folder}")
        sys.exit(1)

    title, body, tags = load_article(folder)
    print(f"\n=== Publishing: {title} ===")
    print(f"Tags: {tags}\n")

    devto_key = os.environ.get("DEV_TO_API_KEY")
    hashnode_token = os.environ.get("HASHNODE_TOKEN")
    hashnode_pub = os.environ.get("HASHNODE_PUBLICATION_ID")
    medium_token = os.environ.get("MEDIUM_TOKEN")

    canonical = None

    if devto_key:
        print("Posting to Dev.to...")
        result = post_to_devto(devto_key, title, body, tags)
        if result["ok"]:
            print(f"  [OK]   {result['url']}")
            canonical = result["url"]
        else:
            print(f"  [FAIL] {result['error']}")
    else:
        print("[SKIP] Dev.to (DEV_TO_API_KEY not set)")

    if hashnode_token and hashnode_pub:
        print("Posting to Hashnode (using Dev.to as canonical)...")
        result = post_to_hashnode(hashnode_token, hashnode_pub, title, body, tags)
        if result["ok"]:
            print(f"  [OK]   {result['url']}")
        else:
            print(f"  [FAIL] {result['error']}")
    else:
        print("[SKIP] Hashnode (HASHNODE_TOKEN or HASHNODE_PUBLICATION_ID not set)")

    if medium_token:
        print("Posting to Medium (using Dev.to as canonical)...")
        result = post_to_medium(medium_token, title, body, tags, canonical)
        if result["ok"]:
            print(f"  [OK]   {result['url']}")
        else:
            print(f"  [FAIL] {result['error']}")
    else:
        print("[SKIP] Medium (MEDIUM_TOKEN not set)")

    print("\nDone.")


if __name__ == "__main__":
    main()

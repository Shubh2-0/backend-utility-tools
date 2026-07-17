"""
Free SEO content bot — generates Java/Spring/MySQL/AI articles using Groq's
free Llama 3.3 70B API, embeds Unsplash images (no key needed), publishes to
Dev.to and Hashnode.

Zero paid services. Setup:
    1. Get Groq API key (free, no credit card): https://console.groq.com/keys
    2. Set env vars (locally or as GitHub secrets):
         GROQ_API_KEY               — required, content generation
         DEV_TO_API_KEY             — optional, Dev.to publishing
         HASHNODE_TOKEN             — optional, Hashnode publishing
         HASHNODE_PUBLICATION_ID    — optional, Hashnode publishing

Usage:
    python free-content-bot.py                          # auto-rotate next topic
    python free-content-bot.py --slug spring-boot-rest-api-best-practices-2026
    python free-content-bot.py --dry-run                # generate but don't publish
    python free-content-bot.py --no-publish             # save .md only

Article rotation is deterministic: index = (ISO week number) % len(topics),
so the same week always picks the same topic (idempotent reruns).
"""

import argparse
import datetime
import json
import os
import random
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).parent
TOPICS_FILE = ROOT / "topics-pool.json"
HISTORY_FILE = ROOT / "published-history.json"
OUTPUT_DIR = ROOT / "generated-articles"

GROQ_API = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

DEV_TO_API = "https://dev.to/api/articles"
HASHNODE_API = "https://gql.hashnode.com/"

AUTHOR_BIO = (
    "*Written by **Shubham Bhati** — Backend Engineer at AlignBits LLC, "
    "specializing in Java 17, Spring Boot, microservices, and AI integration. "
    "Connect on [LinkedIn](https://linkedin.com/in/bhatishubham), "
    "[GitHub](https://github.com/Shubh2-0), or read more at "
    "[shubh2-0.github.io](https://shubh2-0.github.io).*"
)


def load_topics() -> list[dict]:
    data = json.loads(TOPICS_FILE.read_text(encoding="utf-8"))
    return data["topics"]


def load_history() -> dict:
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    return {"published": []}


def save_history(history: dict) -> None:
    HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")


def pick_topic(topics: list[dict], history: dict, explicit_slug: str | None) -> dict:
    if explicit_slug:
        for t in topics:
            if t["slug"] == explicit_slug:
                return t
        raise SystemExit(f"slug '{explicit_slug}' not found in topics-pool.json")

    published_slugs = {p["slug"] for p in history.get("published", [])}
    fresh = [t for t in topics if t["slug"] not in published_slugs]
    if fresh:
        week = datetime.date.today().isocalendar().week
        return fresh[week % len(fresh)]
    # exhausted — rotate by week
    week = datetime.date.today().isocalendar().week
    return topics[week % len(topics)]


def unsplash_image(query: str, width: int = 1200, height: int = 630, seed: int | None = None) -> str:
    """Direct Unsplash image URL — no API key needed."""
    q = query.replace(" ", ",")
    sig = seed if seed is not None else random.randint(1, 99999)
    return f"https://source.unsplash.com/{width}x{height}/?{q}&sig={sig}"


def build_prompt(topic: dict) -> str:
    return f"""You are writing a long-form SEO blog post for a Java/Spring Boot backend
developer audience. The author is Shubham Bhati, a Backend Engineer with 3+ years
of production experience.

TOPIC: {topic['title']}
PRIMARY KEYWORD: {topic['primary_keyword']}
SECONDARY KEYWORDS: {', '.join(topic['secondary_keywords'])}
SEARCH INTENT: {topic['search_intent']}

WRITE A FULL MARKDOWN ARTICLE WITH THIS STRUCTURE:

1. **Intro paragraph** (80-120 words) — hook the reader with a real production
   problem. Mention the primary keyword naturally in the first 100 words.

2. **Table of Contents** (markdown bullet list with anchor links to the H2s
   you'll write below).

3. **6-8 H2 sections** (## headings). Each section:
   - 200-350 words
   - At least ONE code example in ```java ... ``` or ```sql ... ``` or
     ```yaml ... ``` fences (4-15 lines, runnable-looking)
   - Concrete numbers, version-specific notes, "in production we saw..."
     anecdotes
   - Sprinkle secondary keywords naturally — no stuffing

4. **Common Mistakes** H2 — bullet list of 5 pitfalls

5. **FAQ** H2 — 4 questions with 2-3 sentence answers each (use H3 for
   each question — these get picked up by Google's People-Also-Ask)

6. **Conclusion** (100-150 words) — recap and one call to action

CONTENT RULES:
- Total length: 1500-2200 words
- Conversational but technical voice (first person plural "we" works well)
- NO em-dashes, NO words: "leverage", "synergy", "delve", "moreover", "robust",
  "in today's fast-paced world", "embark on", "harness"
- DO use: practical examples, version numbers (Java 21, Spring Boot 3.2), real
  metrics ("reduced p99 from 800ms to 120ms"), trade-offs
- DO link out 2-3 times to authoritative sources (Spring docs, Oracle docs,
  Baeldung, official Java tutorials) — use markdown link syntax
- For code: write real Java/Spring code that compiles, not pseudocode
- Tone: like a senior engineer mentoring a mid-level dev. Confident, opinionated,
  but never condescending.

OUTPUT FORMAT:
- Return ONLY the markdown body. NO title at the top (it'll be added separately).
- Start directly with the intro paragraph.
- Do NOT wrap the output in ```markdown fences.
- Do NOT include images — they'll be inserted later.
- Do NOT include the author bio or "About the author" — added separately.
"""


def call_gemini(api_key: str, prompt: str) -> str:
    models = ["gemini-2.0-flash", "gemini-flash-latest", "gemini-2.5-flash-lite", "gemini-1.5-flash", "gemini-pro-latest"]
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            r = requests.post(url, json=payload, timeout=60)
            if r.status_code == 200:
                res_data = r.json()
                text = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                print(f"[SUCCESS] Generated content via Gemini ({model})!")
                return text
            if r.status_code == 429:
                print(f"[WARN] Gemini model {model} rate limited (429). Trying next model...")
                continue
        except Exception as e:
            print(f"[WARN] Model {model} failed: {e}")
            continue
    raise Exception(f"All Gemini models failed for key ending in ...{api_key[-4:]}")

def call_openai(api_key: str, prompt: str) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    r = requests.post(url, headers={"Authorization": f"Bearer {api_key}"}, json=payload, timeout=120)
    if r.status_code == 200:
        return r.json()["choices"][0]["message"]["content"].strip()
    raise Exception(f"OpenAI API error {r.status_code}: {r.text[:300]}")

def call_groq(api_key: str, prompt: str, max_tokens: int = 4000) -> str:
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You are a senior Java backend engineer and technical writer. Output clean markdown."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": max_tokens,
        "top_p": 0.9,
    }
    for attempt in range(3):
        r = requests.post(
            GROQ_API,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=120,
        )
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
        if r.status_code in (429, 503):
            wait = 5 * (attempt + 1)
            print(f"[WARN] Groq returned {r.status_code}. Retrying in {wait}s...")
            time.sleep(wait)
            continue
        raise Exception(f"Groq API error {r.status_code}: {r.text[:400]}")
    raise Exception("Groq API failed after 3 retries.")

def generate_article_content(prompt: str) -> str:
    groq_key = os.environ.get("GROQ_API_KEY")
    if groq_key:
        try:
            return call_groq(groq_key, prompt)
        except Exception as e:
            print(f"[WARN] Groq failed: {e}. Trying Gemini...")

    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEYS")
    if gemini_key:
        keys = [k.strip() for k in gemini_key.split(",") if k.strip()]
        for k in keys:
            try:
                return call_gemini(k, prompt)
            except Exception as e:
                print(f"[WARN] Gemini key failed: {e}")

    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        try:
            return call_openai(openai_key, prompt)
        except Exception as e:
            print(f"[WARN] OpenAI failed: {e}")

    raise SystemExit("[ERROR] All content generation attempts failed (Groq, Gemini, OpenAI). Missing API keys or rate limited.")


def assemble_article(topic: dict, body: str) -> str:
    """Wrap LLM body with header image, intro frontmatter-style block, and bio footer."""
    today = datetime.date.today().isoformat()
    header_img = unsplash_image(topic["image_query"], 1200, 630, seed=1)
    inline_img = unsplash_image(topic["image_query"], 1000, 500, seed=2)

    alt_text = topic["primary_keyword"].title()
    article = []
    article.append(f"![{alt_text}]({header_img})")
    article.append("")
    article.append(f"> _Published {today} by [Shubham Bhati](https://shubh2-0.github.io) — Backend Engineer (Java 17, Spring Boot, Microservices)._")
    article.append("")
    article.append(body.strip())
    article.append("")
    article.append("---")
    article.append("")
    article.append(f"![{alt_text} in production]({inline_img})")
    article.append("")
    article.append("## Further Reading")
    article.append("")
    article.append("- [Spring Boot Official Documentation](https://docs.spring.io/spring-boot/docs/current/reference/htmlsingle/)")
    article.append("- [Baeldung — Java & Spring Tutorials](https://www.baeldung.com/)")
    article.append("- [Oracle Java Documentation](https://docs.oracle.com/en/java/)")
    article.append("")
    article.append("---")
    article.append("")
    article.append(AUTHOR_BIO)
    article.append("")
    return "\n".join(article)


def save_article(topic: dict, content: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today().isoformat()
    folder = OUTPUT_DIR / f"{today}-{topic['slug']}"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "title.txt").write_text(topic["title"] + "\n", encoding="utf-8")
    (folder / "tags.txt").write_text(", ".join(topic["tags"]) + "\n", encoding="utf-8")
    (folder / "body.md").write_text(content, encoding="utf-8")
    (folder / "meta.json").write_text(json.dumps({
        "slug": topic["slug"],
        "primary_keyword": topic["primary_keyword"],
        "secondary_keywords": topic["secondary_keywords"],
        "published_date": today,
        "tags": topic["tags"],
    }, indent=2), encoding="utf-8")
    return folder


def post_to_devto(api_key: str, title: str, body: str, tags: list[str], description: str) -> dict:
    payload = {"article": {
        "title": title,
        "body_markdown": body,
        "published": True,
        "tags": tags[:4],
        "description": description[:140],
    }}
    r = requests.post(
        DEV_TO_API,
        headers={"api-key": api_key, "Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=60,
    )
    if r.status_code not in (200, 201):
        return {"ok": False, "error": f"HTTP {r.status_code}: {r.text[:300]}"}
    data = r.json()
    return {"ok": True, "url": data.get("url", "?"), "id": data.get("id")}


def post_to_hashnode(token: str, publication_id: str, title: str, body: str, tags: list[str], canonical: str | None) -> dict:
    tag_objects = [{"slug": t.lower().replace(" ", "-"), "name": t} for t in tags[:5]]
    payload_input = {
        "title": title,
        "contentMarkdown": body,
        "tags": tag_objects,
        "publicationId": publication_id,
    }
    if canonical:
        payload_input["originalArticleURL"] = canonical
    mutation = """
    mutation PublishPost($input: PublishPostInput!) {
      publishPost(input: $input) { post { id slug url } }
    }
    """
    r = requests.post(
        HASHNODE_API,
        headers={"Authorization": f"Bearer {token}" if not token.startswith("Bearer ") else token, "Content-Type": "application/json"},
        data=json.dumps({"query": mutation, "variables": {"input": payload_input}}),
        timeout=60,
    )
    if r.status_code != 200:
        return {"ok": False, "error": f"HTTP {r.status_code}: {r.text[:300]}"}
    j = r.json()
    if "errors" in j:
        return {"ok": False, "error": str(j["errors"])[:300]}
    post = j.get("data", {}).get("publishPost", {}).get("post", {})
    return {"ok": True, "url": post.get("url", "?"), "id": post.get("id")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", help="Force a specific topic slug")
    ap.add_argument("--dry-run", action="store_true", help="Print prompt, skip API")
    ap.add_argument("--no-publish", action="store_true", help="Generate + save, skip publishing")
    args = ap.parse_args()

    topics = load_topics()
    history = load_history()
    topic = pick_topic(topics, history, args.slug)

    print(f"\n=== Selected topic ===\nSlug: {topic['slug']}\nTitle: {topic['title']}\n")

    if args.dry_run:
        print(build_prompt(topic))
        return

    print("[1/3] Generating article via Groq / Gemini / OpenAI...")
    body = generate_article_content(build_prompt(topic))
    print(f"      Generated {len(body.split())} words.\n")

    article = assemble_article(topic, body)
    folder = save_article(topic, article)
    print(f"[2/3] Saved to: {folder}")

    if args.no_publish:
        print("\n[skip] --no-publish set. Done.")
        return

    # Meta description = first 140 chars from body, stripped
    description = topic["search_intent"][:140]
    canonical = None

    devto_key = os.environ.get("DEV_TO_API_KEY")
    if devto_key:
        print("[3/3] Publishing to Dev.to...")
        r = post_to_devto(devto_key, topic["title"], article, topic["tags"], description)
        if r["ok"]:
            print(f"      [OK]   {r['url']}")
            canonical = r["url"]
        else:
            print(f"      [FAIL] {r['error']}")
    else:
        print("[3/3] Skipped Dev.to (DEV_TO_API_KEY not set)")

    hn_token = os.environ.get("HASHNODE_TOKEN")
    hn_pub = os.environ.get("HASHNODE_PUBLICATION_ID")
    if hn_token and hn_pub:
        print("      Publishing to Hashnode...")
        r = post_to_hashnode(hn_token, hn_pub, topic["title"], article, topic["tags"], canonical)
        if r["ok"]:
            print(f"      [OK]   {r['url']}")
        else:
            print(f"      [FAIL] {r['error']}")
    else:
        print("      Skipped Hashnode (HASHNODE_TOKEN / HASHNODE_PUBLICATION_ID not set)")

    history["published"].append({
        "slug": topic["slug"],
        "title": topic["title"],
        "date": datetime.date.today().isoformat(),
    })
    save_history(history)
    print("\nDone. Topic added to history.")


if __name__ == "__main__":
    main()

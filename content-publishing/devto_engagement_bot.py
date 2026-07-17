import os
import json
import random
import time
import requests
import re
from pathlib import Path

# Enforce no Oxford comma rule
_OXFORD_COMMA_RE = re.compile(r',\s+and\b')
def strip_oxford_comma(text):
    return _OXFORD_COMMA_RE.sub(' and', text)

CACHE_FILE = Path(__file__).parent / "devto_engagement_cache.json"

TAGS_TO_SCAN = ["springboot", "java", "microservices", "database", "redis", "kafka", "backend"]

FORBIDDEN_WORDS = [
    "delve", "tapestry", "crucial", "vital", "robust", "leverage", "paradigm",
    "ecosystem", "seamless", "game-changer", "indeed", "additionally", "furthermore",
    "thus", "hence", "consequently", "key takeaway", "remember to", "demystify", "testament"
]


def load_cache():
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"commented_articles": []}


def save_cache(cache):
    CACHE_FILE.write_text(json.dumps(cache, indent=2), encoding="utf-8")


def call_groq(api_key, title, body_snippet):
    url = "https://api.groq.com/openai/v1/chat/completions"
    system_instruction = (
        "You are Shubham Bhati, a senior Java Spring Boot & Backend Engineer. "
        "You write crisp, direct, conversational comments on technical posts. "
        "Share a practical engineering perspective, edge case or real-world backend tip related to the article."
    )
    prompt = (
        f"Article Title: {title}\n"
        f"Article Excerpt: {body_snippet[:800]}\n\n"
        "Write a short, high-value developer comment (40-70 words).\n"
        "Rules:\n"
        "1. Write in a casual, direct engineer-to-engineer tone.\n"
        "2. Do NOT say 'Great post!', 'Thanks for sharing!', 'Nice article!' or corporate fluff.\n"
        "3. STRICT RULE: NO Oxford commas (write 'Spring Boot, Kafka and Redis').\n"
        "4. STRICT RULE: Avoid AI words (delve, tapestry, crucial, vital, robust, leverage, paradigm, ecosystem, seamless, game-changer, indeed, additionally, furthermore, thus, hence, consequently, key takeaway, demystify).\n"
        "5. Use natural contractions (don't, can't, it's, we've).\n"
        "6. Return ONLY the comment text."
    )

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 150
    }
    r = requests.post(url, headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, json=payload, timeout=20)
    if r.status_code == 200:
        comment = r.json()["choices"][0]["message"]["content"].strip()
        return strip_oxford_comma(comment)
    return None


def call_gemini(api_key, title, body_snippet):
    models = ["gemini-2.0-flash", "gemini-flash-latest"]
    system_instruction = (
        "You are Shubham Bhati, a Java Spring Boot Engineer. "
        "Write a short, insightful backend developer comment on this post."
    )
    prompt = (
        f"Article Title: {title}\n"
        f"Article Excerpt: {body_snippet[:800]}\n\n"
        "Write a short developer comment (40-70 words).\n"
        "Rules:\n"
        "1. Direct engineer tone.\n"
        "2. NO intro fluff like 'Great post!'.\n"
        "3. NO Oxford commas.\n"
        "4. NO AI buzzwords (delve, tapestry, crucial, vital, robust, leverage, paradigm, ecosystem, seamless, game-changer).\n"
        "5. Use natural contractions.\n"
        "6. Return ONLY the comment text."
    )
    payload = {"contents": [{"parts": [{"text": f"{system_instruction}\n\n{prompt}"}]}]}
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            r = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=20)
            if r.status_code == 200:
                text = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                return strip_oxford_comma(text)
        except Exception:
            pass
    return None


def call_openai(api_key, title, body_snippet):
    url = "https://api.openai.com/v1/chat/completions"
    system_instruction = (
        "You are Shubham Bhati, a Java Spring Boot Engineer. "
        "Write a short, insightful backend developer comment on this post."
    )
    prompt = (
        f"Article Title: {title}\n"
        f"Article Excerpt: {body_snippet[:800]}\n\n"
        "Write a short developer comment (40-70 words).\n"
        "Rules:\n"
        "1. Direct engineer tone.\n"
        "2. NO intro fluff like 'Great post!'.\n"
        "3. NO Oxford commas.\n"
        "4. NO AI buzzwords.\n"
        "5. Use natural contractions.\n"
        "6. Return ONLY the comment text."
    )
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 150
    }
    try:
        r = requests.post(url, headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, json=payload, timeout=20)
        if r.status_code == 200:
            text = r.json()["choices"][0]["message"]["content"].strip()
            return strip_oxford_comma(text)
    except Exception as e:
        print(f"[WARN] OpenAI failed: {e}")
    return None


def generate_comment(title, body_snippet):
    # Try Groq first (fastest, free)
    groq_key = os.environ.get("GROQ_API_KEY")
    if groq_key:
        try:
            res = call_groq(groq_key, title, body_snippet)
            if res:
                print("  [LLM] Comment generated via Groq.")
                return res
        except Exception as e:
            print(f"[WARN] Groq failed: {e}")

    # Try Gemini (free tier)
    gemini_key = os.environ.get("GEMINI_API_KEY") or ""
    if not gemini_key:
        keys_str = os.environ.get("GEMINI_API_KEYS", "")
        gemini_key = keys_str.split(",")[0].strip() if keys_str else ""
    if gemini_key:
        try:
            res = call_gemini(gemini_key, title, body_snippet)
            if res:
                print("  [LLM] Comment generated via Gemini.")
                return res
        except Exception as e:
            print(f"[WARN] Gemini failed: {e}")

    # Try OpenAI as final fallback
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        try:
            res = call_openai(openai_key, title, body_snippet)
            if res:
                print("  [LLM] Comment generated via OpenAI.")
                return res
        except Exception as e:
            print(f"[WARN] OpenAI fallback failed: {e}")

    print("  [WARN] All LLM providers failed or no API keys set.")
    return None


def fetch_trending_articles():
    tag = random.choice(TAGS_TO_SCAN)
    url = f"https://dev.to/api/articles?tag={tag}&top=7"
    print(f"[*] Searching DEV.to articles for tag: '{tag}'...")
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"[ERROR] Failed to fetch articles: {e}")
    return []


def react_to_article(api_key, article_id):
    url = "https://dev.to/api/reactions"
    category = random.choice(["like", "unicorn", "readinglist"])
    payload = {
        "category": category,
        "reactable_id": article_id,
        "reactable_type": "Article"
    }
    try:
        r = requests.post(url, headers={"api-key": api_key, "Content-Type": "application/json"}, json=payload, timeout=15)
        if r.status_code in (200, 201):
            print(f"  [Reaction] Liked article {article_id} with category '{category}'")
            return True
        else:
            print(f"  [Reaction Status] {r.status_code}: {r.text[:100]}")
    except Exception as e:
        print(f"  [Reaction Error] {e}")
    return False


def post_comment(api_key, article_id, comment_body):
    url = "https://dev.to/api/comments"
    payload = {
        "comment": {
            "body_markdown": comment_body,
            "commentable_id": article_id,
            "commentable_type": "Article"
        }
    }
    try:
        r = requests.post(url, headers={"api-key": api_key, "Content-Type": "application/json"}, json=payload, timeout=15)
        if r.status_code in (200, 201):
            print(f"  [Comment Posted] Successfully commented on article {article_id}")
            return True
        else:
            print(f"  [Comment Failed] {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"  [Comment Exception] {e}")
    return False


def main():
    devto_key = os.environ.get("DEV_TO_API_KEY")
    if not devto_key:
        print("[ERROR] DEV_TO_API_KEY not set. Exiting.")
        return

    cache = load_cache()
    commented_ids = set(cache.get("commented_articles", []))

    articles = fetch_trending_articles()
    if not articles:
        print("[WARN] No articles found.")
        return

    engaged_count = 0
    max_engagement = 1  # 1 high-quality interaction per run (100% human-safe)

    for article in articles:
        if engaged_count >= max_engagement:
            break

        article_id = article.get("id")
        title = article.get("title", "")
        author_username = article.get("user", {}).get("username", "").lower()

        # Skip self or already commented articles
        if not article_id or article_id in commented_ids or author_username in ["shubham_bhati", "shubh2-0"]:
            continue

        print(f"\nTarget Article ID: {article_id} | Title: '{title}' by @{author_username}")

        snippet = article.get("description", "") or title
        comment = generate_comment(title, snippet)

        if not comment:
            print("  [SKIP] Could not generate comment.")
            continue

        # Enforce word filter safety
        has_forbidden = any(word in comment.lower() for word in FORBIDDEN_WORDS)
        if has_forbidden:
            print("  [WARN] Comment contained forbidden word. Regenerating or skipping.")
            continue

        print(f"  Generated Comment:\n  \"{comment}\"\n")

        # 1. React to article
        react_to_article(devto_key, article_id)

        time.sleep(random.uniform(5, 12))  # Human delay

        # 2. Post comment
        success = post_comment(devto_key, article_id, comment)
        if success:
            commented_ids.add(article_id)
            cache["commented_articles"] = list(commented_ids)
            save_cache(cache)
            engaged_count += 1
            print("  State updated and cached.")

    print(f"\nCycle finished. Total engaged: {engaged_count}")


if __name__ == "__main__":
    main()

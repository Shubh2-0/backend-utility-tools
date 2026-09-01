"""
Daily Java/Spring Boot tip generator using Groq's free Llama 3.3 70B API.

Generates one short technical tip per run, in Shubham's voice.
Designed to run via GitHub Actions cron (daily) to keep your content fresh.

Setup:
    Get a free Groq API key (no credit card): https://console.groq.com/keys

Usage:
    GROQ_API_KEY=gsk_... python daily-tip.py
    GROQ_API_KEY=gsk_... python daily-tip.py --post-to devto
    GROQ_API_KEY=gsk_... python daily-tip.py --dry-run
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

GROQ_API = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

TOPIC_POOL = [
    "Spring Boot autoconfiguration internals",
    "Hibernate N+1 problem and fixes",
    "Java records vs Lombok",
    "Spring Data JPA dynamic queries",
    "RabbitMQ vs SQS for microservices",
    "OAuth 2.0 + JWT in Spring Security",
    "Redis caching patterns in Spring Boot",
    "MySQL EXPLAIN ANALYZE walkthrough",
    "Docker multi-stage builds for Spring Boot",
    "GitHub Actions for Java CI/CD",
    "Pattern matching in Java 21",
    "Sealed classes and pattern matching",
    "Java memory model basics",
    "JVM garbage collection tuning",
    "Optimistic vs pessimistic locking in MySQL",
    "Idempotency patterns for REST APIs",
    "Saga pattern vs 2PC for distributed transactions",
    "Connection pooling with HikariCP",
    "Spring Cache abstraction in production",
    "Spring AOP practical use cases",
    "Structured logging in Spring Boot",
    "Micrometer + Prometheus integration",
    "When to use Spring WebFlux",
    "MapStruct for object mapping",
    "Liquibase vs Flyway migrations",
    "REST API versioning strategies",
    "Rate limiting with bucket4j + Redis",
    "Circuit breaker with Resilience4j",
    "Spring Profiles in production",
    "Testcontainers for integration tests",
    "Spring Cloud Gateway routing tricks",
    "OpenAI integration in Spring Boot",
    "Java virtual threads vs platform threads",
    "MySQL indexing strategies",
    "Kafka consumer offset management",
    "Spring Security OAuth2 resource server",
    "MongoDB vs MySQL for read-heavy workloads",
    "GraphQL vs REST for backend APIs",
    "Spring Boot Actuator custom endpoints",
    "Building AI chatbots in Spring Boot",
]


def generate_tip(api_key: str) -> dict:
    topic = random.choice(TOPIC_POOL)
    prompt = f"""Write a short, punchy LinkedIn-style technical post (180-280 words) about: {topic}

Voice: Shubham Bhati — Backend Engineer at MobilePe Fintech, 3+ years experience, based in Noida, India. Specializes in Java 17/21, Spring Boot, microservices, MySQL, AWS, AI integration.

Style rules:
- Strong hook on the FIRST line (a number, a contrarian take, or a specific bug)
- Concrete + actionable (no fluff)
- Include a 3-6 line code snippet if relevant (use ```java ... ``` or ```sql ... ``` fences)
- End with a question to drive comments
- Conversational, slightly opinionated
- No "Title:" or "Hook:" labels — just the post itself
- Don't use the words "leverage", "synergy", "delve", "moreover", or "robust"
- Hindi/English mix is OK occasionally for emphasis (like "scale pe", "production me")

Output ONLY the post text. No metadata."""

    for attempt in range(3):
        r = requests.post(
            GROQ_API,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            data=json.dumps({
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.85,
                "max_tokens": 600,
            }),
            timeout=60,
        )
        if r.status_code == 200:
            content = r.json()["choices"][0]["message"]["content"].strip()
            return {"topic": topic, "body": content}
        if r.status_code in (429, 503):
            wait = 5 * (attempt + 1)
            print(f"[WARN] Groq returned {r.status_code}. Retrying in {wait}s...")
            time.sleep(wait)
            continue
        print(f"Groq error: {r.status_code} {r.text[:300]}")
        sys.exit(1)

    print("Groq API failed after 3 retries.")
    sys.exit(1)


def save_tip(tip: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today().isoformat()
    file = out_dir / f"{today}.md"
    with file.open("w", encoding="utf-8") as f:
        f.write(f"# {tip['topic']}\n\n")
        f.write(f"_Generated {today}_\n\n")
        f.write(tip["body"])
        f.write("\n\n---\n\n*By Shubham Bhati — Backend Engineer at AlignBits LLC. [Portfolio](https://shubh2-0.github.io) · [LinkedIn](https://linkedin.com/in/bhatishubham) · [GitHub](https://github.com/Shubh2-0)*\n")
    return file


def split_into_tweets(text: str, max_len: int = 270) -> list[str]:
    """Splits a markdown text body into a list of tweets, each fitting the 280-char limit."""
    # Split by paragraphs first
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    tweets = []
    
    current_tweet = ""
    for para in paragraphs:
        # If adding the paragraph fits, group them to minimize tweets count
        if len(current_tweet) + len(para) + 2 <= max_len:
            if current_tweet:
                current_tweet += "\n\n" + para
            else:
                current_tweet = para
        else:
            if current_tweet:
                tweets.append(current_tweet)
            current_tweet = para
            
            # If a single paragraph is longer than max_len, split it by sentence boundaries
            while len(current_tweet) > max_len:
                split_idx = current_tweet.rfind(". ", 0, max_len)
                if split_idx == -1:
                    split_idx = current_tweet.rfind(" ", 0, max_len)
                if split_idx == -1:
                    split_idx = max_len
                    
                tweets.append(current_tweet[:split_idx].strip())
                current_tweet = current_tweet[split_idx:].strip()
                
    if current_tweet:
        tweets.append(current_tweet)
        
    # Append thread pagination suffix like " (1/3)"
    if len(tweets) > 1:
        numbered_tweets = []
        for idx, t in enumerate(tweets):
            suffix = f" ({idx+1}/{len(tweets)})"
            if len(t) + len(suffix) <= 280:
                numbered_tweets.append(t + suffix)
            else:
                numbered_tweets.append(t[:280-len(suffix)] + suffix)
        return numbered_tweets
    return tweets


def post_to_twitter(consumer_key: str, consumer_secret: str, access_token: str, access_token_secret: str, text: str):
    """Post tweet thread to Twitter (X) using Tweepy Client (API v2)."""
    try:
        import tweepy
    except ImportError:
        print("[FAIL] Tweepy not installed. Tweeting skipped. Run 'pip install tweepy'.")
        return
        
    try:
        session = requests.Session()
        orig_request = session.request
        def request_with_timeout(*args, **kwargs):
            if 'timeout' not in kwargs or kwargs['timeout'] is None:
                kwargs['timeout'] = 15
            return orig_request(*args, **kwargs)
        session.request = request_with_timeout

        client = tweepy.Client(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            session=session
        )
        
        tweets = split_into_tweets(text)
        print(f"Prepared Twitter thread of {len(tweets)} tweets.")
        
        previous_id = None
        for i, tweet_text in enumerate(tweets):
            if previous_id is None:
                resp = client.create_tweet(text=tweet_text)
            else:
                resp = client.create_tweet(text=tweet_text, in_reply_to_tweet_id=previous_id)
            
            previous_id = resp.data["id"]
            print(f"  [OK] Posted Tweet {i+1}/{len(tweets)}: ID {previous_id}")
            time.sleep(1.5)  # Pause to respect rate limits and order
            
        print("  [OK] Twitter Thread posted successfully!")
    except Exception as e:
        print(f"  [FAIL] Twitter: {e}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--post-to", choices=["devto", "hashnode", "both"], default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    key = os.environ.get("GROQ_API_KEY")
    if not key:
        print("GROQ_API_KEY not set. Get one free at https://console.groq.com/keys")
        sys.exit(1)

    tip = generate_tip(key)
    print(f"\n=== Topic: {tip['topic']} ===\n")
    print(tip["body"])
    print()

    if args.dry_run:
        print("[DRY RUN] Not saving or posting.")
        return

    out = save_tip(tip, Path(__file__).parent / "daily-tips")
    print(f"Saved: {out}")

    if args.post_to in ("devto", "both"):
        devto_key = os.environ.get("DEV_TO_API_KEY")
        if devto_key:
            r = requests.post(
                "https://dev.to/api/articles",
                headers={"api-key": devto_key, "Content-Type": "application/json"},
                data=json.dumps({
                    "article": {
                        "title": tip["topic"],
                        "body_markdown": tip["body"],
                        "published": True,
                        "tags": ["java", "springboot", "backend", "tutorial"],
                    }
                }),
                timeout=30,
            )
            if r.status_code in (200, 201):
                print(f"[OK] Dev.to: {r.json().get('url', '?')}")
            else:
                print(f"[FAIL] Dev.to: {r.text[:300]}")

    if args.post_to in ("hashnode", "both"):
        hn_token = os.environ.get("HASHNODE_TOKEN")
        hn_pub = os.environ.get("HASHNODE_PUBLICATION_ID")
        if hn_token and hn_pub:
            tags = [{"slug": "java", "name": "Java"}, {"slug": "springboot", "name": "Spring Boot"}]
            r = requests.post(
                "https://gql.hashnode.com/",
                headers={"Authorization": f"Bearer {hn_token}" if not hn_token.startswith("Bearer ") else hn_token, "Content-Type": "application/json"},
                data=json.dumps({
                    "query": "mutation Pub($i:PublishPostInput!){publishPost(input:$i){post{url}}}",
                    "variables": {"i": {
                        "title": tip["topic"],
                        "contentMarkdown": tip["body"],
                        "tags": tags,
                        "publicationId": hn_pub,
                    }}
                }),
                timeout=30,
            )
            j = r.json()
            if "errors" in j:
                print(f"[FAIL] Hashnode: {j['errors']}")
            else:
                url = j.get("data", {}).get("publishPost", {}).get("post", {}).get("url", "?")
                print(f"[OK] Hashnode: {url}")

    # Twitter (X) Integration
    tw_ck = os.environ.get("TWITTER_CONSUMER_KEY")
    tw_cs = os.environ.get("TWITTER_CONSUMER_SECRET")
    tw_at = os.environ.get("TWITTER_ACCESS_TOKEN")
    tw_ats = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

    if tw_ck and tw_cs and tw_at and tw_ats:
        print("Posting to Twitter (X)...")
        # Strip final markdown signature link for clean Twitter text
        clean_text = tip["body"]
        post_to_twitter(tw_ck, tw_cs, tw_at, tw_ats, clean_text)
    else:
        print("[SKIP] Twitter (X) credentials not fully set.")


if __name__ == "__main__":
    main()

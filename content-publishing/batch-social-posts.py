"""
Batch-generate LinkedIn + Twitter posts using Groq.

Usage:
    GROQ_API_KEY=gsk_... python batch-social-posts.py linkedin 30
    GROQ_API_KEY=gsk_... python batch-social-posts.py twitter 30

Outputs:
    Appends to linkedin-posts.md or twitter-posts.md.
"""

import json
import os
import random
import sys
import time
from pathlib import Path

import requests

GROQ_API = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

LINKEDIN_TOPICS = [
    "Spring Boot startup time optimization",
    "Hibernate session management in production",
    "Java record vs Lombok @Value debate",
    "MySQL composite index tricks",
    "Redis caching with Spring @Cacheable",
    "OAuth 2.0 PKCE flow in Spring Security",
    "Spring Cloud Gateway rate limiting",
    "Kafka consumer rebalance issues",
    "Microservices observability with traces",
    "Spring Profiles for environments",
    "RestTemplate vs WebClient comparison",
    "JPA entity lifecycle gotchas",
    "Spring Boot Docker layered JAR",
    "Database connection leak debugging",
    "Spring Async vs CompletableFuture",
    "Idempotency keys for payment APIs",
    "Spring Retry vs Resilience4j",
    "MySQL query plan analysis",
    "Spring Boot Actuator endpoint security",
    "Testcontainers for integration tests",
    "Java 21 virtual threads in production",
    "Spring Boot circular dependency fix",
    "MapStruct vs manual mapping",
    "Spring Data Specification builder",
    "Hibernate dirty checking performance",
    "Spring Boot graceful shutdown",
    "WebClient connection pool tuning",
    "Spring Boot custom HealthIndicator",
    "API rate limiting with bucket4j",
    "MySQL transaction isolation in Spring",
    "Spring Boot ProblemDetail (RFC 7807)",
    "Hibernate second-level cache pitfalls",
    "Spring Cloud Config refresh scope",
    "AWS SDK v2 with Spring Boot",
    "Spring Boot K8s liveness vs readiness",
    "Kafka exactly-once semantics in Spring",
    "Spring Security method-level auth",
    "MySQL row-level locking patterns",
    "Spring Boot @Scheduled vs Quartz",
    "OpenAI integration retry strategies",
]

TWITTER_TOPICS = [
    "Spring Boot tip of the day",
    "Java 21 cool feature",
    "MySQL gotcha you didn't know",
    "Microservices anti-pattern",
    "Spring Security pitfall",
    "JPA performance trick",
    "Docker for Spring Boot",
    "Production debugging story",
    "Code review nitpick worth fixing",
    "Backend architecture decision",
    "Kafka consumer group tip",
    "Redis caching mistake to avoid",
    "Spring Cloud lesson",
    "Hibernate query optimization",
    "Spring Boot 3.2 feature",
    "REST API design tip",
    "Java concurrency basics",
    "AWS deployment lesson",
    "OpenAI API gotcha in Java",
    "Resilience4j config sane defaults",
    "MySQL index when to add",
    "GraphQL vs REST take",
    "Testing strategy that worked",
    "Junior to senior transition advice",
    "Backend interview red flag",
    "Spring config best practice",
    "AI integration in legacy Java",
    "Refactoring win this week",
    "Documentation that saved hours",
    "Open-source library worth knowing",
    "Career growth tip for engineers",
    "Linux command for Java devs",
    "Maven vs Gradle hot take",
    "Spring Boot startup time win",
    "Production incident root cause",
    "API versioning lesson",
    "Database migration tip",
    "Distributed tracing setup",
    "Logging that actually helped",
    "Tech debt prioritization framework",
]


def call_groq(api_key: str, prompt: str, max_tokens: int = 500) -> str:
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You are a senior Java backend engineer who writes engaging LinkedIn and Twitter posts. Output ONLY the post text, no metadata."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.92,
        "max_tokens": max_tokens,
        "top_p": 0.9,
    }
    for attempt in range(3):
        r = requests.post(
            GROQ_API,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=60,
        )
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
        if r.status_code in (429, 503):
            wait = 5 * (attempt + 1)
            print(f"      [WARN] {r.status_code}, retry in {wait}s")
            time.sleep(wait)
            continue
        print(f"Groq error: {r.status_code} {r.text[:200]}")
        sys.exit(1)
    sys.exit("Groq failed after retries.")


def linkedin_prompt(topic: str, index: int) -> str:
    style_variants = [
        "Start with a contrarian opinion. Mid-section with 3 bullet points. End with a question.",
        "Open with a specific production number. Tell a 5-line story. End with one practical takeaway.",
        "Use a 'I was wrong about X' confessional tone. 2 paragraphs.",
        "Numbered list of 5 lessons. Each lesson 1-2 lines.",
        "Start with a code snippet. Then explain why it matters in 3 lines.",
    ]
    style = style_variants[index % len(style_variants)]
    return f"""Write ONE LinkedIn post (180-260 words) about: {topic}

Voice: Shubham Bhati — Backend Engineer at AlignBits LLC, 3+ years experience, builds Java/Spring/microservices in production.

Style this post: {style}

Rules:
- Strong hook on the FIRST line
- Concrete numbers, version specifics (Java 21, Spring Boot 3.2)
- Include a code snippet only if relevant (```java fence, 3-6 lines)
- End with a single question to drive comments
- No marketing speak, no "leverage/synergy/delve/moreover/robust"
- Hindi/English mix OK occasionally for emphasis
- NO hashtags except the very last line (max 3 hashtags)

Output ONLY the post body. No labels like "Post:" or "Title:"."""


def twitter_prompt(topic: str, index: int) -> str:
    formats = [
        "single tweet (220-270 chars)",
        "single tweet (220-270 chars)",
        "thread of 3 tweets (each 220-270 chars, separated by '---' on its own line)",
        "single tweet (220-270 chars) with a 2-line code snippet",
        "single tweet (220-270 chars) ending with a question",
    ]
    fmt = formats[index % len(formats)]
    return f"""Write {fmt} about: {topic}

Voice: Shubham Bhati — Backend Engineer, Java 21 / Spring Boot / MySQL / microservices.

Rules:
- Specific, opinionated, no fluff
- Numbers and version specifics OK
- No marketing speak
- No hashtags (or max 1)
- For threads: put "---" on its own line between tweets

Output ONLY the tweet text(s)."""


def main():
    if len(sys.argv) < 3:
        print("Usage: python batch-social-posts.py [linkedin|twitter] <count>")
        sys.exit(1)

    kind = sys.argv[1]
    count = int(sys.argv[2])

    key = os.environ.get("GROQ_API_KEY")
    if not key:
        sys.exit("GROQ_API_KEY not set")

    batch = sys.argv[3] if len(sys.argv) > 3 else "batch2"
    if kind == "linkedin":
        out_file = Path(__file__).parent / f"linkedin-posts-{batch}.md"
        topics = random.sample(LINKEDIN_TOPICS, min(count, len(LINKEDIN_TOPICS)))
        prompt_fn = linkedin_prompt
        header = f"# LinkedIn Posts — {batch.title()} (Groq-generated)\n\n"
    elif kind == "twitter":
        out_file = Path(__file__).parent / f"twitter-posts-{batch}.md"
        topics = random.sample(TWITTER_TOPICS, min(count, len(TWITTER_TOPICS)))
        prompt_fn = twitter_prompt
        header = f"# Twitter Posts — {batch.title()} (Groq-generated)\n\n"
    else:
        sys.exit(f"Unknown kind: {kind}")

    posts = []
    print(f"Generating {count} {kind} posts...\n")
    for i, topic in enumerate(topics, 1):
        print(f"  [{i}/{count}] {topic}")
        body = call_groq(key, prompt_fn(topic, i))
        posts.append((i, topic, body))
        time.sleep(2)  # respect rate limits

    with out_file.open("w", encoding="utf-8") as f:
        f.write(header)
        for i, topic, body in posts:
            f.write(f"\n---\n\n## Post {i}: {topic}\n\n{body}\n")

    print(f"\nDone. Wrote {len(posts)} posts to {out_file}")


if __name__ == "__main__":
    main()

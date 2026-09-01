"""
Pre-generate N daily tips, dated for the next N days starting tomorrow.
Stores in daily-tips/<future-date>.md so the daily cron has a backlog
ready to be referenced if generation fails on a given day.
"""

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


def call_groq(api_key: str, prompt: str) -> str:
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.88,
        "max_tokens": 500,
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
            time.sleep(5 * (attempt + 1))
            continue
        sys.exit(f"Groq error: {r.status_code} {r.text[:200]}")
    sys.exit("Groq failed.")


def tip_prompt(topic: str) -> str:
    return f"""Write a short, punchy LinkedIn-style technical post (180-280 words) about: {topic}

Voice: Shubham Bhati — Backend Engineer at MobilePe Fintech, 3+ years experience, based in Noida, India. Java 17/21, Spring Boot, MySQL, AWS, AI integration.

Rules:
- Strong hook on the FIRST line
- Concrete + actionable (no fluff)
- Include a 3-6 line code snippet if relevant (```java ... ``` fences)
- End with a question
- No marketing speak, no "leverage/synergy/delve/moreover/robust"
- Output ONLY the post text. No labels."""


def main():
    if len(sys.argv) < 2:
        print("Usage: python batch-daily-tips.py <count>")
        sys.exit(1)
    count = int(sys.argv[1])

    key = os.environ.get("GROQ_API_KEY")
    if not key:
        sys.exit("GROQ_API_KEY not set")

    out_dir = Path(__file__).parent / "daily-tips"
    out_dir.mkdir(parents=True, exist_ok=True)

    base = datetime.date.today() + datetime.timedelta(days=1)
    topics_used = random.sample(TOPIC_POOL, count)

    for i in range(count):
        date = base + datetime.timedelta(days=i)
        topic = topics_used[i]
        target = out_dir / f"{date.isoformat()}.md"
        print(f"[{i+1}/{count}] {date} — {topic}")
        body = call_groq(key, tip_prompt(topic))
        with target.open("w", encoding="utf-8") as f:
            f.write(f"# {topic}\n\n")
            f.write(f"_Pre-generated for {date.isoformat()}_\n\n")
            f.write(body)
            f.write(
                "\n\n---\n\n*By Shubham Bhati — Backend Engineer at AlignBits LLC. "
                "[Portfolio](https://shubh2-0.github.io) · "
                "[LinkedIn](https://linkedin.com/in/bhatishubham) · "
                "[GitHub](https://github.com/Shubh2-0)*\n"
            )
        time.sleep(2)

    print(f"\nDone. Wrote {count} tips to {out_dir}")


if __name__ == "__main__":
    main()

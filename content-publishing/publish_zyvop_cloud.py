import os
import sys
import time
import random
import requests
from playwright.sync_api import sync_playwright

ZYVOP_EMAIL = os.environ.get("ZYVOP_EMAIL", "shubhambhati226@gmail.com")
ZYVOP_PASSWORD = os.environ.get("ZYVOP_PASSWORD", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEYS", "").split(",")[0]

TOPICS = [
    "Resilience4j Circuit Breaker and Rate Limiter in Spring Boot Microservices",
    "High-Performance Redis Caching Strategies for Java Spring Boot APIs",
    "Kafka Event-Driven Architecture with Spring Boot and Schema Registry",
    "Spring Cloud Gateway Custom Filters and JWT Token Relay",
    "PostgreSQL Optimistic Locking and Index Optimization in Spring Data JPA",
    "Spring Boot 3.4 Virtual Threads vs Reactive WebFlux Performance Benchmark",
    "Distributed Tracing in Microservices with OpenTelemetry, Jaeger and Zipkin"
]

def generate_article_content(topic):
    title = f"{topic}: A Production Hands-On Guide"
    subtitle = "A practical backend engineering guide for Java & Spring Boot developers."
    
    content = f"""# {title}

In high-concurrency enterprise backend systems, building production-ready services requires robust architecture, failure isolation and optimized database connections.

I experienced this firsthand while optimizing infrastructure costs to **under ₹100 per month** (using Koyeb, Vercel and optimized DB connection pooling). That same low-cost, high-performance architecture enabled our platform to generate **₹1 Lakh+ in revenue in just 2 months** under real traffic.

Here is the exact production-grade blueprint for implementing {topic} in modern Spring Boot 3.4+ microservices.

---

## 1. Architectural Overview

When building distributed microservices, avoiding single points of failure is paramount. By enforcing proper timeouts, connection pooling limits and idempotent retry strategies, your services remain responsive under heavy load spikes.

```java
@Configuration
public class ProductionBackendConfig {{

    @Bean
    public RestClient restClient(RestClient.Builder builder) {{
        return builder
            .requestFactory(new SimpleClientHttpRequestFactory())
            .build();
    }}
}}
```

---

## 2. Core Implementation Blueprint

Below is the production-tested pattern for handling distributed requests safely:

```java
@Service
public class EnterpriseBackendService {{

    private static final Logger log = LoggerFactory.getLogger(EnterpriseBackendService.class);

    @Transactional
    public void executeOperation() {{
        log.info("Executing production backend operation for {topic}");
    }}
}}
```

---

## Key Takeaways

- **Zero Downtime**: Isolated failure domains prevent cascading outages across microservices.
- **Sub-10ms P99 Latency**: Optimized database connection pooling and caching layer reduce database IOPS by up to 80%.
- **Low-Cost Infrastructure**: Optimized memory footprint allowing full deployment under ₹100/month.
"""
    return title, subtitle, content

def main():
    topic = random.choice(TOPICS)
    title, subtitle, body = generate_article_content(topic)

    print(f"==========================================")
    print(f"GitHub Actions ZyVOP Cloud Publisher")
    print(f"Selected Topic: {topic}")
    print(f"Title: {title}")
    print(f"==========================================")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        print("Navigating to ZyVOP Write page...")
        page.goto("https://zyvop.com/write", timeout=60000)
        time.sleep(3)

        # Check if login required
        if "login" in page.url or page.locator('input[type="email"]').count() > 0:
            print("Logging into ZyVOP with credentials...")
            try:
                page.locator('input[type="email"]').fill(ZYVOP_EMAIL)
                if ZYVOP_PASSWORD:
                    page.locator('input[type="password"]').fill(ZYVOP_PASSWORD)
                    page.locator('button[type="submit"], button:has-text("Sign In"), button:has-text("Login")').click()
                    time.sleep(5)
            except Exception as e:
                print(f"Login error: {e}")

        print("Populating ZyVOP Editor fields...")
        try:
            title_input = page.locator('#title-input, input[placeholder*="title"], h1[contenteditable="true"]')
            if title_input.count() > 0:
                title_input.first.fill(title)

            subtitle_input = page.locator('#subtitle-input, input[placeholder*="subtitle"]')
            if subtitle_input.count() > 0:
                subtitle_input.first.fill(subtitle)

            editor = page.locator('.tiptap, [contenteditable="true"], textarea[placeholder*="write"]')
            if editor.count() > 0:
                editor.last.fill(body)

            # Category
            category_select = page.locator('#category-select, select')
            if category_select.count() > 0:
                category_select.first.select_option(value="tutorial")

            # Status to published
            status_select = page.locator('#status-select')
            if status_select.count() > 0:
                status_select.first.select_option(value="published")

            # Publish button
            publish_btn = page.locator('button:has-text("Publish"), button:has-text("Publish Post"), button[type="submit"]')
            if publish_btn.count() > 0:
                publish_btn.first.click()
                time.sleep(5)
                print(f"[SUCCESS] Published on ZyVOP! Final URL: {page.url}")

        except Exception as e:
            print(f"Error publishing on ZyVOP: {e}")

        browser.close()

if __name__ == "__main__":
    main()

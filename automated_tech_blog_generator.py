"""
100% Free Technical Blog & Content Generator Engine for Backend Engineers
Generates human-toned Markdown blogs for DEV.to, Hashnode, Medium & LinkedIn.
Author: Shubham Bhati
"""

import os
import json
import argparse
from pathlib import Path

DEFAULT_TEMPLATES = {
    "kafka_resilience": {
        "title": "Scaling Event-Driven Microservices: Kafka Lag, Redis Idempotency and Transactional Outbox",
        "tags": ["springboot", "java", "kafka", "redis"],
        "content": """
Mastering high-throughput event-driven microservices requires more than just launching Kafka producers. In production environments processing high transaction volumes, network glitches and consumer delays can cause duplicate event consumption and data inconsistency.

Here is how we optimized our backend pipeline using Spring Boot 3.4, Apache Kafka, Redis idempotency keys and the Transactional Outbox Pattern:

### 1. The Transactional Outbox Pattern
Instead of publishing events directly to Kafka within a database `@Transactional` block (which risks partial failures if Kafka is unreachable), we write outbox events to a local PostgreSQL table in the same DB transaction. A dedicated polling thread reads from the outbox table and publishes to Kafka cleanly.

```java
@Transactional
public void processPayment(PaymentRequest request) {
    Payment payment = paymentRepository.save(new Payment(request));
    OutboxEvent event = new OutboxEvent("PAYMENT_CREATED", payment.getId().toString(), toJson(payment));
    outboxRepository.save(event);
}
```

### 2. Redis-Backed Idempotency
To prevent duplicate processing when Kafka consumer offsets rebalance, we store an idempotency key (`payment:idempotency:{id}`) in Redis with a 24-hour TTL:

```java
Boolean isNew = redisTemplate.opsForValue().setIfAbsent("payment:idempotency:" + paymentId, "LOCKED", Duration.ofHours(24));
if (Boolean.FALSE.equals(isNew)) {
    log.info("Duplicate event detected for paymentId: {}, skipping", paymentId);
    return;
}
```

### Key Takeaway
By combining outbox tables with Redis idempotency locks, we achieved sub-50ms event processing latency while keeping server hosting costs under ₹100 per month on Koyeb and Vercel.
"""
    }
}

def generate_blog(template_key="kafka_resilience", output_file="generated_tech_post.md"):
    data = DEFAULT_TEMPLATES.get(template_key, DEFAULT_TEMPLATES["kafka_resilience"])
    
    header = f"---\ntitle: {data['title']}\npublished: true\ntags: {', '.join(data['tags'])}\n---\n\n"
    full_markdown = header + data['content'].strip()
    
    out_path = Path(__file__).parent / "content-publishing" / output_file
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(full_markdown, encoding="utf-8")
    
    print(f"[SUCCESS] Generated 100% Free Technical Article at: {out_path}")
    return str(out_path)

if __name__ == "__main__":
    generate_blog()

import os
import requests

API_KEY = "Doen5XSCgWmBSj2Cq7byuCWa"
DEVTO_API_URL = "https://dev.to/api/articles"

md_file_path = r"c:\Users\shubh\OneDrive\Desktop\zyvop_part3_content.md"
with open(md_file_path, "r", encoding="utf-8") as f:
    body_markdown = f.read()

headers = {
    "api-key": API_KEY,
    "Content-Type": "application/json"
}

payload = {
    "article": {
        "title": "Event-Driven Microservices with Apache Kafka, Redis Caching and Transactional Outbox Pattern",
        "published": True,
        "body_markdown": body_markdown,
        "tags": ["springboot", "java", "kafka", "redis"],
        "description": "Master high-throughput event-driven microservices architecture using Java 21, Spring Boot 3.4+, Apache Kafka, Redis idempotency and the Transactional Outbox Pattern."
    }
}

print("Publishing Article to DEV.to via Official REST API...")
response = requests.post(DEVTO_API_URL, headers=headers, json=payload)

if response.status_code == 201:
    data = response.json()
    print("==========================================")
    print("SUCCESS: Published Live on DEV.to!")
    print("Article Title:", data.get("title"))
    print("Live URL:", data.get("url"))
    print("==========================================")
else:
    print("Failed to publish. Status code:", response.status_code)
    print("Response:", response.text)

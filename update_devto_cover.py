import requests

API_KEY = "Doen5XSCgWmBSj2Cq7byuCWa"
# Fetch article by slug to get ID
res = requests.get("https://dev.to/api/articles/shubham_bhati/event-driven-microservices-with-apache-kafka-redis-caching-and-transactional-outbox-pattern-13a7")
if res.status_code == 200:
    article_id = res.json().get("id")
    print(f"Found Article ID: {article_id}")
    
    update_url = f"https://dev.to/api/articles/{article_id}"
    headers = {"api-key": API_KEY, "Content-Type": "application/json"}
    payload = {
        "article": {
            "main_image": "https://raw.githubusercontent.com/Shubh2-0/central-automation-engine/master/banners/kafka_cover.png"
        }
    }
    up_res = requests.put(update_url, headers=headers, json=payload)
    if up_res.status_code == 200:
        print("[SUCCESS] Attached custom Cover Banner to DEV.to article!")
        print("Updated Article URL:", up_res.json().get("url"))
    else:
        print("Update status:", up_res.status_code, up_res.text)

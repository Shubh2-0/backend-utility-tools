import requests

API_KEY = "Doen5XSCgWmBSj2Cq7byuCWa"
res = requests.get("https://dev.to/api/articles/me", headers={"api-key": API_KEY})
if res.status_code == 200:
    articles = res.json()
    if len(articles) > 0:
        latest = articles[0]
        print("Title:", latest.get("title"))
        print("Cover Image:", latest.get("cover_image"))
        print("Social Image:", latest.get("social_image"))

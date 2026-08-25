import requests

API_KEY = "Doen5XSCgWmBSj2Cq7byuCWa"
article_id = 4410360

# Adding timestamp cache buster forces DEV.to CDN to re-download the image instead of serving the cached "image no longer exists" error
image_url = "https://cdn.jsdelivr.net/gh/Shubh2-0/central-automation-engine@master/banners/banner_outbox_pattern.png?v=20260816"

update_url = f"https://dev.to/api/articles/{article_id}"
headers = {"api-key": API_KEY, "Content-Type": "application/json"}

payload = {
    "article": {
        "main_image": image_url
    }
}

print(f"Force updating DEV.to article {article_id} with cache-busted image URL: {image_url}")
up_res = requests.put(update_url, headers=headers, json=payload)

if up_res.status_code == 200:
    print("[SUCCESS] Forced Cover Banner Cache Refresh on DEV.to article!")
    print("Updated Article URL:", up_res.json().get("url"))
else:
    print("Update status:", up_res.status_code, up_res.text)

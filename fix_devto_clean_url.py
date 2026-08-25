import requests

API_KEY = "Doen5XSCgWmBSj2Cq7byuCWa"
article_id = 4410360

# Clean direct URL without '@' symbols so media2.dev.to proxy transforms it cleanly
image_url = "https://raw.githubusercontent.com/Shubh2-0/central-automation-engine/master/banners/banner_outbox_pattern.png"

update_url = f"https://dev.to/api/articles/{article_id}"
headers = {"api-key": API_KEY, "Content-Type": "application/json"}

payload = {
    "article": {
        "main_image": image_url
    }
}

print(f"Updating DEV.to article {article_id} with clean image URL: {image_url}")
up_res = requests.put(update_url, headers=headers, json=payload)

if up_res.status_code == 200:
    print("[SUCCESS] Updated DEV.to cover image URL!")
    print("New Cover Image in API:", up_res.json().get("cover_image"))
else:
    print("Update status:", up_res.status_code, up_res.text)

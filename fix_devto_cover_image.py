import requests

API_KEY = "Doen5XSCgWmBSj2Cq7byuCWa"
article_id = 4410360

update_url = f"https://dev.to/api/articles/{article_id}"
headers = {"api-key": API_KEY, "Content-Type": "application/json"}

# The exact image pushed to GitHub repository
image_url = "https://raw.githubusercontent.com/Shubh2-0/central-automation-engine/master/banners/banner_outbox_pattern.png"

payload = {
    "article": {
        "main_image": image_url
    }
}

print(f"Updating DEV.to article {article_id} with valid image URL: {image_url}")
up_res = requests.put(update_url, headers=headers, json=payload)

if up_res.status_code == 200:
    print("[SUCCESS] Fixed Cover Banner on DEV.to article!")
    print("Updated Article URL:", up_res.json().get("url"))
else:
    print("Update status:", up_res.status_code, up_res.text)

import os
import base64
import requests

API_KEY = "Doen5XSCgWmBSj2Cq7byuCWa"
article_id = 4410360
img_path = r"c:\Users\shubh\OneDrive\Desktop\github\central-automation-engine\banners\banner_outbox_pattern.png"

print("Uploading banner to ImgBB direct image CDN...")

with open(img_path, "rb") as file:
    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": "6d207e02198a847aa98d0a2a901485a5",
        "image": base64.b64encode(file.read()),
    }
    res = requests.post(url, payload)

if res.status_code == 200:
    data = res.json()
    direct_url = data.get("data", {}).get("url")
    print("Direct ImgBB Image URL:", direct_url)

    update_url = f"https://dev.to/api/articles/{article_id}"
    headers = {"api-key": API_KEY, "Content-Type": "application/json"}
    payload = {
        "article": {
            "main_image": direct_url
        }
    }

    print(f"Updating DEV.to article {article_id} with direct ImgBB image URL...")
    up_res = requests.put(update_url, headers=headers, json=payload)
    if up_res.status_code == 200:
        print("[SUCCESS] Set Direct ImgBB Cover Banner on DEV.to article!")
        print("Updated Article URL:", up_res.json().get("url"))
    else:
        print("Update status:", up_res.status_code, up_res.text)
else:
    print("ImgBB Upload error:", res.status_code, res.text)

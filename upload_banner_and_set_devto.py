import os
import requests

API_KEY = "Doen5XSCgWmBSj2Cq7byuCWa"
article_id = 4410360
img_path = r"c:\Users\shubh\OneDrive\Desktop\github\central-automation-engine\banners\banner_outbox_pattern.png"

print("Uploading poster banner to free image CDN...")

# Upload to freeimage.host / tmpfiles for direct image/png streaming
with open(img_path, "rb") as f:
    upload_res = requests.post("https://tmpfiles.org/api/v1/upload", files={"file": f})

if upload_res.status_code == 200:
    data = upload_res.json()
    url = data.get("data", {}).get("url")
    # Convert tmpfiles page URL to direct image URL
    direct_url = url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
    print("Direct Image CDN URL:", direct_url)

    update_url = f"https://dev.to/api/articles/{article_id}"
    headers = {"api-key": API_KEY, "Content-Type": "application/json"}
    payload = {
        "article": {
            "main_image": direct_url
        }
    }

    print(f"Updating DEV.to article {article_id} with direct CDN image URL...")
    up_res = requests.put(update_url, headers=headers, json=payload)
    if up_res.status_code == 200:
        print("[SUCCESS] Set Direct CDN Cover Banner on DEV.to article!")
        print("Updated Article URL:", up_res.json().get("url"))
    else:
        print("Update status:", up_res.status_code, up_res.text)
else:
    print("Upload error:", upload_res.status_code, upload_res.text)

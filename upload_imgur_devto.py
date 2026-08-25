import base64
import requests

API_KEY = "Doen5XSCgWmBSj2Cq7byuCWa"
article_id = 4410360
img_path = r"c:\Users\shubh\OneDrive\Desktop\github\central-automation-engine\banners\banner_outbox_pattern.png"

print("Uploading banner to Imgur direct image CDN...")

with open(img_path, "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode("utf-8")

headers = {"Authorization": "Client-ID 5464654e88e50b1"}
data = {"image": img_b64, "type": "base64"}

res = requests.post("https://api.imgur.com/3/image", headers=headers, data=data)

if res.status_code == 200:
    link = res.json().get("data", {}).get("link")
    print("[SUCCESS] Direct Imgur Link:", link)

    update_url = f"https://dev.to/api/articles/{article_id}"
    dev_headers = {"api-key": API_KEY, "Content-Type": "application/json"}
    payload = {"article": {"main_image": link}}

    up_res = requests.put(update_url, headers=dev_headers, json=payload)
    if up_res.status_code == 200:
        print("[SUCCESS] DEV.to Cover Image set to Imgur Link!")
        print("Updated Article URL:", up_res.json().get("url"))
    else:
        print("Update error:", up_res.status_code, up_res.text)
else:
    print("Imgur upload error:", res.status_code, res.text)

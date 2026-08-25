import requests

API_KEY = "Doen5XSCgWmBSj2Cq7byuCWa"
article_id = 4410360
img_path = r"c:\Users\shubh\OneDrive\Desktop\github\central-automation-engine\banners\banner_outbox_pattern.png"

print("Testing DEV.to official API image upload endpoint...")

with open(img_path, "rb") as f:
    res = requests.post(
        "https://dev.to/api/images",
        headers={"api-key": API_KEY},
        files={"image": f}
    )

print("DEV.to image upload status:", res.status_code)
print("Response text:", res.text)

if res.status_code == 200 or res.status_code == 201:
    s3_url = res.json().get("url")
    print(f"[SUCCESS] Native DEV.to S3 Image URL: {s3_url}")
    
    update_url = f"https://dev.to/api/articles/{article_id}"
    headers = {"api-key": API_KEY, "Content-Type": "application/json"}
    payload = {"article": {"main_image": s3_url}}

    up_res = requests.put(update_url, headers=headers, json=payload)
    if up_res.status_code == 200:
        print("[SUCCESS] Set native S3 Cover Image on DEV.to article!")
        print("Updated Article URL:", up_res.json().get("url"))

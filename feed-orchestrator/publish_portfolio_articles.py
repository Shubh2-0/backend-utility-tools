import os
import sys
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import requests

PROCESSED_FILE = "processed_articles.txt"
ARTICLES_DIR = "articles"

def load_processed():
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, "r") as f:
            return [line.strip() for line in f if line.strip()]
    return []

def mark_processed(filename):
    with open(PROCESSED_FILE, "a") as f:
        f.write(filename + "\n")

def slugify(text):
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[-\s]+", "-", text).strip("-")

def post_to_devto(api_key, title, body, tags, slug):
    url = "https://dev.to/api/articles"
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    
    canonical_url = f"https://shubhambhati.is-a.dev/blog/{slug}"
    
    payload = {
        "article": {
            "title": title,
            "published": True,
            "body_markdown": body,
            "tags": tags,
            "canonical_url": canonical_url
        }
    }
    
    try:
        r = requests.post(url, headers=headers, json=payload)
        if r.status_code == 201:
            res_data = r.json()
            return res_data.get("url")
        else:
            print(f"[Error] Dev.to publishing failed (Status: {r.status_code}, Response: {r.text})")
    except Exception as e:
        print(f"[Error] Dev.to request exception: {e}")
    return None

def send_digest_email(repo, title, post_url):
    smtp_server = os.environ.get("EMAIL_SMTP_SERVER")
    smtp_user = os.environ.get("EMAIL_USER")
    smtp_password = os.environ.get("EMAIL_PASSWORD")
    email_to = os.environ.get("EMAIL_TO")
    
    if not all([smtp_server, smtp_user, smtp_password, email_to]):
        print("[Info] SMTP credentials missing. Skipping email dispatch.")
        return
        
    subject = f"Article Published: {title}"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background-color: #0d1117;
                color: #c9d1d9;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #161b22;
                border-radius: 12px;
                border: 1px solid #30363d;
                overflow: hidden;
                box-shadow: 0 8px 24px rgba(0,0,0,0.5);
            }}
            .header {{
                background: linear-gradient(135deg, #1f6feb 0%, #0d1117 100%);
                padding: 28px 24px;
                text-align: center;
                border-bottom: 1px solid #30363d;
            }}
            .header h1 {{
                color: #ffffff;
                font-size: 20px;
                margin: 0;
                font-weight: 600;
                letter-spacing: 0.5px;
            }}
            .content {{
                padding: 24px;
            }}
            .card {{
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 20px;
            }}
            .status-badge {{
                display: inline-block;
                background-color: #2ea043;
                color: #ffffff;
                font-size: 11px;
                font-weight: 600;
                padding: 4px 10px;
                border-radius: 20px;
                margin-bottom: 12px;
            }}
            .issue-title {{
                color: #58a6ff;
                font-size: 16px;
                font-weight: 600;
                margin: 0 0 12px 0;
                text-decoration: none;
                display: block;
            }}
            .issue-title:hover {{
                text-decoration: underline;
            }}
            .footer {{
                background-color: #0d1117;
                padding: 16px;
                text-align: center;
                font-size: 11px;
                color: #8b949e;
                border-top: 1px solid #30363d;
            }}
            .footer a {{
                color: #58a6ff;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Article Published Successfully</h1>
            </div>
            <div class="content">
                <div class="card">
                    <div class="status-badge">Live on Dev.to</div>
                    <a href="{post_url}" class="issue-title">{title}</a>
                    <p style="font-size:13px; color:#8b949e;">Your article has been cross-published successfully. The canonical URL is set to your custom portfolio domain.</p>
                </div>
            </div>
            <div class="footer">
                <p>Sent autonomously by Antigravity Automation Engine on behalf of <a href="https://github.com/Shubh2-0">Shubh2-0</a>.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = email_to
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))
    
    try:
        server = smtplib.SMTP(smtp_server, 587)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, email_to, msg.as_string())
        server.quit()
        print("[SUCCESS] Publication notification email sent successfully!")
    except Exception as e:
        print(f"[ERROR] Failed to send publication notification: {e}")

def main():
    devto_key = os.environ.get("DEVTO_API_KEY")
    if not devto_key:
        print("[ERROR] DEVTO_API_KEY is missing.")
        return
        
    if not os.path.exists(ARTICLES_DIR):
        print(f"[Info] Articles directory '{ARTICLES_DIR}' does not exist.")
        return
        
    processed = load_processed()
    files = [f for f in os.listdir(ARTICLES_DIR) if f.endswith(".md")]
    
    published_any = False
    for filename in files:
        if filename in processed:
            continue
            
        filepath = os.path.join(ARTICLES_DIR, filename)
        print(f"[*] Parsing article: {filename}")
        
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        title = "Untitled Article"
        tags = ["programming"]
        body_lines = []
        
        for line in lines:
            if line.lower().startswith("title:"):
                title = line.split(":", 1)[1].strip()
            elif line.lower().startswith("tags:"):
                tags_str = line.split(":", 1)[1].strip()
                tags = [t.strip() for t in tags_str.split(",") if t.strip()]
            else:
                body_lines.append(line)
                
        body = "".join(body_lines).strip()
        slug = slugify(title)
        
        print(f"[*] Title: {title}")
        print(f"[*] Slug: {slug}")
        print(f"[*] Tags: {tags}")
        
        post_url = post_to_devto(devto_key, title, body, tags, slug)
        if post_url:
            print(f"[SUCCESS] Article published: {post_url}")
            mark_processed(filename)
            send_digest_email("backend-utility-tools", title, post_url)
            published_any = True
            
    if not published_any:
        print("[Info] No new articles to publish.")

if __name__ == "__main__":
    main()

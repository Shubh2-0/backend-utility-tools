import os
import sys
import json
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import requests
import google.generativeai as genai

# Configuration
CACHE_FILE = "contribution_cache.json"
MAX_DAILY_COMMENTS = 5

API_BASE = "https://api.github.com"
ROUTE_SEARCH = "search/issues"

# Target search queries for Java / Spring Boot / Microservices / Distributed Systems
TARGET_QUERIES = [
    'is:issue language:java state:open "good first issue" security',
    'is:issue language:java state:open "help wanted" spring',
    'is:issue language:java state:open "spring security"',
    'is:issue language:java state:open "kafka" event',
    'is:issue language:java state:open "redis" cache',
    'is:issue language:java state:open "microservices" gateway',
    'is:issue language:java state:open "postgresql" locking',
    'is:issue language:java state:open "hibernate" query',
    'is:issue language:java state:open "performance" optimization',
    'is:issue language:java state:open "rest api" controller'
]

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"commented_issues": [], "daily_logs": [], "last_run_date": ""}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=4)

def get_api_key():
    return os.environ.get("GEMINI_API_KEYS") or os.environ.get("GEMINI_API_KEY")

def generate_outreach_comment(title, body):
    api_key = get_api_key()
    if not api_key:
        print("[ERROR] Gemini API Key is missing.")
        return None
        
    keys = [k.strip() for k in api_key.split(",") if k.strip()]
    if not keys:
        return None
        
    # Use key rotation
    genai.configure(api_key=keys[0])
    
    prompt = f"""
You are a Senior Backend Engineer (3+ YOE specializing in Java, Spring Boot, Microservices, Redis, Kafka, Postgres). You want to contribute to an open-source project.
Read the issue title and description below carefully.
Draft a short, 1-2 sentence comment offering to help solve the issue.
Your offer MUST highlight specific technical details of how you would solve it (e.g., using a custom security filter, configuring Actuator properties, optimizing database locking, or adding a Redis TTL).

CRITICAL TONE RULES:
1. Write 100% like a real human software developer posting on GitHub.
2. NO hashtags. NO emojis.
3. FORBIDDEN AI words: delve, tapestry, crucial, vital, fantastic, robust, leverage, paradigm, ecosystem, seamless, game-changer, indeed, additionally, furthermore, thus, hence, consequently, key takeaway, remember to, demystify, testament.
4. NO Oxford comma — never put a comma before "and". Write "A, B and C" NOT "A, B, and C".
5. Use natural contractions (I'm, I'd, we've).
6. Write mostly in casual, natural lowercase.
7. DO NOT start with cliches like "Hey there!" or "Nice repository!". Just get straight to the point.

Issue Title: {title}
Issue Description: {body}

Draft Comment:
"""
    fallback_models = ["gemini-3.5-flash", "gemini-2.0-flash", "gemini-flash-latest"]
    for m_name in fallback_models:
        try:
            m = genai.GenerativeModel(m_name)
            response = m.generate_content(prompt)
            if response and response.text:
                return response.text.strip().replace('"', '')
        except Exception as e:
            print(f"[Warning] Model {m_name} failed: {e}")
    return None

def fetch_open_issues(token):
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}" if token else ""
    }
    
    # Pick a random query to vary sources
    query = random.choice(TARGET_QUERIES)
    url = f"{API_BASE}/{ROUTE_SEARCH}?q={query}&sort=created&order=desc&per_page=15"
    
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return r.json().get("items", [])
        else:
            print(f"[Error] GitHub search failed (Status: {r.status_code})")
    except Exception as e:
        print(f"[Error] Search API exception: {e}")
    return []

def post_comment(token, repo_full_name, issue_number, body):
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}"
    }
    url = f"{API_BASE}/repos/{repo_full_name}/issues/{issue_number}/comments"
    try:
        r = requests.post(url, headers=headers, json={"body": body})
        return r.status_code == 201
    except Exception as e:
        print(f"[Error] Failed to post comment on {repo_full_name}#{issue_number}: {e}")
    return False

def send_digest_email(logs):
    smtp_server = os.environ.get("EMAIL_SMTP_SERVER")
    smtp_user = os.environ.get("EMAIL_USER")
    smtp_password = os.environ.get("EMAIL_PASSWORD")
    email_to = os.environ.get("EMAIL_TO")
    
    if not all([smtp_server, smtp_user, smtp_password, email_to]):
        print("[Info] SMTP credentials missing. Writing report to daily_digest.md instead.")
        write_digest_file(logs)
        return
        
    subject = f"GitHub Open Source Contribution Digest - {datetime.utcnow().strftime('%Y-%m-%d')}"
    
    # Build styled HTML cards
    cards_html = ""
    for log in logs:
        # Standardize timestamp formatting for display
        try:
            formatted_time = log['timestamp'].split(".")[0].replace("T", " ") + " UTC"
        except:
            formatted_time = log['timestamp']
            
        cards_html += f"""
        <div class="card">
            <a href="https://github.com/{log['repo']}" class="repo-badge">{log['repo']}</a>
            <a href="{log['url']}" class="issue-title">{log['title']}</a>
            <blockquote class="comment-box">
                "{log['comment']}"
            </blockquote>
            <div class="timestamp">{formatted_time}</div>
        </div>
        """
        
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
            .repo-badge {{
                display: inline-block;
                background-color: #21262d;
                border: 1px solid #30363d;
                color: #58a6ff;
                font-size: 11px;
                font-weight: 600;
                padding: 4px 10px;
                border-radius: 20px;
                margin-bottom: 12px;
                text-decoration: none;
            }}
            .issue-title {{
                color: #c9d1d9;
                font-size: 15px;
                font-weight: 600;
                margin: 0 0 12px 0;
                text-decoration: none;
                display: block;
            }}
            .issue-title:hover {{
                color: #58a6ff;
                text-decoration: underline;
            }}
            .comment-box {{
                background-color: #161b22;
                border-left: 4px solid #ab7df8;
                padding: 12px;
                border-radius: 0 4px 4px 0;
                margin: 0;
                font-size: 13px;
                line-height: 1.6;
                color: #8b949e;
                font-style: italic;
            }}
            .timestamp {{
                font-size: 11px;
                color: #8b949e;
                margin-top: 12px;
                text-align: right;
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
                <h1>GitHub Open Source Contribution Digest</h1>
            </div>
            <div class="content">
                {cards_html}
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
        print("[SUCCESS] Digest email sent successfully!")
    except Exception as e:
        print(f"[ERROR] Failed to send digest email: {e}")
        write_digest_file(logs)

def write_digest_file(logs):
    path = "daily_digest.md"
    body = f"# 📝 Daily Digest - {datetime.utcnow().strftime('%Y-%m-%d')}\n\n"
    for log in logs:
        body += f"### 📍 Repo: {log['repo']}\n"
        body += f"- **Issue:** [{log['title']}]({log['url']})\n"
        body += f"- **Comment Posted:** {log['comment']}\n"
        body += f"- **Timestamp:** {log['timestamp']}\n\n---\n"
        
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)
    print(f"[Info] Digest file written to {path}")

def run_outreach_cycle():
    token = os.environ.get("GH_TOKEN")
    if not token:
        print("[ERROR] GH_TOKEN is required to run outreach.")
        return
        
    cache = load_cache()
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    
    # Reset daily limit count if date changed
    if cache["last_run_date"] != today_str:
        cache["last_run_date"] = today_str
        cache["daily_logs"] = []
        
    # Check if daily limit is reached
    today_comments = [l for l in cache["daily_logs"] if l.get("date") == today_str]
    if len(today_comments) >= MAX_DAILY_COMMENTS:
        print(f"[Info] Daily comments limit reached ({MAX_DAILY_COMMENTS}). Skipping outreach check.")
        return
        
    issues = fetch_open_issues(token)
    if not issues:
        print("[Info] No open issues found matching query.")
        return
        
    comment_posted = False
    for issue in issues:
        url = issue.get("html_url")
        if url in cache["commented_issues"]:
            continue
            
        title = issue.get("title", "")
        body = issue.get("body", "") or ""
        
        # Verify title and body are in English (reject Chinese, Japanese, Korean, or foreign script ranges)
        import re
        cjk_pattern = re.compile(r'[\u4e00-\u9fff\uac00-\ud7af\u3040-\u30ff]')
        if cjk_pattern.search(title) or cjk_pattern.search(body):
            print(f"[Info] Skipping issue {url} due to non-English or CJK characters.")
            continue
            
        repo_url = issue.get("repository_url", "")
        repo_name = "/".join(repo_url.split("/")[-2:])
        number = issue.get("number")
        
        # Pre-filter: Skip if assignee already exists
        if issue.get("assignee") or issue.get("assignees"):
            continue
            
        print(f"[*] Found suitable candidate issue: {repo_name}#{number} - {title}")
        
        comment = generate_outreach_comment(title, body)
        if not comment:
            print("[Warning] Failed to generate outreach comment.")
            continue
            
        # Post the comment
        success = post_comment(token, repo_name, number, comment)
        if success:
            print(f"[SUCCESS] Posted comment on {repo_name}#{number}!")
            cache["commented_issues"].append(url)
            log_entry = {
                "date": today_str,
                "timestamp": datetime.utcnow().isoformat(),
                "repo": repo_name,
                "title": title,
                "url": url,
                "comment": comment
            }
            cache["daily_logs"].append(log_entry)
            save_cache(cache)
            comment_posted = True
            break # Exit loop after posting 1 comment to be safe
            
    # If it is the end of the day or we posted a comment, let's process the digest email
    # For GHA automation, we can run the email check step at the end of the day or on each success run
    if comment_posted and len(cache["daily_logs"]) >= 1:
        send_digest_email(cache["daily_logs"])

if __name__ == "__main__":
    run_outreach_cycle()

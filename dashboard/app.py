import os
import sys
import json
import uuid
import logging
import sqlite3
import hashlib
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Cookie, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import requests
from dotenv import load_dotenv, dotenv_values

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dashboard")

# Setup base paths
WORKSPACE_DIR = Path(__file__).parent.parent.resolve()
DASHBOARD_DIR = Path(__file__).parent.resolve()

# Load environment variables for the dashboard itself
load_dotenv(DASHBOARD_DIR / ".env")

# Use persistent volume storage if available (Render/Railway mount at /data)
PERSISTENT_DIR = Path("/data")
if PERSISTENT_DIR.exists() and os.access(PERSISTENT_DIR, os.W_OK):
    QUEUE_FILE = PERSISTENT_DIR / "drafts_queue.json"
    DB_FILE = PERSISTENT_DIR / "users.db"
else:
    QUEUE_FILE = DASHBOARD_DIR / "drafts_queue.json"
    DB_FILE = DASHBOARD_DIR / "users.db"

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect(str(DB_FILE))
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            username TEXT UNIQUE,
            password_hash TEXT,
            salt TEXT,
            created_at TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            username TEXT,
            expires_at TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS otp_verifications (
            username TEXT PRIMARY KEY,
            otp_code TEXT,
            expires_at TEXT
        )
    ''')
    conn.commit()

    # Seed the admin user if not exists
    c.execute('SELECT id FROM users WHERE username = ?', ('shubham',))
    if not c.fetchone():
        pw_hash, pw_salt = hash_password("change-this-password")
        c.execute('INSERT INTO users (id, email, username, password_hash, salt, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                  (str(uuid.uuid4()), 'admin@domain.local', 'shubham', pw_hash, pw_salt, datetime.now().isoformat()))
        conn.commit()
        logger.info("Admin user 'shubham' seeded successfully!")
        
    conn.close()
    logger.info(f"Database initialized at {DB_FILE}")

# init_db call moved below helpers to avoid NameError on hash_password

# Email sending helper for OTP
def send_otp_email(to_email: str, otp: str):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = os.environ.get("SMTP_EMAIL", "admin@domain.local")
    sender_password = os.environ.get("SMTP_PASSWORD")
    
    subject = f"Your TechBrand OTP Code: {otp}"
    body = f"Hello Shubham,\n\nYour 6-digit verification code to access the TechBrand Control Center is:\n\n{otp}\n\nThis code is valid for 10 minutes.\n\nRegards,\nTechBrand Automation System"
    
    # If no SMTP_PASSWORD, print clearly to logs so user can read from Render terminal logs
    if not sender_password:
        logger.warning(f"\n==================================================")
        logger.warning(f"  [OTP CODE FOR SHUBHAM]: {otp}")
        logger.warning(f"  (Set SMTP_PASSWORD in cloud env to email this code)")
        logger.warning(f"==================================================\n")
        return
        
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        logger.info(f"Successfully sent OTP email to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send OTP email: {e}")
        # Print fallback so user is not blocked
        logger.warning(f"\n==================================================")
        logger.warning(f"  [FALLBACK OTP CODE]: {otp}")
        logger.warning(f"==================================================\n")

# Password hashing helper (PBKDF2 with salt)
def hash_password(password: str, salt: bytes = None) -> tuple[str, str]:
    if salt is None:
        salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return key.hex(), salt.hex()

# Session Management helpers
def create_session(username: str) -> str:
    session_id = secrets.token_hex(32)
    expires_at = (datetime.now() + timedelta(days=7)).isoformat()
    conn = sqlite3.connect(str(DB_FILE))
    c = conn.cursor()
    c.execute('INSERT INTO sessions (session_id, username, expires_at) VALUES (?, ?, ?)',
              (session_id, username, expires_at))
    conn.commit()
    conn.close()
    return session_id

def verify_session(session_id: Optional[str]) -> Optional[str]:
    if not session_id:
        return None
    conn = sqlite3.connect(str(DB_FILE))
    c = conn.cursor()
    c.execute('SELECT username, expires_at FROM sessions WHERE session_id = ?', (session_id,))
    row = c.fetchone()
    conn.close()
    if row:
        username, expires_at = row
        if datetime.fromisoformat(expires_at) > datetime.now():
            return username
        else:
            # Delete expired session
            conn = sqlite3.connect(str(DB_FILE))
            c = conn.cursor()
            c.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
            conn.commit()
            conn.close()
    return None

def delete_session(session_id: str):
    if not session_id:
        return
    conn = sqlite3.connect(str(DB_FILE))
    c = conn.cursor()
    c.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
    conn.commit()
    conn.close()

# Initialize DB after all helpers are defined
init_db()

app = FastAPI(title="Unified Automation Control Center")

# Ensure static and templates directory exist
(DASHBOARD_DIR / "static").mkdir(exist_ok=True)
(DASHBOARD_DIR / "templates").mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(DASHBOARD_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(DASHBOARD_DIR / "templates"))

# Define models
class ApproveRequest(BaseModel):
    approved_comment: str

class ManualDraftRequest(BaseModel):
    platform: str
    url: str

# Helper: Load bot envs
def get_bot_env(bot_folder: str) -> dict:
    env_path = WORKSPACE_DIR / bot_folder / ".env"
    env_vars = {}
    if env_path.exists():
        env_vars = dict(dotenv_values(env_path))
    
    # Merge with system environment variables (cloud variables override local .env)
    keys_to_merge = [
        "LINKEDIN_ACCESS_TOKEN", "GEMINI_API_KEY", "INSTAGRAM_USERNAME", 
        "INSTAGRAM_PASSWORD", "INSTAGRAM_SESSIONID", 
        "GH_TOKEN", 
        "DEVTO_API_KEY", "HASHNODE_TOKEN", 
        "HASHNODE_PUBLICATION_ID"
    ]
    for key in keys_to_merge:
        val = os.environ.get(key)
        if val:
            env_vars[key] = val
    return env_vars

# Helper: Initialize Queue File
def load_queue() -> dict:
    if not QUEUE_FILE.exists():
        with open(QUEUE_FILE, "w") as f:
            json.dump({"drafts": []}, f, indent=2)
    try:
        with open(QUEUE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"drafts": []}

def save_queue(queue_data: dict):
    with open(QUEUE_FILE, "w") as f:
        json.dump(queue_data, f, indent=2)

# Helper: Call Gemini to generate a response
def call_gemini(api_key: str, prompt: str) -> Optional[str]:
    if not api_key:
        return "Error: Gemini API Key is missing. Please configure it in your bot's .env file."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=15)
        if r.status_code == 200:
            res = r.json()
            return res['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            logger.error(f"Gemini API error status {r.status_code}: {r.text}")
            return f"Gemini error {r.status_code}: {r.text}"
    except Exception as e:
        logger.error(f"Gemini API request failed: {e}")
        return f"Request failed: {str(e)}"

# GET: Main page (Protected)
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, session_id: Optional[str] = Cookie(None)):
    username = verify_session(session_id)
    if not username:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request=request, name="index.html", context={"username": username})

# GET: Login page
@app.get("/login", response_class=HTMLResponse)
def get_login_page(request: Request, session_id: Optional[str] = Cookie(None)):
    if verify_session(session_id):
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="login.html", context={})

# POST: Login user (Step 1: Credentials check -> OTP generation)
@app.post("/login")
def login_user(
    background_tasks: BackgroundTasks,
    username_or_email: str = Form(...),
    password: str = Form(...)
):
    conn = sqlite3.connect(str(DB_FILE))
    c = conn.cursor()
    c.execute('SELECT username, password_hash, salt, email FROM users WHERE username = ? OR email = ?', 
              (username_or_email, username_or_email))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return HTMLResponse(content="<h3>Invalid username/email or password.</h3><br><a href='/login'>Try again</a>", status_code=400)
        
    db_username, db_hash, db_salt, db_email = row
    verify_hash, _ = hash_password(password, bytes.fromhex(db_salt))
    if verify_hash != db_hash:
        return HTMLResponse(content="<h3>Invalid username/email or password.</h3><br><a href='/login'>Try again</a>", status_code=400)
        
    # Generate 6-digit OTP code
    otp_code = "".join([str(secrets.randbelow(10)) for _ in range(6)])
    expires_at = (datetime.now() + timedelta(minutes=10)).isoformat()
    
    # Save OTP to DB
    conn = sqlite3.connect(str(DB_FILE))
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO otp_verifications (username, otp_code, expires_at) VALUES (?, ?, ?)',
              (db_username, otp_code, expires_at))
    conn.commit()
    conn.close()
    
    # Trigger SMTP email sending in the background
    background_tasks.add_task(send_otp_email, db_email, otp_code)
    
    # Redirect browser to OTP verification page
    return RedirectResponse(url=f"/verify?username={db_username}", status_code=303)

# GET: OTP Verification page
@app.get("/verify", response_class=HTMLResponse)
def get_verify_page(request: Request, username: str, session_id: Optional[str] = Cookie(None)):
    if verify_session(session_id):
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="verify.html", context={"username": username})

# POST: Verify OTP code (Step 2: Session establishment)
@app.post("/verify")
def verify_otp_code(
    username: str = Form(...),
    otp_code: str = Form(...)
):
    conn = sqlite3.connect(str(DB_FILE))
    c = conn.cursor()
    c.execute('SELECT otp_code, expires_at FROM otp_verifications WHERE username = ?', (username,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return HTMLResponse(content="<h3>No active verification request found.</h3><br><a href='/login'>Go to Login</a>", status_code=400)
        
    db_otp, db_expires = row
    if datetime.fromisoformat(db_expires) < datetime.now():
        return HTMLResponse(content="<h3>Verification code has expired (10 min limit).</h3><br><a href='/login'>Request a new code</a>", status_code=400)
        
    if otp_code.strip() != db_otp:
        return HTMLResponse(content="<h3>Invalid verification code.</h3><br><a href='/login'>Try again</a>", status_code=400)
        
    # Success: delete OTP and create session
    conn = sqlite3.connect(str(DB_FILE))
    c = conn.cursor()
    c.execute('DELETE FROM otp_verifications WHERE username = ?', (username,))
    conn.commit()
    conn.close()
    
    session_id = create_session(username)
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        max_age=7 * 24 * 3600, # 7 days
        samesite="lax",
        secure=False
    )
    return response

# GET: Logout user
@app.get("/logout")
def logout_user(session_id: Optional[str] = Cookie(None)):
    if session_id:
        delete_session(session_id)
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("session_id")
    return response

# GET: Status of all bots
@app.get("/api/status")
def get_status(session_id: Optional[str] = Cookie(None)):
    if not verify_session(session_id):
        raise HTTPException(status_code=401, detail="Unauthorized")
    status = {}
    
    # 1. LinkedIn
    li_env = get_bot_env("linkedin-pipeline-local")
    li_token = WORKSPACE_DIR / "linkedin-pipeline-local" / "token.json"
    status["linkedin"] = {
        "configured": bool(li_env.get("LINKEDIN_ACCESS_TOKEN") or li_env.get("GEMINI_API_KEY")),
        "token_active": li_token.exists(),
        "status": "Ready" if li_token.exists() else "Missing Token",
        "last_run": "Check GitHub Actions"
    }


    # 6. Blog Bot
    blog_env = get_bot_env("blog-pipeline-local")
    blog_configured = bool(blog_env.get("DEVTO_API_KEY") or blog_env.get("HASHNODE_TOKEN"))
    status["blog"] = {
        "configured": blog_configured,
        "token_active": blog_configured,
        "status": "Ready" if blog_configured else "Config Needed",
        "last_run": "Ready"
    }
    
    return status

# GET: Retrieve current review queue
@app.get("/api/queue")
def get_queue(session_id: Optional[str] = Cookie(None)):
    if not verify_session(session_id):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return load_queue()

# POST: Reject/delete draft
@app.post("/api/queue/reject/{draft_id}")
def reject_draft(draft_id: str, session_id: Optional[str] = Cookie(None)):
    if not verify_session(session_id):
        raise HTTPException(status_code=401, detail="Unauthorized")
    queue = load_queue()
    updated_drafts = [d for d in queue.get("drafts", []) if d.get("id") != draft_id]
    queue["drafts"] = updated_drafts
    save_queue(queue)
    return {"status": "success", "message": "Draft rejected and removed from queue"}

# POST: Approve and Post comment
@app.post("/api/queue/approve/{draft_id}")
def approve_draft(draft_id: str, payload: ApproveRequest, session_id: Optional[str] = Cookie(None)):
    if not verify_session(session_id):
        raise HTTPException(status_code=401, detail="Unauthorized")
    queue = load_queue()
    draft = next((d for d in queue.get("drafts", []) if d.get("id") == draft_id), None)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    platform = draft.get("platform")
    comment_text = payload.approved_comment
    metadata = draft.get("metadata", {})
    
    success = False
    error_message = ""

    # Execute posting based on platform
    if platform == "linkedin":
        # LinkedIn post comment
        li_env = get_bot_env("linkedin-pipeline-local")
        token = li_env.get("LINKEDIN_ACCESS_TOKEN")
        
        # Read from token.json if env access token is empty
        token_file = WORKSPACE_DIR / "linkedin-pipeline-local" / "token.json"
        if not token and token_file.exists():
            try:
                with open(token_file, "r") as f:
                    token = json.load(f).get("access_token")
            except Exception:
                pass
                
        if not token:
            raise HTTPException(status_code=400, detail="LinkedIn Access Token missing")

        # Resolve User URN
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        try:
            # First fetch user URN
            usr_res = requests.get("https://api.linkedin.com/v2/userinfo", headers=headers)
            user_urn = f"urn:li:person:{usr_res.json()['sub']}"
            
            # Post comment
            post_urn = metadata.get("post_urn")
            comment_url = f"https://api.linkedin.com/v2/socialActions/{post_urn}/comments"
            payload = {
                "actor": user_urn,
                "object": post_urn,
                "message": {"text": comment_text}
            }
            comment_res = requests.post(comment_url, headers=headers, json=payload)
            if comment_res.status_code == 201:
                success = True
            else:
                error_message = f"LinkedIn API failed (status {comment_res.status_code}): {comment_res.text}"
        except Exception as e:
            error_message = f"LinkedIn connection error: {e}"

    if success:
        # Remove from queue on success
        queue["drafts"] = [d for d in queue.get("drafts", []) if d.get("id") != draft_id]
        save_queue(queue)
        return {"status": "success", "message": "Comment posted successfully!", "info": error_message}
    else:
        raise HTTPException(status_code=500, detail=f"Failed to post: {error_message}")

# POST: Scan for fresh posts/issues and generate AI drafts for the queue
@app.post("/api/queue/generate")
def generate_queue_drafts(session_id: Optional[str] = Cookie(None)):
    if not verify_session(session_id):
        raise HTTPException(status_code=401, detail="Unauthorized")
    # Load existing queue
    queue = load_queue()
    existing_urls = {d.get("url") for d in queue.get("drafts", [])}
    
    # We will generate a few mock/demo drafts for the user to try out immediately
    new_drafts = []
    
    # Sample Mock: LinkedIn Post Draft
    linkedin_url = "https://linkedin.com/posts/activity-7128938219"
    if linkedin_url not in existing_urls:
        new_drafts.append({
            "id": str(uuid.uuid4())[:8],
            "platform": "linkedin",
            "title": "System Design: Scaling Cache Invalidation",
            "content": "Why is caching named one of the hardest problems in Computer Science? Cache invalidation is tricky. We moved from write-through to CDC (Change Data Capture) with Debezium and Kafka to sync Postgres database writes directly to Redis. This keeps our stale cache window under 50ms.",
            "author": "Amit Kumar (Staff Engineer)",
            "url": linkedin_url,
            "suggested_comment": "using CDC with Debezium is such a clean way to decouple database transactions from cache eviction. We hit similar caching race conditions last year and moving cache invalidation out of the application flow saved us a ton of database locks",
            "created_at": datetime.now().isoformat(),
            "metadata": {"post_urn": "urn:li:activity:7128938219"}
        })



    queue["drafts"].extend(new_drafts)
    save_queue(queue)
    return {"status": "success", "added": len(new_drafts), "message": f"Added {len(new_drafts)} fresh drafts to the review queue."}

# POST: Sandbox custom URL drafting
@app.post("/api/sandbox/draft")
def sandbox_generate_draft(payload: ManualDraftRequest, session_id: Optional[str] = Cookie(None)):
    if not verify_session(session_id):
        raise HTTPException(status_code=401, detail="Unauthorized")
    platform = payload.platform.lower()
    url = payload.url.strip()
    
    if not url:
        raise HTTPException(status_code=400, detail="URL cannot be empty")
        
    # Pick a suitable Gemini key from any available bot env
    gemini_key = None
    for folder in ["instagram-auto-commenter-local", "linkedin-pipeline-local"]:
        k = get_bot_env(folder).get("GEMINI_API_KEY")
        if k:
            gemini_key = k
            break
            
    if not gemini_key:
        # Fallback to system environment variable
        gemini_key = os.environ.get("GEMINI_API_KEY")
        
    # Generate draft content based on platform
    title = f"Manual Draft for: {platform.capitalize()}"
    content = f"Manually inputted URL: {url}"
    author = "Custom Input"
    
    prompt = f"""
    You are an expert Backend Engineer and Tech Writer. Write a short, highly professional, conversational, and helpful reply comment for a developer who posted the link: '{url}'.
    Keep the reply under 3 sentences. Do not use corporate buzzwords. Focus on java, databases, backend, system design, or Spring Boot concepts. Do not use hashtags or emojis.
    """
    
    suggested_comment = call_gemini(gemini_key, prompt)
    if "Error" in suggested_comment or "failed" in suggested_comment:
        # Fallback response
        suggested_comment = "That's a very solid approach. We implement similar practices in our Spring Boot microservices backend to handle performance bottlenecks."

    draft_id = str(uuid.uuid4())[:8]
    metadata = {}
    
    # Attempt to extract metadata from URL
    if platform == "github":
        # e.g., https://github.com/owner/repo/issues/123
        parts = url.split("github.com/")
        if len(parts) > 1:
            path_parts = parts[1].split("/")
            if len(path_parts) >= 4 and path_parts[2] == "issues":
                metadata = {"repo": f"{path_parts[0]}/{path_parts[1]}", "issue_number": int(path_parts[3])}

    elif platform == "linkedin":
        # Extract URN activity id
        import re
        match = re.search(r'activity[-:](\d+)', url)
        if match:
            metadata = {"post_urn": f"urn:li:activity:{match.group(1)}"}
            
    draft = {
        "id": draft_id,
        "platform": platform,
        "title": title,
        "content": content,
        "author": author,
        "url": url,
        "suggested_comment": suggested_comment,
        "created_at": datetime.now().isoformat(),
        "metadata": metadata
    }
    
    # Save to queue
    queue = load_queue()
    queue["drafts"].insert(0, draft)
    save_queue(queue)
    
    return {"status": "success", "draft": draft}

# GET: Fetch last 50 lines of logs
@app.get("/api/logs/{bot_name}")
def get_bot_logs(bot_name: str, session_id: Optional[str] = Cookie(None)):
    if not verify_session(session_id):
        raise HTTPException(status_code=401, detail="Unauthorized")
    log_file_map = {
        "linkedin": WORKSPACE_DIR / "linkedin-pipeline-local" / "interacted_posts.txt",
        "blog": WORKSPACE_DIR / "blog-pipeline-local" / "published_blogs.txt"
    }
    
    file_path = log_file_map.get(bot_name.lower())
    if not file_path or not file_path.exists():
        return {"logs": f"Log file for '{bot_name}' not found. Please trigger the bot first."}
        
    try:
        # Read last 50 lines or raw contents
        if file_path.suffix == ".json":
            with open(file_path, "r") as f:
                data = json.load(f)
                return {"logs": json.dumps(data, indent=2)}
        else:
            with open(file_path, "r") as f:
                lines = f.readlines()
                return {"logs": "".join(lines[-50:])}
    except Exception as e:
        return {"logs": f"Failed to read logs: {e}"}

# POST: Trigger Bot Script (Background execution)
@app.post("/api/trigger/{bot_name}")
def trigger_bot(bot_name: str, background_tasks: BackgroundTasks, session_id: Optional[str] = Cookie(None)):
    if not verify_session(session_id):
        raise HTTPException(status_code=401, detail="Unauthorized")
    bot_commands = {
        "linkedin": (WORKSPACE_DIR / "linkedin-pipeline-local", "python auto_finder.py"),
        "blog": (WORKSPACE_DIR / "blog-pipeline-local", "python blog_bot.py")
    }
    
    trigger_info = bot_commands.get(bot_name.lower())
    if not trigger_info:
        raise HTTPException(status_code=400, detail="Invalid bot name")
        
    cwd, command = trigger_info
    
    def run_script(cmd, path):
        import subprocess
        logger.info(f"Triggering background command '{cmd}' in {path}")
        subprocess.run(cmd, cwd=path, shell=True)
        
    background_tasks.add_task(run_script, command, cwd)
    return {"status": "success", "message": f"Bot '{bot_name}' has been triggered in the background."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

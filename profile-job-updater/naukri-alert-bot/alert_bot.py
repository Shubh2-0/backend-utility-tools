#!/usr/bin/env python3
"""
Java Job Alert Bot for Naukri
Searches Java jobs every 10 min, filters 3yr exp + posted last 24h,
dedupes by job_id, sends alerts via Telegram and/or WhatsApp.

Runs on AWS Mumbai VM via cron. Zero ban risk — only GET requests, no apply.
"""

import os
import json
import time
import logging
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

import sys
NOPERI_PATH = Path.home() / "NopeRi"
sys.path.insert(0, str(NOPERI_PATH))

from src.client.naukri_client import NaukriLoginClient
from src.client.job_client import NaukriJobClient

load_dotenv(NOPERI_PATH / ".env")
load_dotenv(Path.home() / "naukri-alert-bot" / ".env", override=False)

SEARCH_KEYWORD = os.getenv("SEARCH_KEYWORD", "Java")
EXPERIENCE = int(os.getenv("EXPERIENCE", "3"))
MAX_ALERTS_PER_RUN = int(os.getenv("MAX_ALERTS_PER_RUN", "10"))
STATE_FILE = Path.home() / "naukri-alert-bot" / "seen_jobs.json"
LOG_FILE = Path.home() / "naukri-alert-bot" / "alert_bot.log"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE", "").strip()
CALLMEBOT_API_KEY = os.getenv("CALLMEBOT_API_KEY", "").strip()

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("alert_bot")


def load_seen_jobs():
    if not STATE_FILE.exists():
        return {}
    try:
        data = json.loads(STATE_FILE.read_text())
        cutoff = (datetime.utcnow() - timedelta(days=7)).isoformat()
        return {k: v for k, v in data.items() if v >= cutoff}
    except Exception as e:
        log.warning(f"State file corrupt, resetting: {e}")
        return {}


def save_seen_jobs(seen):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(seen, indent=2))


def is_posted_within_24h(posted_text):
    if not posted_text:
        return False
    pt = posted_text.lower().strip()
    same_day = ("just now", "few", "minute", "hour", "today", "1 day ago")
    return any(token in pt for token in same_day)


def send_telegram(message_html):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return None

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_html,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    try:
        r = requests.post(url, json=payload, timeout=30)
        if r.status_code == 200 and r.json().get("ok"):
            log.info("Telegram sent OK")
            return True
        log.error(f"Telegram failed: HTTP {r.status_code} body={r.text[:300]}")
    except Exception as e:
        log.error(f"Telegram exception: {e}")
    return False


def send_whatsapp(message_plain):
    if not WHATSAPP_PHONE or not CALLMEBOT_API_KEY:
        return None

    phone = WHATSAPP_PHONE.lstrip("+").replace(" ", "")
    encoded = urllib.parse.quote(message_plain)
    url = (
        f"https://api.callmebot.com/whatsapp.php"
        f"?phone={phone}&text={encoded}&apikey={CALLMEBOT_API_KEY}"
    )

    try:
        r = requests.get(url, timeout=30)
        if r.status_code == 200 and ("Message queued" in r.text or "Message sent" in r.text):
            log.info("WhatsApp sent OK")
            return True
        log.error(f"WhatsApp failed: HTTP {r.status_code} body={r.text[:200]}")
    except Exception as e:
        log.error(f"WhatsApp exception: {e}")
    return False


def send_alert(job):
    html_msg = format_job_message_html(job)
    plain_msg = format_job_message_plain(job)

    tg = send_telegram(html_msg)
    wa = send_whatsapp(plain_msg)

    if tg is None and wa is None:
        log.error("No notification channels configured (Telegram or WhatsApp)")
        return False
    return bool(tg) or bool(wa)


def _safe_str(v):
    if v is None:
        return ""
    if isinstance(v, dict):
        for k in ("label", "text", "value", "name", "title"):
            if v.get(k):
                return str(v[k])
        return ""
    if isinstance(v, (list, tuple)):
        return ", ".join(_safe_str(x) for x in v if x)
    return str(v)


def html_escape(s):
    return _safe_str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _apply_url(job):
    url = _safe_str(job.apply_link)
    if url and not url.startswith("http"):
        url = "https://www.naukri.com" + url
    return url


def format_job_message_html(job):
    skills = ", ".join(_safe_str(t) for t in (job.tags[:5] if job.tags else [])) or "N/A"
    return (
        f"<b>NEW JAVA JOB</b>\n\n"
        f"<b>Role:</b> {html_escape(job.title)}\n"
        f"<b>Company:</b> {html_escape(job.company)}\n"
        f"<b>Location:</b> {html_escape(job.location)}\n"
        f"<b>Salary:</b> {html_escape(job.salary)}\n"
        f"<b>Posted:</b> {html_escape(job.posted_date)}\n"
        f"<b>Skills:</b> {html_escape(skills)}\n\n"
        f'<a href="{html_escape(_apply_url(job))}">Apply on Naukri</a>'
    )


def format_job_message_plain(job):
    skills = ", ".join(_safe_str(t) for t in (job.tags[:5] if job.tags else [])) or "N/A"
    return (
        f"NEW JAVA JOB\n\n"
        f"Role: {_safe_str(job.title)}\n"
        f"Company: {_safe_str(job.company)}\n"
        f"Location: {_safe_str(job.location)}\n"
        f"Salary: {_safe_str(job.salary)}\n"
        f"Posted: {_safe_str(job.posted_date)}\n"
        f"Skills: {skills}\n\n"
        f"Apply: {_apply_url(job)}"
    )


def main():
    log.info("=" * 60)
    log.info(f"Alert bot run start | keyword={SEARCH_KEYWORD} | exp={EXPERIENCE}")

    seen = load_seen_jobs()
    log.info(f"Loaded {len(seen)} seen jobs from state")

    username = os.getenv("USERNAME") or os.getenv("NAUKRI_USERNAME")
    password = os.getenv("PASSWORD") or os.getenv("NAUKRI_PASSWORD")
    if not username or not password:
        log.error("Naukri credentials missing")
        return

    try:
        client = NaukriLoginClient(username, password)
        client.login()
        log.info("Naukri login OK")
    except Exception as e:
        log.error(f"Login failed: {e}")
        return

    jc = NaukriJobClient(client)
    all_jobs = []
    try:
        for page in (1, 2):
            page_jobs = jc.search_jobs(
                keyword=SEARCH_KEYWORD,
                location="",
                experience=EXPERIENCE,
                page=page,
            )
            if not page_jobs:
                break
            all_jobs.extend(page_jobs)
            time.sleep(2)
        log.info(f"Search returned {len(all_jobs)} jobs across pages")
    except Exception as e:
        log.error(f"Search failed: {e}")
        return

    new_jobs = []
    for job in all_jobs:
        if not job.job_id or job.job_id in seen:
            continue
        if not is_posted_within_24h(job.posted_date):
            continue
        new_jobs.append(job)
        seen[job.job_id] = datetime.utcnow().isoformat()
        if len(new_jobs) >= MAX_ALERTS_PER_RUN:
            break

    log.info(f"New jobs to alert: {len(new_jobs)}")

    sent = 0
    for job in new_jobs:
        if send_alert(job):
            sent += 1
        time.sleep(3)

    save_seen_jobs(seen)
    log.info(f"Run done | sent={sent}/{len(new_jobs)} | total seen={len(seen)}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log.exception(f"Fatal error: {e}")

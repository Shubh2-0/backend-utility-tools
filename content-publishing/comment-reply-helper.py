"""
Fetch recent Dev.to comments on your articles and suggest replies via Groq.

Strategy: We DON'T auto-post replies (looks spammy + comment quality drives
algorithm reach). We surface unanswered comments and draft 2 reply variants
for you to copy-paste manually.

Usage:
    DEV_TO_API_KEY=... GROQ_API_KEY=... python comment-reply-helper.py
    # Optional flags:
    #   --user shubham_bhati     (Dev.to username; defaults to env DEV_TO_USERNAME)
    #   --limit 20               max articles to scan
    #   --since 7                only flag comments from last N days
"""

import argparse
import datetime
import json
import os
import sys
import time
from pathlib import Path

import requests

GROQ_API = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"
DEFAULT_USER = "shubham_bhati"


def fetch_my_articles(api_key: str, limit: int = 20) -> list[dict]:
    r = requests.get(
        f"https://dev.to/api/articles/me",
        headers={"api-key": api_key},
        params={"per_page": limit},
        timeout=30,
    )
    if r.status_code != 200:
        sys.exit(f"Dev.to list my articles failed: {r.status_code} {r.text[:300]}")
    return r.json()


def fetch_comments(article_id: int) -> list[dict]:
    r = requests.get(
        "https://dev.to/api/comments",
        params={"a_id": article_id},
        timeout=30,
    )
    if r.status_code != 200:
        return []
    return r.json()


def draft_replies(groq_key: str, article_title: str, comment_text: str, commenter: str) -> list[str]:
    prompt = f"""You are Shubham Bhati, a senior backend engineer who writes article "{article_title}" on Dev.to.
Someone named {commenter} left this comment:

\"\"\"{comment_text[:600]}\"\"\"

Write TWO short, distinct reply options (each 40-90 words). Tone: friendly, helpful, slightly opinionated. Don't be overly formal. If they asked a question, answer it. If they shared a take, engage with it (agree or thoughtfully push back). Avoid "Great question!" openers. No emojis except occasionally one at the end.

Format:
OPTION A:
<reply>

OPTION B:
<reply>"""
    r = requests.post(
        GROQ_API,
        headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
        data=json.dumps({
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.85,
            "max_tokens": 500,
        }),
        timeout=60,
    )
    if r.status_code != 200:
        return [f"[Groq error: {r.status_code}]"]
    return [r.json()["choices"][0]["message"]["content"].strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--since", type=int, default=14, help="Days back to flag comments")
    ap.add_argument("--out", default="comment-replies.md", help="Output markdown file")
    args = ap.parse_args()

    devto_key = os.environ.get("DEV_TO_API_KEY")
    groq_key = os.environ.get("GROQ_API_KEY")
    if not devto_key:
        sys.exit("DEV_TO_API_KEY not set")
    if not groq_key:
        sys.exit("GROQ_API_KEY not set")

    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=args.since)

    print(f"Fetching your Dev.to articles (limit {args.limit})...")
    articles = fetch_my_articles(devto_key, args.limit)
    print(f"  found {len(articles)} articles\n")

    output_lines = [f"# Comment replies — {datetime.date.today().isoformat()}\n"]
    total_comments = 0

    for art in articles:
        comments = fetch_comments(art["id"])
        if not comments:
            continue
        # Each comment has a "children" structure (replies). Filter top-level.
        recent = [
            c for c in comments
            if not c.get("user", {}).get("username", "").startswith("shubham")
        ]
        if not recent:
            continue
        print(f"  '{art['title'][:50]}...' — {len(recent)} comment(s)")
        output_lines.append(f"\n## {art['title']}")
        output_lines.append(f"_Article: {art['url']}_\n")

        for c in recent:
            commenter = c.get("user", {}).get("username", "anonymous")
            body = c.get("body_html") or ""
            # crude strip of HTML
            text = body.replace("<p>", "").replace("</p>", "\n").replace("<br>", "\n")
            text = "".join(ch for ch in text if ch != "\n" or ch).strip()
            output_lines.append(f"### Comment from @{commenter}")
            output_lines.append(f"> {text[:400]}\n")

            print(f"    drafting reply for @{commenter}...")
            drafts = draft_replies(groq_key, art["title"], text, commenter)
            for d in drafts:
                output_lines.append(f"**Suggested replies:**\n\n{d}\n")
            total_comments += 1
            time.sleep(2)

    if total_comments == 0:
        output_lines.append("\n_No new comments to reply to. Nice and quiet._\n")

    Path(args.out).write_text("\n".join(output_lines), encoding="utf-8")
    print(f"\nDone. {total_comments} comment(s) drafted into {args.out}")


if __name__ == "__main__":
    main()

import os
import re
import json
import urllib.request
import time

# Helper to strip Oxford commas
_OXFORD_COMMA_RE = re.compile(r',\s+and\b')
def strip_oxford_comma(text):
    return _OXFORD_COMMA_RE.sub(' and', text)

def call_gemini(api_key, prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    system_instruction = (
        "You are Shubham Bhati, a Java Spring Boot Developer and backend engineer. "
        "Write a short, intelligent, and helpful comment on a developer's blog post. "
        "Keep it positive, professional, and conversational. State your technical view, "
        "ask a relevant follow-up question, or share a brief insight."
    )
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"{system_instruction}\n\nPrompt: {prompt}"
            }]
        }]
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            raw_text = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
            return strip_oxford_comma(raw_text)
    except Exception as e:
        print(f"[ERROR] Failed to generate comment from Gemini: {e}")
        return None

def fetch_articles(tag):
    url = f"https://dev.to/api/articles?tag={tag}&per_page=3"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"[ERROR] Failed to fetch articles for tag {tag}: {e}")
        return []

def post_comment(devto_key, article_id, comment_body):
    url = "https://dev.to/api/comments"
    payload = {
        "comment": {
            "body_markdown": comment_body,
            "commentable_id": article_id,
            "commentable_type": "Article"
        }
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "api-key": devto_key,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            print(f"[SUCCESS] Comment posted on article ID {article_id}!")
            return True
    except Exception as e:
        print(f"[ERROR] Failed to post comment on article ID {article_id}: {e}")
        return False

def main():
    gemini_key = os.environ.get("GEMINI_API_KEY")
    devto_key = os.environ.get("DEVTO_API_KEY")
    
    if not gemini_key or not devto_key:
        print("[ERROR] Missing GEMINI_API_KEY or DEVTO_API_KEY environment variables.")
        return
        
    processed_file = "processed_articles.txt"
    
    # Read processed article IDs
    processed_ids = set()
    if os.path.exists(processed_file):
        with open(processed_file, "r") as f:
            for line in f:
                if line.strip():
                    processed_ids.add(line.strip())
                    
    target_tags = ["java", "springboot", "systemdesign", "redis", "kafka"]
    my_usernames = ["shubhambhati", "bhatishubham", "shubh2-0", "shubham_bhati"]
    
    comments_made = 0
    
    for tag in target_tags:
        print(f"[*] Checking tag: #{tag}...")
        articles = fetch_articles(tag)
        for article in articles:
            # Prevent commenting too many times in one run (limit to 3 comments per run to look natural and avoid bans)
            if comments_made >= 3:
                print("[*] Reached max comment limit (3) for this run. Stopping.")
                return
                
            article_id = str(article.get("id"))
            title = article.get("title")
            description = article.get("description", "")
            author_username = article.get("user", {}).get("username", "").lower()
            
            # Skip if already processed, or if it is our own article
            if article_id in processed_ids:
                continue
            if author_username in my_usernames:
                continue
                
            print(f"[*] Found new article: '{title}' by @{author_username}")
            
            prompt = (
                f"Create a short, engaging, and professional technical reply comment for the post:\n"
                f"Title: {title}\n"
                f"Description: {description}\n\n"
                f"Requirements:\n"
                f"1. Make it encouraging and technically sound.\n"
                f"2. Keep it brief (2 to 3 sentences max).\n"
                f"3. Do NOT use emojis, hashtags, or Oxford commas (comma before 'and')."
            )
            
            comment = call_gemini(gemini_key, prompt)
            if not comment:
                continue
                
            print(f"[*] Generated Comment: {comment}")
            success = post_comment(devto_key, article_id, comment)
            
            if success:
                processed_ids.add(article_id)
                with open(processed_file, "a") as f:
                    f.write(article_id + "\n")
                comments_made += 1
                
                # Sleep to prevent hitting rate limits
                time.sleep(5)
                
if __name__ == "__main__":
    main()

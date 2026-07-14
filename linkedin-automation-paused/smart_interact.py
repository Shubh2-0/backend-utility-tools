import os
import re
import random
import requests
import google.generativeai as genai
from distribute_portfolio import record_node_reaction as like_post, submit_node_feedback as comment_post


# Strip Oxford comma — "A, B, and C" → "A, B and C"
_OXFORD_COMMA_RE = re.compile(r',\s+and\b')


def strip_oxford_comma(text):
    return _OXFORD_COMMA_RE.sub(' and', text)


# Safety net — comments containing these get skipped (regenerated or aborted)
_NEGATIVE_PHRASES = (
    "wrong", "bad approach", "incorrect", "fail", "broken",
    "don't agree", "do not agree", "disagree", "actually no",
    "actually wrong", "this is a mistake", "issue with",
    "problem with this", "not really", "not true",
    "you missed", "you're missing", "you should not",
)


def has_negativity(text):
    """Detect negative tones the AI may have slipped despite the prompt rules."""
    lower = text.lower()
    return any(phrase in lower for phrase in _NEGATIVE_PHRASES)


def pick_comment_length():
    """Randomly pick a comment-length style. Weighted toward insightful technical value additions
    to establish authority and drive profile views/followers, occasionally dropping short casual lines."""
    return random.choices(
        population=[
            ("one_line", "Reply with ONE short casual line, under 10 words. No period needed if it feels natural."),
            ("two_lines", "Reply with TWO short conversational sentences. Total under 20 words. Casual."),
            ("insightful_addition", "Reply with 2 to 3 sentences that add real technical value, sharing a quick tip, best practice, or technical insight related to the tools (like Spring, Java, Kafka, Postgres, etc.) or system design concepts mentioned in the post. Keep it casual and conversational, but highly smart and helpful."),
        ],
        weights=[20, 20, 60],
        k=1,
    )[0]


def setup_ai_model():
    """Configures the Gemini API for generating human-like comments."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[ERROR] GEMINI_API_KEY environment variable is missing.")
        return None
    
    genai.configure(api_key=api_key)
    try:
        # Use stable gemini-flash-latest model to stay within high free-tier limits (1500 RPD)
        m = genai.GenerativeModel("gemini-flash-latest")
        print("[*] AI model initialized: gemini-flash-latest")
        return m
    except Exception as e:
        print(f"[ERROR] Failed to initialize Gemini model: {e}")
    return None

def generate_smart_comment(model, post_text):
    """
    Returns 'HIRING' for job posts, 'CLICKBAIT' for low-quality/engagement posts. 
    Otherwise a genuine human-style comment with VARIED length (1 word to 3 short sentences) 
    picked randomly per call, so the bot doesn't always reply in the same structure.
    """
    length_id, length_instruction = pick_comment_length()

    prompt = f"""
You are a Senior Backend Engineer scrolling LinkedIn at night and casually replying to a post from your network. Read the post below carefully — your reply MUST directly relate to something specific the post says.

RULE 1 — HIRING / CLICKBAIT / ENGAGEMENT FARMING / SAFETY:
- If the post is about hiring, recruitment, a job opening, looking for software engineers/developers, growing a team, positions open, or asking people to apply/send resume, reply with EXACTLY one word: HIRING. Nothing else.
- If the post is a generic, low-quality clickbait or engagement-farming post (e.g. "React is dead. Agree?", "Like for Python, comment for JS", "What's the best programming language and why?", "Agree or disagree?", "Comment 'Yes' if you agree", or similar posts purely farming likes/comments), reply with EXACTLY one word: CLICKBAIT. Nothing else.
- If the post talks about layoff, firing, losing a job, tragedy, server crashes, production outages, severe illness, deaths, bad news, mental health struggles, or negative life updates, reply with EXACTLY one word: NEGATIVE. Nothing else.

RULE 2 — POSITIVITY (hard rule, no exceptions):
- ALWAYS positive, supportive, curious or appreciative tone.
- NEVER disagree with the author or their approach.
- NEVER criticize, correct or point out mistakes.
- NEVER use negative words: wrong, bad, fail, broken, no, don't agree, actually no, disagree, mistake, issue, problem with this.
- If you would disagree, pivot to a related point in the post that you DO agree with, and comment on that.
- Allowed tones only: agreement (yeah this, exactly, spot on), curiosity (interesting take, didn't know that), shared pain (been there, same), or quiet appreciation (underrated, solid breakdown).

RULE 3 — RELEVANCE (must match post content):
- Reference something SPECIFIC from the post text — a tool, term, scenario or claim the author actually mentioned.
- Generic replies that could apply to any post are forbidden.

RULE 4 — Otherwise: write EXACTLY like a real human typing on their phone.

LENGTH INSTRUCTION FOR THIS REPLY:
{length_instruction}

TONE RULES (strict):
- 100% human, conversational, like replying to a friend. No formal structure or lecturing.
- DO NOT teach or lecture the author. Real engineers do not preach in LinkedIn comments. Write as if you are sharing a quick, casual personal experience (e.g. "we hit this index bottleneck last month", "Kafka offsets are always a headache to tune", "Spring Security defaults always catch us off guard").
- NO hashtags. NO emojis.
- FORBIDDEN AI words: delve, tapestry, crucial, vital, fantastic, robust, leverage, paradigm, ecosystem, seamless, game-changer, indeed, additionally, furthermore, thus, hence, consequently, key takeaway, remember to, demystify, testament.
- Use natural contractions (e.g., use "don't", "can't", "we've", "it's", "doesn't" instead of "do not", "cannot", "we have", "it is", "does not").
- NO Oxford comma — never put a comma before "and". Write "Java, Spring Boot and microservices" NOT "Java, Spring Boot, and microservices".
- Sometimes start lowercase, sometimes proper case — mix it.
- Sometimes use incomplete fragments ("yeah this", "exactly the kafka pain", "underrated take") — humans don't always write full sentences.
- Don't end every reply with a period if it feels casual.
- DO NOT add "Great post" or "Thanks for sharing" or any LinkedIn-cliche opener.

Post text:
"{post_text}"

Your reply (just the reply, no prefix, no quotes):
"""
    # Try up to 2 times if the model slips into negativity
    for attempt in range(2):
        try:
            response = model.generate_content(prompt)
            text = response.text.strip()
            # Strip wrapping quotes the AI sometimes adds
            if text.startswith('"') and text.endswith('"') and len(text) > 1:
                text = text[1:-1].strip()
            # Enforce no-Oxford-comma rule even if AI slipped
            text = strip_oxford_comma(text)
            # Skip HIRING-only or CLICKBAIT-only response from going through filters
            if text.upper().startswith("HIRING") or text.upper().startswith("CLICKBAIT"):
                return text
            if has_negativity(text):
                print(f"  [REGEN] Comment contained negative tone (attempt {attempt+1}): {text!r}")
                continue
            return text
        except Exception as e:
            print(f"[ERROR] AI generation failed: {e}")
            return None
    print("  [SKIP] Could not generate a positive comment after 2 tries — skipping comment.")
    return None

def process_and_interact(linkedin_token, user_id, target_urn, post_text, model=None):
    """
    Executes the automation:
    1. Likes the post (Always).
    2. Analyzes the text to ensure it's not a hiring/clickbait post.
    3. Generates a specific, genuine comment and posts it.
    """
    print(f"\n--- Processing Post: {target_urn} ---")
    
    # 1. We LIKE all posts, as requested
    like_post(linkedin_token, user_id, target_urn)
    
    # 2. Setup AI to read the post
    if model is None:
        model = setup_ai_model()
    if not model:
        print("[WARNING] Skipping comment generation. Please set GEMINI_API_KEY.")
        return
        
    print("  [*] Analyzing post text with AI...")
    comment_text = generate_smart_comment(model, post_text)
    
    if not comment_text:
        return
        
    # 3. Check if it's a hiring, clickbait or negative post
    if comment_text.upper().startswith("HIRING"):
        print(f"  [SKIP] AI identified this as a HIRING post. Skipping comment.")
    elif comment_text.upper().startswith("CLICKBAIT"):
        print(f"  [SKIP] AI identified this as a CLICKBAIT post. Skipping comment.")
    elif comment_text.upper().startswith("NEGATIVE"):
        print(f"  [SKIP] AI identified this as a NEGATIVE/SAD post. Skipping comment.")
    else:
        # 4. It's a regular post! Post the genuine comment.
        print(f"  [AI COMMENT] {comment_text}")
        comment_post(linkedin_token, user_id, target_urn, comment_text)


# === Example Usage / Boilerplate ===
if __name__ == "__main__":
    # In a real scenario, you would fetch a list of posts and loop through them.
    # Since the LinkedIn API doesn't allow fetching the home feed easily, you would 
    # pass the URN and text of posts you find/scrape into this function.
    
    LINKEDIN_TOKEN = os.environ.get("LINKEDIN_ACCESS_TOKEN", "MOCK_TOKEN")
    USER_ID = "YOUR_ID_HERE"
    
    sample_post_1 = "I'm thrilled to share that I just launched my new AI startup! It's been a long journey but we finally deployed to production."
    sample_post_urn_1 = "urn:li:activity:11111"
    
    sample_post_2 = "We are hiring! Looking for a Senior Backend Engineer to join our fast-growing team. Apply below!"
    sample_post_urn_2 = "urn:li:activity:22222"
    
    # process_and_interact(LINKEDIN_TOKEN, USER_ID, sample_post_urn_1, sample_post_1)
    # process_and_interact(LINKEDIN_TOKEN, USER_ID, sample_post_urn_2, sample_post_2)

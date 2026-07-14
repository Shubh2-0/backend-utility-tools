"""
Comment Templates for Maa Kaali Creations (@maakaali_creations)
100% promotional — every comment drives traffic to the brand.

Safety features built-in:
- Variation system (prefix/suffix/emoji/filler) so no two comments are identical
- Niche keywords for targeting relevant reels only
"""

import random
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemini Client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
gemini_client = None
if GEMINI_API_KEY:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    
BRAND_TAG = ""
BRAND_HASHTAG = ""

# ── TECH/CODING TEMPLATES ──────────────────────────────────────────

TEMPLATES = [
    "Spot on! We hit this exact database bottleneck last month and had to rewrite our indexes.",
    "Been there! Dealing with race conditions in distributed systems is always a headache.",
    "Haha true! Compiler errors are way better than silent production bugs.",
    "Dockerizing everything is fun until you check the image sizes.",
    "Exactly. Using standard connection pooling limits is so underrated.",
    "Underrated tip! People always forget about N+1 query problems until production lags.",
    "Yeah, CompletableFuture can get really messy if exception handling isn't configured properly.",
    "Redis caching is great but eviction policies always catch people off guard.",
    "Spot on, standardizing API responses early saves so much frontend coordination headache.",
    "Yeah, Kafka partitions are easy to understand but a pain to scale dynamically.",
    "Spot on! PostgreSQL indexing defaults are good but fine-tuning them is always worth it.",
    "Definitely. Using clean code principles early prevents a lot of legacy debt.",
    "Totally agree. Microservices are great but sometimes a clean monolith is all you need."
]

# ── VARIATION SYSTEM (makes each comment unique) ────────────────────

PREFIXES = [
    "", "", "", "", "",  # 50% no prefix
    "Honestly, ",
    "Sach batau toh ",
    "Bhai ",
    "Yaar ",
    "Arre ",
]

SUFFIXES = [
    "", "", "", "", "",  # 50% no suffix
    ". Highly recommend",
    ". Must try",
    ". Worth it",
    ". Check it out",
    ". Trust me on this",
    ". No regrets",
]

EMOJIS = [
    " ✨", " 🔥", " 💻", " 💯", " 👌",
    " 🙌", "", "", "", "", "", "", "", "",
]

# ── NICHE KEYWORDS (for filtering relevant reels) ───────────────────

NICHE_KEYWORDS = [
    "springboot", "spring boot", "java", "backend", "microservices", "system design",
    "developer", "coding", "programming", "programmer", "database", "sql", "postgres",
    "kafka", "docker", "kubernetes", "api", "rest api", "software engineer", "computer science",
    "git", "github", "bug", "debugging", "production", "server", "architecture"
]

# Track recently used templates to avoid repetition in same session
_recent_indices = []


def get_random_comment(caption: str = "") -> str:
    """
    Pick a unique tech comment.
    If a caption is provided and Gemini API key is set, it will try to generate an AI comment perfectly tailored to the caption.
    If AI fails or no caption/key is provided, it falls back to the random variation system.
    """
    global _recent_indices

    # ---- AI COMMENT GENERATION ----
    if caption and gemini_client:
        try:
            # Clean caption slightly
            clean_caption = caption.strip()[:300] if caption else "Coding topic"
            
            prompt = f"""
            You are a Senior Backend Engineer scrolling Instagram Reels. Read the reel's caption: "{clean_caption}"
            
            Write a short, friendly, and natural Hinglish (mixture of Hindi and English) or casual English comment responding to the tech tip, coding joke, or engineering topic.
            - Write it exactly how a real experienced programmer would casually reply to a colleague.
            - Keep it strictly under 2 sentences (less than 20 words). Sound casual, smart, and direct.
            - Do NOT use hashtags, do NOT use emojis, and do NOT use corporate AI buzzwords (like "Delve", "Tapestry", "Crucial", "Vital", "Fantastic").
            - Use natural contractions (e.g. use "don't", "can't", "it's").
            - Connect specifically to a technical point made in the text.
            - DO NOT pitch any product, link, or brand name.
            
            - SPECIAL RULE FOR SAFETY:
              If the caption is about tragedy, layoffs, firing, losing a job, severe illness, accidents, deaths, server crashes, production outages, bad news, mental health struggles, or negative life updates, return exactly the word: NEGATIVE. Nothing else.
            """
            
            # Using Gemini 2.5 Flash for fast, cheap, and good text generation
            response = gemini_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            
            generated_text = response.text.strip().replace('"', '').replace("'", "")
            
            # Fallback check - make sure it generated something sensible
            if len(generated_text) > 10:
                return generated_text
                
        except Exception as e:
            print(f"Gemini AI generation failed: {e}. Falling back to templates.")
            pass # Fall back to template system below


    # ---- STATIC TEMPLATE FALLBACK ----
    # Pick a template we haven't used recently
    available = [i for i in range(len(TEMPLATES)) if i not in _recent_indices]
    if not available:
        _recent_indices.clear()
        available = list(range(len(TEMPLATES)))

    idx = random.choice(available)
    _recent_indices.append(idx)
    # Keep last 10 indices to avoid repeats
    if len(_recent_indices) > 10:
        _recent_indices.pop(0)

    template = TEMPLATES[idx]
    body = template

    # Add random prefix
    prefix = random.choice(PREFIXES)

    # Add random suffix
    suffix = random.choice(SUFFIXES)

    # Add random emoji
    emoji = random.choice(EMOJIS)

    comment = f"{prefix}{body}{suffix}{emoji}"

    return comment.strip()


def is_niche_relevant(caption: str) -> bool:
    """Check if a reel's caption matches tech/coding/backend niche."""
    if not caption:
        return False
    caption_lower = caption.lower()
    return any(kw in caption_lower for kw in NICHE_KEYWORDS)

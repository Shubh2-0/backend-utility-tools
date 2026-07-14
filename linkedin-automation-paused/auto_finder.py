import os
import re
import time
import random
from datetime import datetime
try:
    from duckduckgo_search import DDGS
except ImportError:
    from ddgs import DDGS
from smart_interact import process_and_interact, setup_ai_model
from distribute_portfolio import fetch_urn_owner_id as get_user_id, record_node_reaction as like_post


# === Run-tunable constants ===
LIKES_PER_RUN = 20         # 4 runs/day × 20 = 80/day — safe upper limit
COMMENTS_PER_RUN = 5       # 4 runs/day × 5 = 20 comments/day
QUERIES_PER_DAY = 4        # broader topic coverage = more candidates
MAX_RESULTS_PER_QUERY = 50 # was 30 — need more candidates for higher likes
MIN_SLEEP_SEC = 8          # was 5 — slightly longer pauses look more human
MAX_SLEEP_SEC = 20         # was 15

# Rotating query pool — 15 different angles focused on top Indian tech creators
# and local Indian tech hubs to maximize engagement and impressions.
SEARCH_QUERIES = [
    'site:linkedin.com/posts "Spring Boot" India',
    'site:linkedin.com/posts "microservices" java India',
    'site:linkedin.com/posts "system design" India',
    'site:linkedin.com/posts "kunal-kushwaha"',
    'site:linkedin.com/posts "akshay-saini" OR "namaste javascript"',
    'site:linkedin.com/posts "hitesh-choudhary"',
    'site:linkedin.com/posts "sanket-singh" backend',
    'site:linkedin.com/posts "love-babbar"',
    'site:linkedin.com/posts "tanay-pratap"',
    'site:linkedin.com/posts "spring boot" bangalore OR gurgaon OR noida',
    'site:linkedin.com/posts "system design" microservices backend India',
    'site:linkedin.com/posts "backend engineer" India',
    'site:linkedin.com/posts "java developer" tips India',
    'site:linkedin.com/posts "distributed systems" India',
    'site:linkedin.com/posts "kafka" java India',
]

EXCLUDE_TERMS = (
    'hiring', 'we are hiring', 'job opening', 'apply now',
    'growing my team', 'growing our team', 'grow my team',
    'looking for software', 'looking for engineers', 'looking for developers',
    'join our team', 'join us as', 'recruiting', 'we are recruiting',
    'open position', 'open positions', 'job description', 'hiring for',
    'vacancy', 'vacancies', 'careers at'
)


def pick_queries_for_today(k=None):
    """Deterministic per-day query rotation — different days, different topics."""
    k = k or QUERIES_PER_DAY
    seed = datetime.utcnow().toordinal()
    rng = random.Random(seed)
    return rng.sample(SEARCH_QUERIES, k=k)


ACTIVITY_RE = re.compile(r'activity[-:](\d+)')


def is_linkedin_post(url):
    """Pre-filter: only accept LinkedIn post URLs with an activity ID."""
    if not url or "linkedin.com/posts/" not in url:
        return False
    return bool(ACTIVITY_RE.search(url))


def search_linkedin_posts():
    """Search across multiple queries, dedupe by URL, pre-filter for LinkedIn post URLs only."""
    queries = pick_queries_for_today()
    print(f"[*] Today's query rotation ({len(queries)} queries):")
    for q in queries:
        print(f"     - {q}")

    seen_urls = set()
    all_results = []

    for query in queries:
        try:
            results = list(DDGS().text(query, max_results=MAX_RESULTS_PER_QUERY, timelimit='w'))
        except Exception as e:
            print(f"  [ERROR] Query '{query[:40]}...' failed: {e}")
            continue

        kept = 0
        for r in results:
            url = r.get("href", "")
            if not is_linkedin_post(url):
                continue
            if url in seen_urls:
                continue
            seen_urls.add(url)
            all_results.append(r)
            kept += 1
        print(f"  [{query[:50]}...] → {len(results)} raw, {kept} LinkedIn posts kept")

    print(f"[*] Total deduped LinkedIn post candidates: {len(all_results)}")
    return all_results


def find_and_interact():
    print("=== LinkedIn Auto-Finder Started ===")

    history_file = "interacted_posts.txt"
    interacted_urns = set()
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            interacted_urns = set(line.strip() for line in f.readlines())
    print(f"[*] Already interacted with {len(interacted_urns)} posts historically")

    token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
    if not token or token == "DUMMY_TOKEN":
        print("[ERROR] Real LINKEDIN_ACCESS_TOKEN not set!")
        user_id = "YOUR_ID_HERE"
    else:
        user_id = get_user_id(token)
        print(f"[*] Dynamically fetched User ID: {user_id}")

    model = setup_ai_model()
    results = search_linkedin_posts()

    # Shuffle so we don't always engage with the top result from query #1
    random.shuffle(results)

    comments_made = 0
    likes_made = 0
    skipped_seen = 0

    for r in results:
        if likes_made >= LIKES_PER_RUN:
            print(f"[*] Reached run limit of {LIKES_PER_RUN} likes. Stopping.")
            break

        url = r.get("href", "")
        snippet = (r.get("body") or "").strip()

        match = ACTIVITY_RE.search(url)
        if not match:
            continue  # Defensive — pre-filter should have caught
        post_urn = f"urn:li:activity:{match.group(1)}"

        if post_urn in interacted_urns:
            skipped_seen += 1
            continue

        # Quick hiring-keyword skip before spending AI quota
        lower_snip = snippet.lower()
        if any(term in lower_snip for term in EXCLUDE_TERMS):
            print(f"  [SKIP] Likely hiring post (keyword match): {url}")
            continue

        print(f"\n[*] Found Fresh Post: {url}")

        # Comment on first COMMENTS_PER_RUN fresh posts, like-only the rest
        if comments_made < COMMENTS_PER_RUN:
            print(f"    Snippet: {snippet[:200]}{'...' if len(snippet) > 200 else ''}")
            process_and_interact(token, user_id, post_urn, snippet, model=model)
            comments_made += 1
        else:
            print("    [ACTION] Liking only (comment limit reached).")
            like_post(token, user_id, post_urn)

        likes_made += 1

        # Persist to history so we never re-engage
        with open(history_file, "a") as f:
            f.write(post_urn + "\n")
        interacted_urns.add(post_urn)

        # Random human-like delay (longer = looks less bot-like at higher volume)
        sleep_time = random.uniform(MIN_SLEEP_SEC, MAX_SLEEP_SEC)
        print(f"    [SLEEP] Waiting {sleep_time:.1f}s to mimic human pacing...")
        time.sleep(sleep_time)

    print()
    print(f"=== Run complete: {likes_made} likes, {comments_made} comments, "
          f"{skipped_seen} already-seen skipped ===")


if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    find_and_interact()

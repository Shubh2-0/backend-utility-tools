"""
Instagram Reel Auto-Commenter for Maa Kaali Creations
100% promotional — every comment drives traffic to @maakaali_creations.
Fully automated with 8 safety features built-in.

Safety features:
1. Comment uniqueness — variations so no two comments are identical
2. Niche targeting — only comments on fashion/wedding/saree reels
3. Human behavior — browse → wait → like → wait → comment
4. Rest days — skips 1-2 random days per week
5. Warm-up — starts slow (5/day) and increases over 2 weeks
6. Smart cooldown — 24-48hr pause after action blocks
7. Session persistence — saves login to avoid repeated logins
8. 100% promotional with natural variation patterns

Usage:
    python auto_commenter.py --dry-run                    # preview comments
    python auto_commenter.py --max-comments 10            # single session
    python auto_commenter.py --schedule                   # auto 3 sessions/day
"""

import argparse
import json
import logging
import os
import random
import time
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import List

import pyotp
from dotenv import load_dotenv
from instagrapi import Client

from comment_templates import get_random_comment

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
LOG_FILE = BASE_DIR / "comment_log.json"
DAILY_LOG_FILE = BASE_DIR / "daily_comment_count.json"
SESSION_FILE = BASE_DIR / "ig_session.json"
STATE_FILE = BASE_DIR / "bot_state.json"

# Schedule: 3 sessions per day (IST hours)
SCHEDULE_SESSIONS = {
    "morning":   {"hour": 9,  "comments": 10},
    "afternoon": {"hour": 14, "comments": 10},
    "evening":   {"hour": 20, "comments": 10},
}


class ReelAutoCommenter:
    """
    Comment on viral Indian reels from personal account.
    Every comment promotes @maakaali_creations with human-like behavior.
    """

    def __init__(self):
        self.ig_username = os.getenv("INSTAGRAM_USERNAME", "")
        self.ig_password = os.getenv("INSTAGRAM_PASSWORD", "")

        self.max_per_day = int(os.getenv("MAX_COMMENTS_PER_DAY", "30"))
        self.comments_per_session = int(os.getenv("COMMENTS_PER_SESSION", "10"))
        self.default_min_delay = int(os.getenv("COMMENT_MIN_DELAY", "180"))
        self.default_max_delay = int(os.getenv("COMMENT_MAX_DELAY", "300"))
        self.totp_key = os.getenv("INSTAGRAM_TOTP_KEY", "")

        self.client = Client()
        self.client.set_locale("en_IN")
        self.client.set_timezone_offset(19800)  # IST
        self.client.set_device({
            "app_version": "357.0.0.25.101",
            "android_version": 34,
            "android_release": "14",
            "dpi": "420dpi",
            "resolution": "1080x2400",
            "manufacturer": "samsung",
            "device": "SM-A546B",
            "model": "a54x",
            "cpu": "exynos",
            "version_code": "408932556",
        })
        self.client.set_user_agent(
            "Instagram 357.0.0.25.101 Android (34/14; 420dpi; 1080x2400; samsung; SM-A546B; a54x; exynos; en_IN; 408932556)"
        )

        self.is_logged_in = False
        self.commented_ids = self._load_commented_ids()
        self.state = self._load_state()

    # ── State management ───────────────────────────────────────────

    def _load_state(self) -> dict:
        """Load persistent bot state (first run date, cooldown, rest days, etc.)."""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, KeyError):
                pass
        return {}

    def _save_state(self):
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2)

    # ── Safety #5: Warm-up period ──────────────────────────────────

    def _get_warmup_limit(self) -> int:
        """
        Gradually increase daily limit over 2 weeks.
        Week 1: 5/day → Week 2: 15/day → After: full 30/day.
        """
        first_run = self.state.get("first_run_date")
        if not first_run:
            self.state["first_run_date"] = date.today().isoformat()
            self._save_state()
            first_run = date.today().isoformat()

        days_active = (date.today() - date.fromisoformat(first_run)).days

        if days_active < 3:
            return 5     # First 3 days: 5 comments/day
        elif days_active < 7:
            return 10    # Day 4-7: 10 comments/day
        elif days_active < 14:
            return 20    # Week 2: 20 comments/day
        else:
            return self.max_per_day  # After 2 weeks: full 30/day

    # ── Safety #4: Rest days ───────────────────────────────────────

    def _is_rest_day(self) -> bool:
        """
        Skip 1-2 random days per week. Decided at start of each day.
        Uses the day-of-year as seed so it's consistent within the day.
        """
        today = date.today()
        # Use date as seed for consistent result throughout the day
        day_seed = today.toordinal()
        rng = random.Random(day_seed)

        # Each day has ~20% chance of being a rest day (≈1-2 per week)
        return rng.random() < 0.20

    # ── Safety #6: Smart cooldown ──────────────────────────────────

    def _is_in_cooldown(self) -> bool:
        """Check if we're in a cooldown period after an action block."""
        cooldown_until = self.state.get("cooldown_until")
        if not cooldown_until:
            return False
        cooldown_time = datetime.fromisoformat(cooldown_until)
        if datetime.now() < cooldown_time:
            remaining = (cooldown_time - datetime.now()).total_seconds() / 3600
            logger.warning(f"In cooldown. Resuming in {remaining:.1f} hours.")
            return True
        # Cooldown expired, clear it
        del self.state["cooldown_until"]
        self._save_state()
        return False

    def _trigger_cooldown(self):
        """Set a 24-48 hour cooldown after action block detection."""
        hours = random.randint(24, 48)
        cooldown_until = datetime.now() + timedelta(hours=hours)
        self.state["cooldown_until"] = cooldown_until.isoformat()
        self._save_state()
        logger.warning(f"ACTION BLOCK! Entering {hours}-hour cooldown until {cooldown_until.strftime('%I:%M %p %d-%b')}.")

    # ── Safety #7: Session persistence ─────────────────────────────

    def _generate_totp_code(self) -> str:
        """Generate a 6-digit TOTP code from the secret key."""
        if not self.totp_key:
            return ""
        # Clean up key (remove spaces, dashes)
        clean_key = self.totp_key.replace(" ", "").replace("-", "").upper()
        totp = pyotp.TOTP(clean_key)
        code = totp.now()
        logger.info(f"Generated 2FA code: {code}")
        return code

    def login(self) -> bool:
        if not self.ig_username or not self.ig_password:
            logger.error("INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD must be set in .env")
            return False

        # Try loading saved session first (created by login_local.py)
        if SESSION_FILE.exists():
            try:
                logger.info("Loading saved session...")
                self.client.load_settings(SESSION_FILE)
                
                # Verify session works without calling login()
                try:
                    self.client.get_timeline_feed()
                    logger.info("Session verified — feed loaded.")
                    self.is_logged_in = True
                    return True
                except Exception as ve:
                    logger.warning(f"Saved session is invalid or expired: {ve}")
                    SESSION_FILE.unlink(missing_ok=True)
            except Exception as e:
                logger.warning(f"Failed to load settings file: {e}")
                SESSION_FILE.unlink(missing_ok=True)

        # Fresh login with 2FA support (works on local PC with residential IP)
        try:
            logger.info(f"Fresh login as {self.ig_username}...")

            if self.totp_key:
                totp_code = self._generate_totp_code()
                self.client.login(
                    self.ig_username,
                    self.ig_password,
                    verification_code=totp_code,
                )
            else:
                self.client.login(self.ig_username, self.ig_password)

            self.is_logged_in = True
            self.client.dump_settings(SESSION_FILE)
            logger.info("Login successful. Session saved.")
            return True
        except Exception as e:
            logger.error(f"Login failed: {e}")
            logger.error("If running on GitHub Actions, run 'python login_local.py --upload' from your PC first.")
            return False

    # ── Discover fashion/saree/wedding reels ─────────────────────────

    # ONLY tech-specific hashtags (aligned for Indian Tech & Java Backend)
    NICHE_HASHTAGS = [
        "springboot", "javadeveloper", "backenddeveloper", "systemdesign",
        "indianprogrammer", "indiancoder", "btech", "placements", 
        "microservices", "codingindia", "placementpreparation"
    ]

    JAVA_BACKEND_KEYWORDS = {
        "java", "springboot", "spring boot", "springframework", "spring security",
        "microservice", "hibernate", "jpa", "backend", "system design",
        "multithreading", "concurrency", "jdbc", "maven", "gradle", "database",
        "sql", "postgres", "mysql", "redis", "kafka"
    }

    INDIAN_CONTEXT_KEYWORDS = {
        "lpa", "ctc", "tcs", "infosys", "wipro", "cognizant", "hcl", "accenture",
        "placement", "btech", "mtech", "crore", "lakh", "package", "hiring",
        "interview", "dsa", "bengaluru", "bangalore", "noida", "pune", "hyderabad",
        "gurgaon", "delhi", "mumbai", "india", "offcampus", "off-campus", "chhoro",
        "yaar", "bhai", "career", "roadmaps", "job", "salaries", "salary", "prep",
        "preparations", "college", "campus", "offcampus"
    }

    def _is_tech_relevant(self, media: dict) -> bool:
        """
        Check if a post is about Java Backend/System Design and relates to the Indian tech ecosystem.
        Must have at least 1 Java/Backend keyword AND at least 1 Indian/Placement/Career keyword.
        """
        # Extract caption text
        caption_obj = media.get("caption") or {}
        caption = ""
        if isinstance(caption_obj, dict):
            caption = caption_obj.get("text", "")
        elif isinstance(caption_obj, str):
            caption = caption_obj

        if not caption:
            return False

        caption_lower = caption.lower()

        # Must match at least 1 Java backend keyword
        has_java_backend = any(kw in caption_lower for kw in self.JAVA_BACKEND_KEYWORDS)
        
        # Must match at least 1 Indian context/placement keyword
        has_indian_context = any(kw in caption_lower for kw in self.INDIAN_CONTEXT_KEYWORDS)

        return has_java_backend and has_indian_context

    def _fetch_hashtag_posts_raw(self, tag: str, amount: int = 20) -> list:
        """Fetch posts from hashtag using raw API to avoid pydantic errors."""
        posts = []
        try:
            result = self.client.private_request(
                f"tags/{tag}/sections/",
                data={
                    "tab": "recent",
                    "page": 0,
                },
            )
            sections = result.get("sections", [])

            for section in sections:
                medias = section.get("layout_content", {}).get("medias", [])
                for item in medias:
                    media = item.get("media", {})
                    if media.get("pk") or media.get("id"):
                        posts.append(media)
                    if len(posts) >= amount:
                        break
                if len(posts) >= amount:
                    break

            logger.info(f"  #{tag}: {len(posts)} posts fetched")
        except Exception as e:
            logger.warning(f"  #{tag}: fetch failed - {e}")
        return posts

    def fetch_trending_posts(self, count: int = 20) -> list:
        all_posts = []
        relevant_posts = []
        seen_ids = set()

        # Pick 4-5 random niche hashtags per session
        hashtags = random.sample(self.NICHE_HASHTAGS, min(5, len(self.NICHE_HASHTAGS)))
        logger.info(f"Searching: {', '.join(['#' + h for h in hashtags])}")

        for tag in hashtags:
            if len(relevant_posts) >= count * 2:
                break

            raw_posts = self._fetch_hashtag_posts_raw(tag, amount=20)

            for media in raw_posts:
                media_id = str(media.get("pk", media.get("id", "")))
                if media_id in seen_ids or not media_id:
                    continue
                seen_ids.add(media_id)
                all_posts.append(media)

                # Filter: only keep tech-relevant posts
                if self._is_tech_relevant(media):
                    relevant_posts.append(media)

            time.sleep(random.randint(2, 5))

        logger.info(f"Fetched {len(all_posts)} total → {len(relevant_posts)} tech-relevant posts")

        # Sort by engagement (most viral first)
        relevant_posts.sort(
            key=lambda r: (r.get("like_count", 0) or 0) + (r.get("comment_count", 0) or 0),
            reverse=True,
        )

        logger.info(f"Selected top {min(count, len(relevant_posts))} posts for commenting.")
        return relevant_posts[:count]

    # ── Comment generation ─────────────────────────────────────────

    def get_comment(self, reel: dict = None) -> str:
        """Get a unique promotional comment. Uses AI if configured and caption is available."""
        caption_text = ""
        if reel:
            caption_obj = reel.get("caption") or {}
            if isinstance(caption_obj, dict):
                caption_text = caption_obj.get("text", "")
            elif isinstance(caption_obj, str):
                caption_text = caption_obj
        
        return get_random_comment(caption=caption_text)

    # ── Safety #3: Human behavior simulation ───────────────────────

    def _simulate_human_browse(self, reel: dict):
        """Simulate human behavior: view reel → pause → like → pause."""
        media_id = self._get_media_id(reel)

        # Step 1: "View" the reel (pause as if watching)
        view_time = random.randint(5, 20)
        logger.info(f"Watching reel for {view_time}s...")
        time.sleep(view_time)

        # Step 2: Like the reel (humans like before commenting)
        try:
            self.client.media_like(media_id)
            logger.info(f"Liked reel {media_id}")
        except Exception as e:
            logger.warning(f"Like failed: {e}")

        # Step 3: Pause after liking (humans don't instantly comment)
        pause = random.randint(8, 25)
        logger.info(f"Pausing {pause}s before commenting...")
        time.sleep(pause)

    # ── Post comment ───────────────────────────────────────────────

    def _get_reel_url(self, reel: dict) -> str:
        """Get the Instagram URL for a post/reel."""
        code = reel.get("code", "")
        if code:
            return f"https://www.instagram.com/reel/{code}/"
        media_id = self._get_media_id(reel)
        return f"https://www.instagram.com/p/{media_id}/"

    def comment_on_reel(self, reel: dict, comment_text: str) -> bool:
        media_id = self._get_media_id(reel)
        reel_url = self._get_reel_url(reel)
        user_obj = reel.get("user") or {}
        username = user_obj.get("username", "?") if isinstance(user_obj, dict) else "?"
        caption_obj = reel.get("caption") or {}
        caption = ""
        if isinstance(caption_obj, dict):
            caption = caption_obj.get("text", "")[:80]
        elif isinstance(caption_obj, str):
            caption = caption_obj[:80]
        try:
            self.client.media_comment(media_id, comment_text)
            logger.info(f"POSTED on {reel_url}")
            logger.info(f"  By: @{username} | Caption: {caption}...")
            logger.info(f"  Comment: {comment_text}")
            return True
        except Exception as e:
            logger.error(f"Failed on {media_id}: {e}")
            error_str = str(e).lower()
            if "spam" in error_str or "block" in error_str or "challenge" in error_str or "feedback_required" in error_str:
                self._trigger_cooldown()
            return False

    # ── Logging ────────────────────────────────────────────────────

    def _load_commented_ids(self) -> set:
        if not LOG_FILE.exists():
            return set()
        try:
            with open(LOG_FILE, "r") as f:
                logs = json.load(f)
            return {entry["media_id"] for entry in logs}
        except (json.JSONDecodeError, KeyError):
            return set()

    def _get_media_id(self, reel: dict) -> str:
        return str(reel.get("pk", reel.get("id", "")))

    def save_log(self, reel: dict, comment: str, status: str):
        media_id = self._get_media_id(reel)
        caption_obj = reel.get("caption") or {}
        caption = ""
        if isinstance(caption_obj, dict):
            caption = caption_obj.get("text", "")[:200]
        elif isinstance(caption_obj, str):
            caption = caption_obj[:200]
        user_obj = reel.get("user") or {}
        username = user_obj.get("username", "") if isinstance(user_obj, dict) else ""

        entry = {
            "media_id": media_id,
            "username": username,
            "caption_snippet": caption,
            "comment": comment,
            "status": status,
            "timestamp": datetime.now().isoformat(),
        }

        logs = []
        if LOG_FILE.exists():
            try:
                with open(LOG_FILE, "r") as f:
                    logs = json.load(f)
            except json.JSONDecodeError:
                logs = []

        logs.append(entry)
        with open(LOG_FILE, "w") as f:
            json.dump(logs, f, indent=2)
        self.commented_ids.add(media_id)

    def _get_daily_count(self) -> int:
        today = date.today().isoformat()
        if not DAILY_LOG_FILE.exists():
            return 0
        try:
            with open(DAILY_LOG_FILE, "r") as f:
                data = json.load(f)
            return data.get(today, 0)
        except (json.JSONDecodeError, KeyError):
            return 0

    def _increment_daily_count(self):
        today = date.today().isoformat()
        data = {}
        if DAILY_LOG_FILE.exists():
            try:
                with open(DAILY_LOG_FILE, "r") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                data = {}
        data[today] = data.get(today, 0) + 1
        with open(DAILY_LOG_FILE, "w") as f:
            json.dump(data, f, indent=2)

    # ── Single session ─────────────────────────────────────────────

    def run(
        self,
        max_comments: int = 10,
        min_delay: int = 180,
        max_delay: int = 300,
        dry_run: bool = False,
    ):
        """Run a single commenting session with all safety checks."""
        session_name = datetime.now().strftime("%I:%M %p")
        logger.info(f"{'='*55}")
        logger.info(f"SESSION START — {session_name}")
        logger.info(f"{'='*55}")

        # Safety #6: Check cooldown
        if not dry_run and self._is_in_cooldown():
            logger.warning("Skipping session — in cooldown period.")
            return

        # Safety #4: Check rest day
        if not dry_run and self._is_rest_day():
            logger.info("Today is a rest day. Skipping to stay safe.")
            return

        if dry_run:
            logger.info("DRY RUN — no comments will be posted")
        else:
            if not self.is_logged_in and not self.login():
                return

        # Safety #5: Apply warm-up limit
        warmup_limit = self._get_warmup_limit()
        daily_count = self._get_daily_count()
        remaining = warmup_limit - daily_count

        if remaining <= 0:
            logger.warning(f"Daily limit reached ({warmup_limit}). Try tomorrow.")
            return

        target = min(max_comments, remaining)
        logger.info(f"Target: {target} comments | Daily: {daily_count}/{warmup_limit} (warmup limit)")

        # Dry run without login — just show sample comments
        if dry_run and not self.is_logged_in:
            logger.info("Sample comments (each unique):")
            for i in range(target):
                comment = self.get_comment()
                logger.info(f"  #{i + 1}: {comment}")
            logger.info(f"Done. {target} sample comments generated.")
            return

        reels = self.fetch_trending_posts(count=target * 3)
        if not reels:
            logger.warning("No reels found.")
            return

        posted = 0
        for reel in reels:
            if posted >= target:
                break

            # Check cooldown (might have been triggered mid-session)
            if not dry_run and self._is_in_cooldown():
                logger.warning("Cooldown triggered mid-session. Stopping.")
                break

            media_id = self._get_media_id(reel)
            if media_id in self.commented_ids:
                logger.info(f"Skip {media_id} — already commented.")
                continue

            comment = self.get_comment(reel)

            if comment.upper().strip().startswith("NEGATIVE"):
                logger.info(f"Skip {media_id} — AI identified negative sentiment (tragedy/layoffs/outage).")
                continue

            if dry_run:
                user_obj = reel.get("user") or {}
                username = user_obj.get("username", "?") if isinstance(user_obj, dict) else "?"
                likes = reel.get("like_count", "?")
                caption_obj = reel.get("caption") or {}
                caption = ""
                if isinstance(caption_obj, dict):
                    caption = caption_obj.get("text", "")[:60]
                elif isinstance(caption_obj, str):
                    caption = caption_obj[:60]
                logger.info(f"  #{posted + 1} | @{username} | Likes: {likes}")
                logger.info(f"    Caption: {caption}...")
                logger.info(f"    Comment: {comment}")
                self.save_log(reel, comment, "dry_run")
                posted += 1
            else:
                # Safety #3: Simulate human behavior
                self._simulate_human_browse(reel)

                if self.comment_on_reel(reel, comment):
                    posted += 1
                    self._increment_daily_count()
                    self.save_log(reel, comment, "posted")
                else:
                    self.save_log(reel, comment, "failed")

            # Wait between comments (variable delay for human-like pattern)
            if posted < target:
                # Occasionally take a longer break (human behavior)
                if random.random() < 0.15:
                    delay = random.randint(max_delay, max_delay * 2)
                    logger.info(f"Taking a longer break... {delay}s")
                else:
                    delay = random.randint(min_delay, max_delay)
                    logger.info(f"Waiting {delay}s...")
                time.sleep(delay)

        logger.info(f"{'='*55}")
        logger.info(f"SESSION DONE — Posted: {posted}/{target} | Daily: {self._get_daily_count()}/{warmup_limit}")
        logger.info(f"{'='*55}")

    # ── Scheduled 3 sessions/day ───────────────────────────────────

    def run_scheduled(self, dry_run: bool = False):
        """
        Run 3 sessions per day: morning (9 AM), afternoon (2 PM), evening (8 PM).
        Keeps running forever — sleeps between sessions.
        """
        if not dry_run:
            if not self.is_logged_in and not self.login():
                return

        warmup_limit = self._get_warmup_limit()

        logger.info("=" * 55)
        logger.info("SCHEDULED MODE — 3 sessions per day")
        logger.info("  Morning:   9:00 AM  — 10 comments")
        logger.info("  Afternoon: 2:00 PM  — 10 comments")
        logger.info("  Evening:   8:00 PM  — 10 comments")
        logger.info(f"  Today's limit: {warmup_limit} comments (warm-up)")
        logger.info("=" * 55)

        while True:
            now = datetime.now()
            next_session = None
            next_name = None

            for name, config in SCHEDULE_SESSIONS.items():
                session_time = now.replace(
                    hour=config["hour"], minute=0, second=0, microsecond=0
                )
                if session_time > now:
                    if next_session is None or session_time < next_session:
                        next_session = session_time
                        next_name = name

            # If no session left today, schedule for tomorrow morning
            if next_session is None:
                tomorrow = now.replace(
                    hour=SCHEDULE_SESSIONS["morning"]["hour"],
                    minute=0, second=0, microsecond=0,
                )
                next_session = tomorrow + timedelta(days=1)
                next_name = "morning"

            # Add random offset (0-30 min) so timing isn't robotic
            random_offset = random.randint(0, 1800)
            wait_seconds = (next_session - now).total_seconds() + random_offset

            if wait_seconds > 60:
                wait_hours = wait_seconds / 3600
                logger.info(
                    f"Next session: {next_name} at ~{next_session.strftime('%I:%M %p')} "
                    f"(waiting {wait_hours:.1f} hours)"
                )
                time.sleep(wait_seconds)

            # Reload state for new day
            self.commented_ids = self._load_commented_ids()
            self.state = self._load_state()

            # Run the session (safety checks happen inside run())
            session_comments = SCHEDULE_SESSIONS[next_name]["comments"]
            logger.info(f"\n{'#'*55}")
            logger.info(f"STARTING {next_name.upper()} SESSION — {session_comments} comments")
            logger.info(f"{'#'*55}")

            self.run(
                max_comments=session_comments,
                min_delay=self.default_min_delay,
                max_delay=self.default_max_delay,
                dry_run=dry_run,
            )

            # Buffer after session
            time.sleep(60)


def main():
    parser = argparse.ArgumentParser(
        description="Maa Kaali Creations — Auto-comment on viral Indian reels"
    )
    parser.add_argument("--max-comments", type=int, default=10,
                        help="Comments per session (default: 10)")
    parser.add_argument("--min-delay", type=int, default=None,
                        help="Min delay in seconds (default: 180)")
    parser.add_argument("--max-delay", type=int, default=None,
                        help="Max delay in seconds (default: 300)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview comments without posting")
    parser.add_argument("--schedule", action="store_true",
                        help="Run 3 sessions/day: morning (9AM), afternoon (2PM), evening (8PM)")
    args = parser.parse_args()

    c = ReelAutoCommenter()
    min_delay = args.min_delay if args.min_delay is not None else c.default_min_delay
    max_delay = args.max_delay if args.max_delay is not None else c.default_max_delay

    if args.schedule:
        c.run_scheduled(dry_run=args.dry_run)
    else:
        c.run(
            max_comments=args.max_comments,
            min_delay=min_delay,
            max_delay=max_delay,
            dry_run=args.dry_run,
        )


if __name__ == "__main__":
    main()

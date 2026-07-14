import os
import sys
from pathlib import Path
from instagrapi import Client
from dotenv import load_dotenv

load_dotenv()

SESSION_FILE = Path(__file__).parent / "ig_session.json"

if not SESSION_FILE.exists():
    print("Error: ig_session.json not found. Run login_local.py first.")
    sys.exit(1)

cl = Client()
cl.set_locale("en_IN")
cl.set_timezone_offset(19800)
cl.set_device({
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
cl.set_user_agent(
    "Instagram 357.0.0.25.101 Android (34/14; 420dpi; 1080x2400; samsung; SM-A546B; a54x; exynos; en_IN; 408932556)"
)

print("Loading saved session settings...")
cl.load_settings(SESSION_FILE)

username = os.getenv("INSTAGRAM_USERNAME", "shubham.bhati_")
password = os.getenv("INSTAGRAM_PASSWORD", "")

print(f"Logging in as {username}...")
try:
    cl.login(username, password)
    print("Login successful.")
except Exception as e:
    print(f"Login failed: {e}")
    sys.exit(1)

print(f"Loaded session. User ID in client: {cl.user_id}")

print("\n--- Testing self user_info ---")
try:
    info = cl.user_info(cl.user_id)
    print(f"Success! Username: {info.username}, Full Name: {info.full_name}")
except Exception as e:
    print(f"user_info failed: {e}")

print("\n--- Testing hashtag_medias_top('systemdesign') ---")
try:
    medias = cl.hashtag_medias_top("systemdesign", amount=3)
    print(f"Success! Retrieved {len(medias)} posts.")
except Exception as e:
    print(f"hashtag_medias_top failed: {e}")



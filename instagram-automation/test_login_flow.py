import os
import sys
from pathlib import Path
from instagrapi import Client
from dotenv import load_dotenv

load_dotenv()

username = os.getenv("INSTAGRAM_USERNAME", "")
password = os.getenv("INSTAGRAM_PASSWORD", "")

if not username or not password:
    print("Error: Username or password missing in .env")
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

print(f"Attempting login as {username}...")
try:
    success = cl.login(username, password)
    print(f"cl.login returned: {success}")
except Exception as e:
    print(f"cl.login threw exception: {type(e).__name__}: {e}")
    sys.exit(1)

print("\n--- Dumping client cookies ---")
cookies = cl.private.cookies.get_dict()
for key, value in cookies.items():
    # Mask sessionid for safety
    display_value = value if key != "sessionid" else f"{value[:10]}...{value[-10:]}" if len(value) > 20 else value
    print(f"Cookie: {key} = {display_value}")

print("\n--- Verifying session with user_info ---")
try:
    info = cl.user_info(cl.user_id)
    print(f"Success! Username: {info.username}, User ID: {cl.user_id}")
except Exception as e:
    print(f"user_info failed: {type(e).__name__}: {e}")
    if hasattr(cl, 'last_response') and cl.last_response:
        print(f"Last response status: {cl.last_response.status_code}")
        print(f"Last response headers: {cl.last_response.headers}")
        print(f"Last response text: {cl.last_response.text[:500]}")

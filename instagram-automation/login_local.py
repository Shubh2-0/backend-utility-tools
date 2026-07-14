"""
Login to Instagram from your local PC and save the session.
Run this whenever your session expires (every ~30 days).

This creates ig_session.json which gets uploaded to GitHub.
Your home IP is trusted by Instagram, so login always works here.

Usage:
    python login_local.py              # login and save session
    python login_local.py --upload     # login, save, and upload to GitHub
"""

import argparse
import base64
import json
import os
import subprocess
import sys
from pathlib import Path

import pyotp
from dotenv import load_dotenv
from instagrapi import Client

load_dotenv()

SESSION_FILE = Path(__file__).parent / "ig_session.json"
STATE_FILE = Path(__file__).parent / "bot_state.json"


def login_and_save():
    username = os.getenv("INSTAGRAM_USERNAME", "")
    password = os.getenv("INSTAGRAM_PASSWORD", "")
    totp_key = os.getenv("INSTAGRAM_TOTP_KEY", "")
    session_id = os.getenv("INSTAGRAM_SESSIONID", "")

    if not username:
        print("ERROR: Set INSTAGRAM_USERNAME in .env")
        sys.exit(1)

    client = Client()
    client.set_locale("en_IN")
    client.set_timezone_offset(19800)
    client.delay_range = [1, 3]
    client.set_device({
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
    client.set_user_agent(
        "Instagram 357.0.0.25.101 Android (34/14; 420dpi; 1080x2400; samsung; SM-A546B; a54x; exynos; en_IN; 408932556)"
    )

    import time
    time.sleep(3)

    print(f"Logging in as {username}...")

    try:
        # Step 0: Attempt login using INSTAGRAM_SESSIONID if provided
        logged_in_with_session = False
        if session_id:
            from urllib.parse import unquote
            decoded_session_id = unquote(session_id.strip())
            print("Found INSTAGRAM_SESSIONID in .env. Attempting login using Session ID...")
            try:
                client.login_by_sessionid(decoded_session_id)
                # Verify session works
                client.get_timeline_feed()
                print("Login successful using Session ID!")
                logged_in_with_session = True
            except Exception as se:
                print(f"Session ID login failed: {se}")
                client.set_settings({})
                print("Falling back to password login...")

        if not logged_in_with_session:
            if not password:
                print("ERROR: Set INSTAGRAM_PASSWORD in .env for password login")
                sys.exit(1)

            # Step 1: Attempt normal login
            try:
                client.login(username, password)
                print("Login successful!")
            except Exception as e:
                err_str = str(e).lower()
                is_blacklist_or_facebook = "blacklist" in err_str or "facebook" in err_str or "change your ip" in err_str or "checkpoint" in err_str
                is_2fa = "two-factor" in err_str or "two_factor" in err_str or "verification_code" in err_str or "challenge" in err_str or "twofactorrequired" in err_str
                
                if is_2fa:
                    print("\n[2FA Required] Two-Factor Authentication is active on your account.")
                    
                    if totp_key:
                        clean_key = totp_key.replace(" ", "").replace("-", "").upper()
                        totp = pyotp.TOTP(clean_key)
                        fresh_code = totp.now()
                        print(f"Generated 2FA code from TOTP Key: {fresh_code}")
                    else:
                        # Prompt user directly in terminal to enter the code from Google Authenticator
                        print("Please open the Google Authenticator app on your phone.")
                        fresh_code = input("Enter the 6-digit 2FA code for Instagram: ").strip()
                    
                    print(f"Submitting 2FA code: {fresh_code}...")
                    client.login(username, password, verification_code=fresh_code)
                    print("Login successful with 2FA!")
                elif is_blacklist_or_facebook:
                    print("\n[Instagram Firewall Block] Instagram has blocked password logins from this IP/device.")
                    print("You can bypass this firewall by using your browser's Instagram session cookie.")
                    print("\nInstructions to get your Session ID:")
                    print("1. Log in to Instagram on your web browser (Chrome, Edge, Firefox, Safari).")
                    print("2. Open Developer Tools (Press F12, or Right-Click -> Inspect).")
                    print("3. Go to 'Application' (Chrome/Edge) or 'Storage' (Firefox) tab.")
                    print("4. Expand 'Cookies' in the left sidebar and click 'https://www.instagram.com'.")
                    print("5. Find the row with Name 'sessionid' and copy its Value.")
                    print("6. Paste it into INSTAGRAM_SESSIONID in your .env file to save it.")
                    
                    user_cookie = input("\nEnter your Instagram 'sessionid' cookie value: ").strip()
                    if not user_cookie:
                        raise Exception("No Session ID provided. Cannot bypass firewall.")
                    
                    from urllib.parse import unquote
                    decoded_cookie = unquote(user_cookie.strip())
                    print("\nAttempting login using provided Session ID...")
                    client.login_by_sessionid(decoded_cookie)
                    # Verify
                    client.get_timeline_feed()
                    print("Login successful using Session ID!")
                else:
                    raise e

        print("Login complete!")

        # Verify session works
        try:
            client.get_timeline_feed()
            print("Session verified — feed loaded.")
        except Exception as ve:
            print(f"Warning: Session verification (feed load) failed: {ve}")
            print("Proceeding to save the session settings anyway since authentication completed.")

        # Save session
        client.dump_settings(SESSION_FILE)
        print(f"Session saved to: {SESSION_FILE}")

        # Initialize bot state if not exists
        if not STATE_FILE.exists():
            from datetime import date
            state = {"first_run_date": date.today().isoformat()}
            with open(STATE_FILE, "w") as f:
                json.dump(state, f, indent=2)
            print("Bot state initialized.")

        return True

    except Exception as e:
        print(f"Login failed: {e}")
        return False



def upload_session_to_github():
    """Upload session as base64 encoded GitHub secret."""
    if not SESSION_FILE.exists():
        print("ERROR: No session file found. Run login first.")
        return False

    print("\nUploading session to GitHub...")

    with open(SESSION_FILE, "r") as f:
        session_data = f.read()

    # Base64 encode the session
    encoded = base64.b64encode(session_data.encode()).decode()

    try:
        # Set as GitHub secret
        result = subprocess.run(
            ["gh", "secret", "set", "IG_SESSION_DATA", "--body", encoded],
            capture_output=True, text=True, cwd=str(Path(__file__).parent)
        )

        if result.returncode == 0:
            print("Session uploaded to GitHub secret: IG_SESSION_DATA")
            print("GitHub Actions will now use your saved session!")
            return True
        else:
            print(f"Upload failed: {result.stderr}")
            return False

    except FileNotFoundError:
        print("ERROR: 'gh' CLI not found. Install GitHub CLI first.")
        return False


def main():
    parser = argparse.ArgumentParser(description="Login to Instagram locally and save session")
    parser.add_argument("--upload", action="store_true",
                        help="Upload session to GitHub after login")
    args = parser.parse_args()

    success = login_and_save()
    if success and args.upload:
        upload_session_to_github()
    elif success:
        print("\nTo upload session to GitHub, run:")
        print("  python login_local.py --upload")


if __name__ == "__main__":
    main()

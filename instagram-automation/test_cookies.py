import sys
from instagrapi import Client

raw_cookie = "72191183896%3AST3opphv77lh1Z%3A23%3AAYi1OhaNPPGvnfY5QDM2WzK1caq11bTli5lBWpWZaA"
decoded_cookie = "72191183896:ST3opphv77lh1Z:23:AYi1OhaNPPGvnfY5QDM2WzK1caq11bTli5lBWpWZaA"

cl1 = Client()
cl1.set_locale("en_IN")
cl1.set_timezone_offset(19800)

print("--- Test 1: Trying with RAW URL-encoded cookie (%3A) ---")
try:
    cl1.login_by_sessionid(raw_cookie)
    print("Success! Logged in with raw cookie.")
    # Try an API call
    info = cl1.user_info(cl1.user_id)
    print(f"Verified! User: {info.username}")
except Exception as e:
    print(f"Failed with raw cookie: {e}")

cl2 = Client()
cl2.set_locale("en_IN")
cl2.set_timezone_offset(19800)

print("\n--- Test 2: Trying with DECODED cookie (:) ---")
try:
    cl2.login_by_sessionid(decoded_cookie)
    print("Success! Logged in with decoded cookie.")
    # Try an API call
    info = cl2.user_info(cl2.user_id)
    print(f"Verified! User: {info.username}")
except Exception as e:
    print(f"Failed with decoded cookie: {e}")

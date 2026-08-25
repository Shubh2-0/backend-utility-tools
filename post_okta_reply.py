import subprocess
import json
import time

token = subprocess.check_output('gh auth token --user Shubh2-0', shell=True).decode().strip()

comment_text = """Hey @A-N-O-D-E-R, thanks for tagging me!

Checking `OktaOAuth2Configurer` around line 116 — checking `authenticationManagerResolver != null` before fallback opaque token validation is a solid approach. When `AuthenticationManagerResolver` is present, Spring Security delegates token verification dynamically across OIDC issuers, so skipping default opaque token config avoids overriding multi-issuer resolvers.

I'll review PR #934 and test it against a multi-tenant OIDC setup to make sure there are no side effects on existing JWT flows."""

url = "https://api.github.com/repos/okta/okta-spring-boot/issues/933/comments"
payload = json.dumps({"body": comment_text})

for attempt in range(5):
    try:
        cmd = f'curl.exe -s -X POST -H "Authorization: Bearer {token}" -H "Content-Type: application/json" -H "Accept: application/vnd.github+json" "{url}" -d {json.dumps(payload)}'
        res = subprocess.check_output(cmd, shell=True).decode()
        if "html_url" in res:
            print("[SUCCESS] Comment Posted on okta/okta-spring-boot#933!")
            data = json.loads(res)
            print("Comment URL:", data.get("html_url"))
            break
        else:
            print(f"Attempt {attempt+1} response:", res[:200])
    except Exception as e:
        print(f"Attempt {attempt+1} error: {e}")
    time.sleep(3)

import subprocess
import json
import time

token = subprocess.check_output('gh auth token --user Shubh2-0', shell=True).decode().strip()

comment_text = """Makes sense @rstoyanchev. Unwrapping `HttpMessageNotWritableException` and checking if its underlying cause matches `DisconnectedClientHelper.isClientDisconnectedException(...)` before logging will keep `DefaultHandlerExceptionResolver` clean without swallowing actual serialization errors.

I'd be glad to take this up and submit a PR if it's open for contributions."""

url = "https://api.github.com/repos/spring-projects/spring-framework/issues/37151/comments"
payload = json.dumps({"body": comment_text})

for attempt in range(3):
    try:
        cmd = f'curl.exe -s -X POST -H "Authorization: Bearer {token}" -H "Content-Type: application/json" -H "Accept: application/vnd.github+json" "{url}" -d {json.dumps(payload)}'
        res = subprocess.check_output(cmd, shell=True).decode()
        if "html_url" in res:
            print("[SUCCESS] Comment Posted on spring-projects/spring-framework#37151!")
            data = json.loads(res)
            print("Comment URL:", data.get("html_url"))
            break
        else:
            print(f"Attempt {attempt+1} response:", res[:200])
    except Exception as e:
        print(f"Attempt {attempt+1} error: {e}")
    time.sleep(2)

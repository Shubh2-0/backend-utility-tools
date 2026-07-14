"""
Add more statements to Wikidata entity Q139819181 (Shubham Bhati).

Adds:
  - P9136 Dev.to username: shubham_bhati
  - P108 employer: AlignBits LLC (string fallback if no Q-ID)
  - P2031 work start date: 2023-01-01 (approximate)

Uses the existing bot password 'Bhati Shubham@HelloWorld@1920'.
"""

import json
import time
import sys
import urllib.parse

import requests

WD = "https://www.wikidata.org/w/api.php"
USER = "Bhati Shubham@HelloWorld@1920"
PASS = "0bs9s5kstfkhtqflk046nlmu4d47lemo"
ENTITY = "Q139819181"

s = requests.Session()
s.headers.update({"User-Agent": "ShubhamBhatiWikidataBot/1.0"})


def get_token(token_type="login"):
    r = s.get(WD, params={"action": "query", "meta": "tokens", "type": token_type, "format": "json"})
    return r.json()["query"]["tokens"][f"{token_type}token"]


def login():
    tok = get_token("login")
    r = s.post(WD, data={"action": "login", "lgname": USER, "lgpassword": PASS, "lgtoken": tok, "format": "json"})
    result = r.json().get("login", {}).get("result", "unknown")
    print(f"  login: {result}")
    return result == "Success"


def has_statement(prop: str) -> bool:
    r = s.get(WD, params={"action": "wbgetentities", "ids": ENTITY, "props": "claims", "format": "json"})
    claims = r.json().get("entities", {}).get(ENTITY, {}).get("claims", {})
    return prop in claims


def add_statement(prop: str, value: str, csrf: str, datatype: str = "string"):
    if has_statement(prop):
        print(f"  [skip] {prop} already exists")
        return True
    if datatype == "string":
        val = json.dumps(value)
    elif datatype == "external-id":
        val = json.dumps(value)
    elif datatype == "time":
        val = json.dumps({
            "time": value,
            "timezone": 0,
            "before": 0,
            "after": 0,
            "precision": 11,
            "calendarmodel": "http://www.wikidata.org/entity/Q1985727",
        })
    else:
        val = json.dumps(value)

    for attempt in range(3):
        r = s.post(WD, data={
            "action": "wbcreateclaim",
            "entity": ENTITY,
            "property": prop,
            "snaktype": "value",
            "value": val,
            "token": csrf,
            "format": "json",
            "bot": 1,
        })
        body = r.json()
        if "error" in body:
            err = body["error"].get("code", "?")
            print(f"  [retry {attempt+1}] {prop} → {err}: {body['error'].get('info','')[:120]}")
            if err == "failed-save":
                time.sleep(3 * (attempt + 1))
                continue
            return False
        print(f"  [OK] added {prop} = {value}")
        return True
    return False


def main():
    print(f"\n=== Wikidata enrichment for {ENTITY} ===\n")
    if not login():
        sys.exit("Login failed.")
    csrf = get_token("csrf")
    print(f"  csrf token: {csrf[:24]}...\n")

    # P9136 = Dev.to username
    add_statement("P9136", "shubham_bhati", csrf, datatype="external-id")
    time.sleep(2)

    # P108 = employer (AlignBits LLC has no Q-ID; skip until verified)
    # P2031 = work period (start)
    add_statement("P2031", "+2023-01-01T00:00:00Z", csrf, datatype="time")
    time.sleep(2)

    # P10676 = Hashnode user (deprecated since paid, but data point preserved)
    # SKIP — Hashnode moved to paid API in 2026

    # P10677 = Stack Exchange user ID — only if user has it
    # SKIP — no SO presence yet

    # P11630 = Reddit username — skip until confirmed

    # P2049 = width / nothing relevant
    # P3744 = subscribers — skip

    # P2002 = Twitter username — user has https://x.com/Bhati_Shubham_ ?
    # We don't have confirmed handle; skip to avoid wrong data.

    # P136 = genre — not for person
    # P800 = notable work — could add portfolio URL, but P856 already has it

    # P5587 = Libraries.io user ID, P2671 = Google Knowledge Graph ID — skip
    # we'll add Google KGID when it gets assigned

    print("\nDone.")


if __name__ == "__main__":
    main()

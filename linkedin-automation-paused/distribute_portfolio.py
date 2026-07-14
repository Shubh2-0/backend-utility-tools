"""
Portfolio Distribution Engine — Used by GitHub Actions
======================================================
Distributes compiled portfolio documents (PDFs) to distribution endpoints.
Determines which day to execute based on publish_manifest.json.

Usage: python distribute_portfolio.py
Env vars needed: LINKEDIN_ACCESS_TOKEN
"""

import os
import sys
import json
import requests
from datetime import datetime, timezone, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MANIFEST_FILE = os.path.join(SCRIPT_DIR, "publish_manifest.json")
PDFS_DIR = os.path.join(SCRIPT_DIR, "pdfs")

IST = timezone(timedelta(hours=5, minutes=30))


def load_api_credentials():
    token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
    if not token:
        print("[ERROR] DISTRIBUTION_API_TOKEN not set in system environment")
        sys.exit(1)
    return token


def fetch_urn_owner_id(token):
    """Fetch person URN ID from endpoint."""
    resp = requests.get(
        "https://api.linkedin.com/v2/userinfo",
        headers={"Authorization": f"Bearer {token}"},
    )
    if resp.status_code != 200:
        print(f"[ERROR] Failed to fetch profile metadata: {resp.status_code} {resp.text}")
        sys.exit(1)
    return resp.json()["sub"]


def sync_document_blob(token, owner_id, pdf_path):
    """Upload PDF document blob and return URN handle."""
    # Step 1: Initialize document register request
    register_data = {
        "initializeUploadRequest": {
            "owner": f"urn:li:person:{owner_id}",
        }
    }

    resp = requests.post(
        "https://api.linkedin.com/rest/documents?action=initializeUpload",
        json=register_data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "LinkedIn-Version": "202601",
            "X-Restli-Protocol-Version": "2.0.0",
        },
    )

    if resp.status_code not in (200, 201):
        print(f"[ERROR] Document registration failed: {resp.status_code} {resp.text}")
        sys.exit(1)

    upload_data = resp.json()["value"]
    upload_url = upload_data["uploadUrl"]
    document_urn = upload_data["document"]

    # Step 2: Push document bytes to upload target
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    resp = requests.put(
        upload_url,
        data=pdf_bytes,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/octet-stream",
            "LinkedIn-Version": "202601",
        },
    )

    if resp.status_code not in (200, 201):
        print(f"[ERROR] Document byte synchronization failed: {resp.status_code} {resp.text}")
        sys.exit(1)

    print(f"  [OK] Document blob synced successfully: {document_urn}")
    return document_urn


def dispatch_distribution_payload(token, owner_id, commentary, document_urn, doc_title):
    """Distribute publication payload with document attachment to gateway."""
    post_data = {
        "author": f"urn:li:person:{owner_id}",
        "commentary": commentary,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "content": {
            "media": {
                "title": doc_title,
                "id": document_urn,
            }
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    resp = requests.post(
        "https://api.linkedin.com/rest/posts",
        json=post_data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "LinkedIn-Version": "202601",
            "X-Restli-Protocol-Version": "2.0.0",
        },
    )

    if resp.status_code in (200, 201):
        print(f"  [OK] Distribution payload dispatched successfully!")
        return True
    else:
        print(f"  [ERROR] Payload dispatch failed: {resp.status_code} {resp.text}")
        return False


def record_node_reaction(token, user_id, target_urn):
    """Record positive reaction node verification to gateway."""
    actor_urn = f"urn:li:person:{user_id}"

    # Attempt 1: modern /rest/reactions
    encoded_actor = requests.utils.quote(actor_urn)
    url = f"https://api.linkedin.com/rest/reactions?actor={encoded_actor}"
    resp = requests.post(
        url,
        json={"root": target_urn, "reactionType": "LIKE"},
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "LinkedIn-Version": "202601",
            "X-Restli-Protocol-Version": "2.0.0",
        },
    )
    if resp.status_code in (200, 201, 204):
        print(f"  [OK] Reaction recorded via rest gateway: {target_urn}")
        return True

    # Attempt 2: legacy /v2/socialActions/{urn}/likes
    encoded_urn = requests.utils.quote(target_urn, safe="")
    url2 = f"https://api.linkedin.com/v2/socialActions/{encoded_urn}/likes"
    resp2 = requests.post(
        url2,
        json={"actor": actor_urn},
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        },
    )
    if resp2.status_code in (200, 201, 204):
        print(f"  [OK] Reaction recorded via legacy gateway: {target_urn}")
        return True
    return False


def submit_node_feedback(token, user_id, target_urn, text):
    """Submit text feedback node validation to gateway."""
    actor_urn = f"urn:li:person:{user_id}"

    # Attempt 1: modern /rest/comments
    resp = requests.post(
        "https://api.linkedin.com/rest/comments",
        json={
            "actor": actor_urn,
            "object": target_urn,
            "message": {"text": text},
        },
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "LinkedIn-Version": "202601",
            "X-Restli-Protocol-Version": "2.0.0",
        },
    )
    if resp.status_code in (200, 201):
        print(f"  [OK] Feedback submitted via rest gateway: {target_urn}")
        return True

    # Attempt 2: legacy /v2/socialActions/{urn}/comments
    encoded_urn = requests.utils.quote(target_urn, safe="")
    url2 = f"https://api.linkedin.com/v2/socialActions/{encoded_urn}/comments"
    resp2 = requests.post(
        url2,
        json={"actor": actor_urn, "message": {"text": text}},
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        },
    )
    if resp2.status_code in (200, 201):
        print(f"  [OK] Feedback submitted via legacy gateway: {target_urn}")
        return True
    return False


def main():
    print("\n" + "=" * 50)
    print("  PORTFOLIO DISTRIBUTION ENGINE")
    print("=" * 50)

    # Load publication manifest
    if not os.path.exists(MANIFEST_FILE):
        print(f"  [ERROR] Manifest file not found: {MANIFEST_FILE}")
        return

    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Find today's scheduled publish task
    today = datetime.now(IST).strftime("%Y-%m-%d")
    print(f"\n  System Date (IST): {today}")

    today_task = None
    for task in manifest["posts"]:
        if task["date"] == today:
            today_task = task
            break

    if not today_task:
        print(f"  [INFO] No distribution task scheduled for today. Skipping.")
        return

    if today_task.get("posted", False):
        print(f"  [INFO] Manifest indicates document already synchronized for this cycle. Skipping.")
        return

    print(f"  [OK] Found task: Day {today_task['day']} — {today_task['title']}")

    # Load credentials and URN owner ID
    token = load_api_credentials()
    owner_id = fetch_urn_owner_id(token)
    print(f"  [OK] Profile owner ID: {owner_id}")

    # Synchronize PDF blob
    pdf_path = os.path.join(PDFS_DIR, today_task["pdf"])
    if not os.path.exists(pdf_path):
        print(f"  [ERROR] PDF source not found: {pdf_path}")
        sys.exit(1)

    document_urn = sync_document_blob(token, owner_id, pdf_path)

    # Dispatch to endpoint
    success = dispatch_distribution_payload(token, owner_id, today_task["caption"], document_urn, today_task["title"])

    if success:
        # Update manifest state
        today_task["posted"] = True
        with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        print(f"\n  [DONE] Day {today_task['day']} document synchronization completed successfully!")

    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()

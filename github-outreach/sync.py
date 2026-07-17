import time
import random
import os
import json
import requests
from datetime import datetime, timedelta

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

TOKEN = os.environ["GH_TOKEN"]
MAX_SYNC = int(os.environ.get("MAX_FOLLOW", 20))  # Max connection nodes to sync per run (safe & fast: 20 per run)
DATA_FILE = "sync_cache.json"
MAX_PAGES_SCAN = 5
MAX_EXECUTION_SECONDS = 300

# Target user profiles to sync connection graphs from
TARGET_USERS = [
    "mirainiki",
    "JohnMwendwa",
    "A-Hemeda",
    "seehiong",
    "otosmane",
    "NazmusSayad",
    "kynaderd",
    "aibers",
    "Martin322s",
    "BlingLynnVaultz",
    "onerauv"
]

API_BASE = "https://api.github.com"
ROUTE_USERS = "users"
ROUTE_USER = "user"
ROUTE_FOLLOWING = "user/following"
ROUTE_FOLLOWERS = "user/followers"
ROUTE_STARRED = "user/starred"

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}


def github_request(method, url, json_data=None):
    """Make requests to GitHub API with automatic rate-limit and secondary limit handling"""
    for attempt in range(3):
        try:
            if method.upper() == "GET":
                resp = requests.get(url, headers=headers, timeout=15)
            elif method.upper() == "PUT":
                resp = requests.put(url, headers=headers, json=json_data, timeout=15)
            elif method.upper() == "DELETE":
                resp = requests.delete(url, headers=headers, timeout=15)
            else:
                return None
            
            # Handle rate limiting / abuse detection
            if resp.status_code == 403 or resp.status_code == 429:
                reset_time = resp.headers.get("X-RateLimit-Reset")
                retry_after = resp.headers.get("Retry-After")
                
                if retry_after:
                    wait_time = int(retry_after) + 5
                elif reset_time:
                    wait_time = max(int(float(reset_time) - time.time()) + 5, 30)
                else:
                    wait_time = 60 * (attempt + 1)
                
                print(f"  [Rate Limit / Abuse Protection] Blocked. Sleeping for {wait_time}s...")
                time.sleep(wait_time)
                continue
                
            return resp
        except Exception as e:
            print(f"  [API Error] Request failed on attempt {attempt+1}: {e}")
            time.sleep(5)
    return None


def get_authenticated_username():
    """Dynamically fetch the authenticated user's login to prevent self-following"""
    url = f"{API_BASE}/{ROUTE_USER}"
    resp = github_request("GET", url)
    if resp and resp.status_code == 200:
        return resp.json().get("login")
    return "Shubh2-0"  # Safe default


def load_sync_cache():
    # Handle backward compatibility migration if followed_users.json exists
    old_file = "followed_users.json"
    if os.path.exists(old_file) and not os.path.exists(DATA_FILE):
        try:
            print("Migrating legacy connection logs to sync cache...")
            os.rename(old_file, DATA_FILE)
        except Exception as e:
            print(f"Migration error: {e}")

    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    if "followed_users" not in data:
                        data["followed_users"] = []
                    if "history" not in data:
                        data["history"] = []
                    return data
        except Exception as e:
            print(f"Error reading cache: {e}")
    return {"followed_users": [], "history": []}


def migrate_old_data(data):
    """Migrate from old week1/week2 schema to flat followed_users list if needed"""
    if "followed_users" not in data:
        print("Migrating old cache structure to flat list...")
        flat_list = []
        now = datetime.utcnow()
        
        def parse_date(date_str):
            try:
                return datetime.strptime(date_str.split(".")[0], "%Y-%m-%dT%H:%M:%S").isoformat()
            except Exception:
                return now.isoformat()

        if "week1" in data:
            for entry in data["week1"]:
                if isinstance(entry, dict) and "username" in entry:
                    flat_list.append({
                        "username": entry["username"],
                        "followed_on": parse_date(entry.get("followed_on") or (now - timedelta(days=7)).isoformat()),
                        "followed_back": False
                    })
                elif isinstance(entry, str):
                    flat_list.append({
                        "username": entry,
                        "followed_on": (now - timedelta(days=7)).isoformat(),
                        "followed_back": False
                    })
                    
        if "week2" in data:
            for entry in data["week2"]:
                if isinstance(entry, dict) and "username" in entry:
                    flat_list.append({
                        "username": entry["username"],
                        "followed_on": parse_date(entry.get("followed_on") or now.isoformat()),
                        "followed_back": False
                    })
                elif isinstance(entry, str):
                    flat_list.append({
                        "username": entry,
                        "followed_on": now.isoformat(),
                        "followed_back": False
                    })
                    
        data = {"followed_users": flat_list, "history": []}
        save_sync_cache(data)
    return data


def save_sync_cache(data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving tracking cache: {e}")


def get_tracked_connections(data):
    """All nodes we are tracking in active sync cycle"""
    nodes_set = set()
    if "followed_users" in data:
        for u in data["followed_users"]:
            if isinstance(u, dict) and "username" in u:
                nodes_set.add(u["username"])
    return nodes_set


def fetch_account_connections():
    """Fetch lists of inbound and outbound graph nodes directly from GitHub API"""
    inbound = set()
    outbound = set()
    
    # 1. Get inbound nodes (followers)
    page = 1
    while True:
        url = f"{API_BASE}/{ROUTE_FOLLOWERS}?per_page=100&page={page}"
        resp = github_request("GET", url)
        if not resp or resp.status_code != 200:
            break
        users = resp.json()
        if not users:
            break
        for u in users:
            inbound.add(u["login"])
        page += 1
        
    # 2. Get outbound nodes (following)
    page = 1
    while True:
        url = f"{API_BASE}/{ROUTE_FOLLOWING}?per_page=100&page={page}"
        resp = github_request("GET", url)
        if not resp or resp.status_code != 200:
            break
        users = resp.json()
        if not users:
            break
        for u in users:
            outbound.add(u["login"])
        page += 1
        
    return inbound, outbound


def validate_node_profile(username):
    """Verify if target user is active and likely to follow back"""
    url = f"{API_BASE}/{ROUTE_USERS}/{username}"
    resp = github_request("GET", url)
    if not resp or resp.status_code != 200:
        return False
    try:
        profile = resp.json()
        
        # Filter 1: Must have at least 1 public repo (ensures they are developers, not fake spam accounts)
        public_repos = profile.get("public_repos", 0)
        if public_repos < 1:
            print(f"  [Skip] {username} has 0 public repositories.")
            return False
            
        # Filter 2: Must be following at least 5 people (proves they follow others / follow back)
        following = profile.get("following", 0)
        if following < 5:
            print(f"  [Skip] {username} is following only {following} users (low follow-back probability).")
            return False
            
        # Filter 3: No Organizations
        if profile.get("type") == "Organization":
            return False
            
        return True
    except Exception as e:
        print(f"  [Validation Error] for {username}: {e}")
        return False


def ping_node_handshake(username):
    """Star a repo of the target node to ping for connection verification"""
    url = f"{API_BASE}/{ROUTE_USERS}/{username}/repos?per_page=5&sort=updated"
    try:
        resp = github_request("GET", url)
        if not resp or resp.status_code != 200:
            return
        repos = resp.json()
        if not repos:
            return
        # Find a non-fork repo
        target_repo = None
        for r in repos:
            if not r.get("fork"):
                target_repo = r.get("name")
                break
        if not target_repo:
            target_repo = repos[0].get("name")
            
        star_url = f"{API_BASE}/{ROUTE_STARRED}/{username}/{target_repo}"
        r = github_request("PUT", star_url)
        if r and r.status_code == 204:
            print(f"  [Handshake] Pinged connection verification with node: {username}/{target_repo}")
    except Exception as e:
        print(f"  [Handshake Error] failed to ping node {username}: {e}")


def synchronize_network_nodes():
    """Follow active users from a randomly selected target developer's followers list"""
    raw_data = load_sync_cache()
    data = migrate_old_data(raw_data)
    
    if "history" not in data:
        data["history"] = []
    
    tracked_nodes = get_tracked_connections(data)
    history_set = set(data["history"])
    
    my_username = get_authenticated_username()
    print(f"Initiating graph synchronization process as {my_username}...")
    
    inbound_nodes, outbound_nodes = fetch_account_connections()
    
    priority_target = os.environ.get("PRIORITY_TARGET")
    if priority_target and priority_target in TARGET_USERS:
        target_node = priority_target
        print(f"Priority target active: {target_node}")
    else:
        target_node = random.choice(TARGET_USERS)
        print(f"Target node source selected: {target_node}")
        
    print(f"Active cache size: {len(tracked_nodes)} nodes")
    print(f"Inbound connections: {len(inbound_nodes)} nodes")
    print(f"Outbound connections: {len(outbound_nodes)} nodes")

    page = 1
    synced = 0
    consecutive_empty_pages = 0
    
    # Introduce human-like randomization of target count
    target_count = random.randint(int(MAX_SYNC * 0.8), int(MAX_SYNC * 1.1))
    print(f"Determined safety cap for this cycle: {target_count} follows.")

    start_time = time.time()
    while synced < target_count and consecutive_empty_pages < 3 and page <= MAX_PAGES_SCAN:
        if time.time() - start_time > MAX_EXECUTION_SECONDS:
            print(f"  [Timeout Guard] Maximum execution time ({MAX_EXECUTION_SECONDS}s) reached. Saving state and exiting cycle.")
            break

        url = f"{API_BASE}/{ROUTE_USERS}/{target_node}/followers?per_page=50&page={page}"
        resp = github_request("GET", url)

        if not resp or resp.status_code != 200:
            print(f"Error reading nodes from {target_node}")
            break

        users = resp.json()

        if not users:
            consecutive_empty_pages += 1
            page += 1
            continue
        
        consecutive_empty_pages = 0

        for user in users:
            if synced >= target_count:
                break

            if isinstance(user, dict) and "login" in user:
                username = user["login"]
            else:
                continue

            # Self-follow protection
            if username.lower() == my_username.lower():
                continue

            # Skip if already tracked or in historical blacklist
            if username in tracked_nodes or username in history_set:
                continue

            # Skip if outbound connection already exists
            if username in outbound_nodes:
                if "followed_users" not in data:
                    data["followed_users"] = []
                data["followed_users"].append({
                    "username": username,
                    "followed_on": datetime.utcnow().isoformat(),
                    "followed_back": True
                })
                if username not in data["history"]:
                    data["history"].append(username)
                save_sync_cache(data)
                tracked_nodes.add(username)
                history_set.add(username)
                continue

            # Skip if node is already inbound
            if username in inbound_nodes:
                continue

            print(f"Checking node status: {username}...")
            if not validate_node_profile(username):
                # Add to history to avoid checking this inactive node ever again
                if username not in data["history"]:
                    data["history"].append(username)
                    save_sync_cache(data)
                    history_set.add(username)
                continue

            # Establish connection (PUT request)
            connect_url = f"{API_BASE}/{ROUTE_FOLLOWING}/{username}"
            r = github_request("PUT", connect_url)

            if r and r.status_code == 204:
                synced += 1
                if "followed_users" not in data:
                    data["followed_users"] = []
                data["followed_users"].append({
                    "username": username,
                    "followed_on": datetime.utcnow().isoformat(),
                    "followed_back": False
                })
                if username not in data["history"]:
                    data["history"].append(username)
                save_sync_cache(data)
                tracked_nodes.add(username)
                history_set.add(username)
                print(f"Established connection node ({synced}/{target_count}): {username}")
                ping_node_handshake(username)
            elif r and r.status_code == 304:
                print(f"Node already linked (304): {username}")
                tracked_nodes.add(username)
                if username not in data["history"]:
                    data["history"].append(username)
                    save_sync_cache(data)
                    history_set.add(username)
            else:
                print(f"Failed to sync node {username}")

            # Sleep to prevent high load / rate limit
            wait = random.randint(12, 25)
            print(f"  Throttling: waiting {wait}s...")
            time.sleep(wait)

        page += 1

    print(f"Completed sync cycle. Added {synced} connection nodes today.")


def prune_stale_cache():
    """Evaluate and prune stale connection nodes from local cache"""
    raw_data = load_sync_cache()
    data = migrate_old_data(raw_data)
    
    if "history" not in data:
        data["history"] = []

    if "followed_users" not in data or not data["followed_users"]:
        print("No connections active in cache.")
        return

    print(f"Evaluating {len(data['followed_users'])} cache nodes for pruning...")

    inbound_nodes, _ = fetch_account_connections()

    pruned_count = 0
    remaining_nodes = []
    now = datetime.utcnow()

    for entry in data["followed_users"]:
        username = entry["username"]
        followed_on_str = entry["followed_on"]

        try:
            followed_on = datetime.strptime(followed_on_str.split(".")[0], "%Y-%m-%dT%H:%M:%S")
        except Exception:
            followed_on = now

        is_linked = username in inbound_nodes
        days_in_cache = (now - followed_on).days

        should_prune = False
        reason = ""
        if is_linked:
            # Protect mutual connections from being unfollowed
            pass
        else:
            # Prune unlinked connections after 14 days
            if days_in_cache >= 14:
                should_prune = True
                reason = "Unlinked node - cache duration expired (14d)"

        if should_prune:
            disconnect_url = f"{API_BASE}/{ROUTE_FOLLOWING}/{username}"
            r = github_request("DELETE", disconnect_url)

            if r and r.status_code == 204:
                pruned_count += 1
                print(f"Pruned node: {username} ({reason}, lifetime: {days_in_cache}d)")
            else:
                print(f"Failed to disconnect node {username}")
                remaining_nodes.append(entry)

            # Wait during pruning to respect rate limits
            wait = random.randint(3, 10)
            time.sleep(wait)
        else:
            if is_linked:
                entry["followed_back"] = True
            remaining_nodes.append(entry)

    data["followed_users"] = remaining_nodes
    save_sync_cache(data)
    print(f"Cache pruning done. Removed {pruned_count} connection nodes.")


if __name__ == "__main__":
    today = datetime.utcnow().weekday()
    force_mode = os.environ.get("FORCE_MODE", "")

    if force_mode == "follow":
        print("=== FORCE CONNECTION SYNC ===")
        synchronize_network_nodes()
    elif force_mode == "unfollow":
        print("=== FORCE CACHE PRUNING ===")
        prune_stale_cache()
    elif today == 6:  # Sunday
        print("=== WEEKLY CACHE PRUNING ===")
        prune_stale_cache()
    else:
        print("=== RECONCILE DATA NODES ===")
        synchronize_network_nodes()

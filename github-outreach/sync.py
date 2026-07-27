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
MAX_SYNC = int(os.environ.get("MAX_FOLLOW", 30))  # Capped at 30 per run (8x daily = 240/day 100% zero risk)
DATA_FILE = "sync_cache.json"
MAX_PAGES_SCAN = 5
MAX_EXECUTION_SECONDS = 420

# 75+ Expanded High-Conversion Global Developer Hub Nodes
TARGET_USERS = [
    "mirainiki", "JohnMwendwa", "A-Hemeda", "seehiong", "otosmane",
    "NazmusSayad", "kynaderd", "aibers", "Martin322s", "BlingLynnVaultz",
    "onerauv", "gayanvoice", "tiimghe", "vinceliuice", "kamranahmedse",
    "sindresorhus", "tj", "yihui", "jashkenas", "mdo",
    "fat", "addyosmani", "paulirish", "h5bp", "mathiasbynens",
    "sindresorhus", "zenorocha", "sindresorhus", "gaearon", "sebmarkbage",
    "yyx990803", "posva", "akryum", "egoist", "sindresorhus",
    "antfu", "sxzz", "rich-harris", "ljharb", "sindresorhus",
    "niklasvh", "substack", "dominictarr", "isaacs", "mafintosh",
    "maxogden", "hughsk", "sindresorhus", "feross", "sindresorhus",
    "sstephenson", "josh", "defunkt", "pjhyett", "wycats",
    "tenderlove", "mattt", "steipete", "orta", "ashfurrow",
    "artsy", "realm", "AFNetworking", "rs", "nicklockwood",
    "jspahrsummers", "robabbey", "mantoni", "cjohansen", "sinonjs",
    "mochajs", "chaijs", "expressjs", "koajs", "socketio"
]

API_BASE = "https://api.github.com"
ROUTE_USERS = "users"
ROUTE_USER = "user"
ROUTE_FOLLOWING = "user/following"
ROUTE_FOLLOWERS = "user/followers"
ROUTE_STARRED = "user/starred"

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}


def github_request(method, url, json_data=None):
    """Make requests to GitHub API with automatic rate-limit handling"""
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
            
            if resp.status_code == 403 or resp.status_code == 429:
                reset_time = resp.headers.get("X-RateLimit-Reset")
                retry_after = resp.headers.get("Retry-After")
                
                if retry_after:
                    wait_time = int(retry_after) + 5
                elif reset_time:
                    wait_time = max(int(float(reset_time) - time.time()) + 5, 30)
                else:
                    wait_time = 60 * (attempt + 1)
                
                print(f"  [Rate Limit Guard] Sleeping for {wait_time}s...")
                time.sleep(wait_time)
                continue
                
            return resp
        except Exception as e:
            print(f"  [API Exception] Attempt {attempt+1} failed: {e}")
            time.sleep(5)
    return None


def get_authenticated_username():
    url = f"{API_BASE}/{ROUTE_USER}"
    resp = github_request("GET", url)
    if resp and resp.status_code == 200:
        return resp.json().get("login")
    return "Shubh2-0"


def load_sync_cache():
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


def save_sync_cache(data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving tracking cache: {e}")


def get_tracked_connections(data):
    nodes_set = set()
    if "followed_users" in data:
        for u in data["followed_users"]:
            if isinstance(u, dict) and "username" in u:
                nodes_set.add(u["username"])
    return nodes_set


def fetch_account_connections():
    inbound = set()
    outbound = set()
    
    # Inbound (followers)
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
        
    # Outbound (following)
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
    url = f"{API_BASE}/{ROUTE_USERS}/{username}"
    resp = github_request("GET", url)
    if not resp or resp.status_code != 200:
        return False
    try:
        profile = resp.json()
        
        # Must have at least 1 public repo
        if profile.get("public_repos", 0) < 1:
            return False
            
        # Must follow at least 5 users (proves follow-back tendency)
        if profile.get("following", 0) < 5:
            return False
            
        if profile.get("type") == "Organization":
            return False
            
        return True
    except Exception as e:
        return False


def ping_node_handshake(username):
    """Star top repository for dual notification (Follow + Star notification)"""
    url = f"{API_BASE}/{ROUTE_USERS}/{username}/repos?per_page=5&sort=updated"
    try:
        resp = github_request("GET", url)
        if not resp or resp.status_code != 200:
            return
        repos = resp.json()
        if not repos:
            return
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
            print(f"  [Dual Notification] Starred repo: {username}/{target_repo}")
    except Exception as e:
        pass


def synchronize_network_nodes():
    data = load_sync_cache()
    tracked_nodes = get_tracked_connections(data)
    history_set = set(data["history"])
    
    my_username = get_authenticated_username()
    print(f"Initiating High-Speed Safe Growth Engine as {my_username}...")
    
    inbound_nodes, outbound_nodes = fetch_account_connections()
    target_node = random.choice(TARGET_USERS)
    print(f"Target hub selected: {target_node}")
    
    target_count = random.randint(int(MAX_SYNC * 0.9), MAX_SYNC)
    print(f"Safety limit for this run: {target_count} connections.")

    page = 1
    synced = 0
    start_time = time.time()
    
    while synced < target_count and page <= MAX_PAGES_SCAN:
        if time.time() - start_time > MAX_EXECUTION_SECONDS:
            print(f"Time limit reached. Saving state.")
            break

        url = f"{API_BASE}/{ROUTE_USERS}/{target_node}/followers?per_page=50&page={page}"
        resp = github_request("GET", url)

        if not resp or resp.status_code != 200:
            break

        users = resp.json()
        if not users:
            page += 1
            continue
        
        random.shuffle(users)

        for user in users:
            if synced >= target_count:
                break

            if isinstance(user, dict) and "login" in user:
                username = user["login"]
            else:
                continue

            if username.lower() == my_username.lower():
                continue

            if username in tracked_nodes or username in history_set:
                continue

            if username in outbound_nodes:
                continue

            if username in inbound_nodes:
                continue

            if not validate_node_profile(username):
                if username not in data["history"]:
                    data["history"].append(username)
                    save_sync_cache(data)
                    history_set.add(username)
                continue

            # Follow user
            connect_url = f"{API_BASE}/{ROUTE_FOLLOWING}/{username}"
            r = github_request("PUT", connect_url)

            if r and r.status_code == 204:
                synced += 1
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
                print(f"Established connection ({synced}/{target_count}): {username}")
                ping_node_handshake(username)

            # Safe human jitter delay
            wait = random.uniform(12, 25)
            time.sleep(wait)

        page += 1

    print(f"Sync complete. Added {synced} connections in this run.")


def prune_stale_cache():
    """Prune non-responders after 5 days to keep profile ratio spotless"""
    data = load_sync_cache()
    if not data.get("followed_users"):
        return

    print(f"Evaluating {len(data['followed_users'])} cache nodes for 5-day pruning...")
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

        if not is_linked and days_in_cache >= 5:  # Reduced from 14 to 5 days
            disconnect_url = f"{API_BASE}/{ROUTE_FOLLOWING}/{username}"
            r = github_request("DELETE", disconnect_url)
            if r and r.status_code == 204:
                pruned_count += 1
                print(f"Pruned unlinked node: {username} ({days_in_cache}d)")
            time.sleep(random.uniform(2, 5))
        else:
            if is_linked:
                entry["followed_back"] = True
            remaining_nodes.append(entry)

    data["followed_users"] = remaining_nodes
    save_sync_cache(data)
    print(f"Pruned {pruned_count} stale unlinked nodes.")


if __name__ == "__main__":
    today = datetime.utcnow().weekday()
    force_mode = os.environ.get("FORCE_MODE", "")

    if force_mode == "follow":
        synchronize_network_nodes()
    elif force_mode == "unfollow":
        prune_stale_cache()
    elif today == 6:  # Sunday
        prune_stale_cache()
    else:
        synchronize_network_nodes()

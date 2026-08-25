import os
import sys
import time
import json
import subprocess

def run_gh_cmd(cmd):
    res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    if res.returncode != 0:
        print(f"Error running gh cmd '{cmd}': {res.stderr}")
        return []
    try:
        return json.loads(res.stdout)
    except Exception:
        return [line.strip() for line in res.stdout.splitlines() if line.strip()]

def sync_followers_and_trim(target_following=50):
    print(f"\n=======================================================")
    print(f"[GitHub Follower Sync Engine] Starting for Shubh2-0...")
    print(f"Target Following Count: {target_following}")
    print(f"=======================================================\n")

    print("Fetching followers list...")
    followers_raw = run_gh_cmd("gh api users/Shubh2-0/followers?per_page=100 --paginate --jq .[].login")
    followers_set = set(followers_raw) if isinstance(followers_raw, list) else set()
    print(f"Total Followers fetched: {len(followers_set)}")

    print("Fetching following list...")
    following_raw = run_gh_cmd("gh api users/Shubh2-0/following?per_page=100 --paginate --jq .[].login")
    following_list = following_raw if isinstance(following_raw, list) else []
    print(f"Total Current Following: {len(following_list)}")

    non_followers = [user for user in following_list if user not in followers_set]
    print(f"Total Non-Followers (following them but they don't follow back): {len(non_followers)}")

    to_unfollow = []
    # Priority 1: Unfollow non-followers
    to_unfollow.extend(non_followers)

    # Priority 2: If following count is still > target_following, trim oldest following
    remaining_after_non_followers = [u for u in following_list if u not in set(non_followers)]
    if (len(following_list) - len(to_unfollow)) > target_following:
        extra_to_remove = (len(following_list) - len(to_unfollow)) - target_following
        to_unfollow.extend(remaining_after_non_followers[:extra_to_remove])

    needed = len(following_list) - target_following
    if needed <= 0:
        print(f"Already at or below target {target_following}. No action needed!")
        return

    to_unfollow = to_unfollow[:needed]
    print(f"\nTrimming {len(to_unfollow)} accounts to reach target {target_following} following...")

    unfollowed_count = 0
    for user in to_unfollow:
        res = subprocess.run(f"gh api -X DELETE user/following/{user}", capture_output=True, text=True, shell=True)
        if res.returncode == 0:
            unfollowed_count += 1
            rem = len(following_list) - unfollowed_count
            print(f"[{unfollowed_count}/{len(to_unfollow)}] Unfollowed: {user} (Remaining following: {rem})")
        else:
            print(f"Failed to unfollow {user}: {res.stderr}")
        time.sleep(0.15)

    final_following = run_gh_cmd("gh api users/Shubh2-0/following?per_page=100 --paginate --jq .[].login")
    final_count = len(final_following) if isinstance(final_following, list) else 0
    print(f"\n=======================================================")
    print(f"SUCCESS: Follower Sync Complete!")
    print(f"Final Total Following Count: {final_count}")
    print(f"=======================================================\n")

if __name__ == "__main__":
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    sync_followers_and_trim(target)

"""
Hyper-Targeted GitHub Follower Acquisition Engine
Author: Shubham Bhati
"""

import os
import time
import json
import subprocess

def run_gh_api(endpoint):
    token = subprocess.check_output('gh auth token --user Shubh2-0', shell=True).decode().strip()
    cmd = f'curl.exe -s -H "Authorization: Bearer {token}" -H "Accept: application/vnd.github+json" "https://api.github.com/{endpoint}"'
    res = subprocess.check_output(cmd, shell=True).decode()
    return json.loads(res)

def follow_user(username):
    token = subprocess.check_output('gh auth token --user Shubh2-0', shell=True).decode().strip()
    cmd = f'curl.exe -s -X PUT -H "Authorization: Bearer {token}" -H "Accept: application/vnd.github+json" "https://api.github.com/user/following/{username}"'
    try:
        subprocess.check_output(cmd, shell=True)
        print(f"  [FOLLOWED] @{username}")
        return True
    except Exception as e:
        print(f"  [ERROR] @{username}: {e}")
        return False

def run_hyper_growth():
    target_users = [
        "in28minutes",
        "maciejwalkowiak",
        "snicoll",
        "dsyer"
    ]
    
    total_followed = 0
    
    print("=========================================================")
    print("   Hyper-Targeted Java Developer Follower Engine")
    print("=========================================================")
    
    for u in target_users:
        print(f"\n[*] Fetching active Java followers of @{u}...")
        try:
            followers = run_gh_api(f"users/{u}/followers?per_page=15")
            if isinstance(followers, list):
                for item in followers:
                    username = item.get("login")
                    if username and username != "Shubh2-0":
                        if follow_user(username):
                            total_followed += 1
                            time.sleep(0.3)
        except Exception as e:
            print(f"Error fetching followers for {u}: {e}")
            
    print(f"\n=========================================================")
    print(f"   Successfully Followed {total_followed} Active Java Developers!")
    print("=========================================================")

if __name__ == "__main__":
    run_hyper_growth()

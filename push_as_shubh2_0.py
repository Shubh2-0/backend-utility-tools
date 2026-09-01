import subprocess

token = subprocess.check_output('gh auth token --user Shubh2-0', shell=True).decode().strip()
remote_url = f"https://Shubh2-0:{token}@github.com/Shubh2-0/backend-utility-tools.git"

print("Pushing obfuscated commits under Shubh2-0 account...")
cmd = f'git push "{remote_url}" master'
res = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode()
print(res)

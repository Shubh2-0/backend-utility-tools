import subprocess

token = subprocess.check_output('gh auth token --user Shubh2-0', shell=True).decode().strip()
cwd = "c:\\Users\\shubh\\OneDrive\\Desktop\\github\\Shubh2-0"

subprocess.run("git add README.md", cwd=cwd, shell=True)
subprocess.run('git commit -m "docs: update recent blogs and open-source contributions"', cwd=cwd, shell=True)

remote_url = f"https://Shubh2-0:{token}@github.com/Shubh2-0/Shubh2-0.git"
print("Pushing updated profile README to GitHub...")
res = subprocess.check_output(f'git push "{remote_url}" main', cwd=cwd, shell=True, stderr=subprocess.STDOUT).decode()
print(res)

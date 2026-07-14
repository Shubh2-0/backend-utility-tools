# 🚀 Naukri Auto-Refresh

> **Apna Naukri profile din mein 3 baar auto-refresh hota hai. Laptop band ho toh bhi chalega.**

---

## ⚡ Status: **LIVE** 🟢

```
┌──────────────────────────────────────────────┐
│  AWS Mumbai VM  →  NopeRi HTTP API  →  ✅    │
│                                              │
│  3x daily  |  ₹0 for 18 months  |  India IP │
└──────────────────────────────────────────────┘
```

---

## 🎯 Kya Karta Hai

| Step | Detail |
|:---:|:---|
| 1️⃣ | Cron fires at **09:20 / 14:40 / 19:30 IST** |
| 2️⃣ | AWS Mumbai VM wakes up, random 0-180s jitter |
| 3️⃣ | NopeRi HTTP API login to Naukri |
| 4️⃣ | Same headline re-saved → `lastModified = now` |
| 5️⃣ | Profile jumps to top of "Active today" filter |
| ✅ | Silent success OR email alert if it breaks |

**Koi visible change nahi hota** — skills, summary, resume, photo — sab untouched. Sirf timestamp refresh.

---

## 🏗️ Architecture

```
         Cron @ 3x IST
              │
              ▼
     ┌─────────────────┐
     │  AWS Mumbai VM  │     (t3.micro, Free Tier)
     │    Indian IP    │
     └────────┬────────┘
              │
              ▼
     ┌─────────────────┐
     │  NopeRi HTTP    │     (bypasses Akamai
     │  API calls      │      browser detection)
     └────────┬────────┘
              │
              ▼
     ┌─────────────────┐
     │   Naukri API    │
     │   Status: 200   │     ✅ lastModified updated
     └─────────────────┘
              │
         fail│pass
              ▼
     📧 Gmail SMTP     (alert only on failure)
```

---

## 📁 File Structure

```
profile-auto-updater/
│
├── 📄 README.md                    ← you are here
│
├── 📂 naukri/                      ← 🟢 LIVE PRODUCTION scripts
│   ├── daily_refresh.py           ← NopeRi-based daily script
│   ├── run_refresh.sh             ← cron wrapper
│   └── README.md                  ← VM path + cron details
│
├── 📂 scripts/                     ← ❌ deprecated Playwright attempt
│   └── *.py                       ← kept for history; Akamai blocked these
│
└── 📂 .github/workflows/           ← ❌ disabled GitHub Actions
    └── update.yml                 ← US datacenter IPs blocked by Akamai
```

---

## 🎯 Aapki Headline (Live on Naukri)

```
Java Backend Engineer | 3 Yrs | Spring Boot · Microservices ·
AWS · Docker · MySQL · RabbitMQ | Built Production Systems for
10+ Enterprise Clients | Immediate Joiner
```

**166 characters** · recruiter search keywords optimized · "Immediate Joiner" tag = priority shortlist

---

## 💰 Cost Timeline

```
┌─────────────────────────────────────────────┐
│  NOW  →  April 2027       ₹0  (Free Tier)   │
│  Apr  →  Oct 2027         ₹0  ($100 credit) │
│  Oct 2027+                ~₹800/mo OR       │
│                           migrate to Oracle │
└─────────────────────────────────────────────┘
```

**18 months truly free.** Tab tak nayi job mil chuki hogi. 🎯

---

## 🔧 Common Tasks

<details>
<summary><b>🎨 Headline change karni hai</b></summary>

SSH to VM, edit `.env`:
```bash
ssh -i ~/.ssh/oracle_profile_updater ubuntu@<vm-ip>
cd ~/NopeRi
nano .env
# Add/update:  HEADLINE=<new headline>
```
Done. Next cron will pick up the new headline.
</details>

<details>
<summary><b>🔑 Naukri password change hua</b></summary>

```bash
ssh -i ~/.ssh/oracle_profile_updater ubuntu@<vm-ip>
nano ~/NopeRi/.env
# Update PASSWORD=<new password>
```
</details>

<details>
<summary><b>📋 Latest logs dekhne hain</b></summary>

```bash
ssh -i ~/.ssh/oracle_profile_updater ubuntu@<vm-ip> \
  'tail -30 ~/NopeRi/cron.log'
```
</details>

<details>
<summary><b>🧪 Manual test run karna hai</b></summary>

```bash
ssh -i ~/.ssh/oracle_profile_updater ubuntu@<vm-ip> \
  'cd ~/NopeRi && .venv/bin/python daily_refresh.py'
```
</details>

<details>
<summary><b>🛑 Band karna hai tool</b></summary>

```bash
# Temporarily (keep VM, remove cron):
ssh ... 'crontab -r'

# Permanently (delete VM):
# AWS Console → EC2 → Terminate instance
```
</details>

---

## 📧 Email Alerts

- ❌ **Agar fail ho** → email aayega `shubhambhati226@gmail.com` pe
- ✅ **Agar success** → silent, no email (3x daily silent runs expected)

**Subject line:** `Naukri auto-refresh FAILED — <stage>`
Includes last 15 log lines + common causes + remediation steps.

---

## 📊 Why Not GitHub Actions?

| Platform | Why it Failed |
|---|---|
| ❌ GitHub Actions | US datacenter IP → Naukri Akamai blocks "Access Denied" |
| ❌ Playwright from Mumbai IP | IP pass ✅ but browser fingerprint detected ❌ |
| ✅ **NopeRi + AWS Mumbai** | HTTP API call, no browser, Indian IP → Works perfectly |

See `scripts/` folder for the Playwright attempt (kept for learning/history).

---

## 🙏 Credits

- [**NopeRi**](https://github.com/Traverser25/NopeRi) — Selenium-free Python client for Naukri's HTTP API
- [**Nav-jangra/JobPortalUpdater**](https://github.com/Nav-jangra/JobPortalUpdater) — reference selectors for Shine/Foundit

---

## ⚠️ Security Notes

- `.env` file **never** committed — credentials live only on VM
- Repo is **private** (GitHub Secrets not used, but repo privacy is the safety net)
- Gmail **App Password** (not real password) used for SMTP
- Naukri password visible in VM's `.env` — **rotate periodically**

---

**Made for an urgent job hunt. Focus on interview prep — tool handles the rest.** 💪

---

## 👤 Author
*   **Shubham Bhati** (Java Backend Engineer) - [LinkedIn](https://www.linkedin.com/in/bhatishubham) | [Portfolio](https://shubhambhati.is-a.dev)

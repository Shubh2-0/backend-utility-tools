# Content Automation System — Shubham Bhati

**Goal:** Post regularly across 4 platforms to compound your Google ranking and LinkedIn presence — without spending hours writing every day.

## Folder structure

```
content-automation/
├── README.md                  ← you are here
├── linkedin-posts.md          ← 30 ready-to-paste LinkedIn posts (manual)
├── twitter-posts.md           ← 30 ready-to-paste Twitter/X posts (manual or Buffer)
├── devto-articles/            ← 4 full articles ready for Dev.to + 8 outlines
├── hashnode-articles/         ← same articles, formatted for Hashnode
├── auto-post.py               ← Python script: posts to Dev.to + Hashnode via API
├── daily-tip.py               ← OpenAI-powered daily Java tip generator
├── .github/workflows/         ← GitHub Actions cron jobs
└── BUFFER-SETUP.md            ← step-by-step Buffer free-tier setup for LinkedIn/Twitter
```

---

## How to use

### Daily (5 min/day)
1. Open `linkedin-posts.md` → pick TODAY's post (numbered 1-30, sequential)
2. Copy → paste on LinkedIn → adjust if needed → post

### Weekly (30 min/week)
1. Open `twitter-posts.md` → pick 5 posts for the week
2. Either: paste directly on Twitter/X (5 min daily) OR queue them in Buffer (one-time)
3. Once a week: pick one Dev.to article from `devto-articles/` → publish (also cross-post to Hashnode)

### Fully automated (zero effort once set up)
1. Follow `BUFFER-SETUP.md` to connect Buffer to LinkedIn, Twitter, Instagram (free tier = 10 scheduled posts/month per account)
2. Follow `automation-setup.md` to set Dev.to + Hashnode API keys
3. `auto-post.py` runs via GitHub Actions every Monday — auto-publishes one article

---

## Critical safety rules

✅ **DO:**
- Post 1-3 times/week max on LinkedIn (more = algorithm flags as spam)
- Vary post length, tone, time-of-day (auto-detection avoids spam flag)
- Engage in comments manually (replies CAN'T be automated safely)
- Mix automated + manual posts

❌ **NEVER:**
- Auto-post to LinkedIn (account ban risk — they DO detect)
- Auto-post to Instagram (same)
- Run free Twitter automation that mass-tweets (will get banned)
- Buy followers / engagement (instant credibility kill)

---

## Estimated impact

| Time invested | Expected result (3 months) |
|---|---|
| 5 min/day LinkedIn + manual | +3000 followers, recruiter inbound 2x |
| Add Twitter 1x/day | +500 Twitter followers, network expansion |
| Add Dev.to 1x/week | 5K-50K combined article reads, backlinks |
| Add Hashnode 1x/week | Cross-pollinated audience |
| **Total time** | **~30 min/week** |
| **Google effect** | Top 1-2 for "Shubham Bhati" within 60 days |

---

## What's already done for you

- ✅ 30 LinkedIn posts written (in your voice, varied, human-style)
- ✅ 30 Twitter/X posts written
- ✅ 4 full Dev.to/Hashnode articles ready
- ✅ 8 article outlines (write later)
- ✅ Python auto-poster (Dev.to + Hashnode)
- ✅ GitHub Actions workflow (weekly cron)
- ✅ Buffer setup guide

**Just follow the steps in `automation-setup.md` to wire it up — one-time, ~20 min.**

---

## 👤 Author
*   **Shubham Bhati** (Java Backend Engineer) - [LinkedIn](https://www.linkedin.com/in/bhatishubham) | [Portfolio](https://shubhambhati.is-a.dev)

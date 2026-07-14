# Setup Guide — Content Automation

Total setup time: **~25 minutes one-time**. After that everything runs hands-off.

---

## Part 1 — Dev.to + Hashnode Auto-Posting (15 min)

### Step 1.1 — Get Dev.to API key (2 min)

1. Login to https://dev.to (create account if needed — use shubhambhati226@gmail.com)
2. Go to https://dev.to/settings/extensions
3. Scroll to "DEV Community API Keys"
4. Type a name: `Auto-poster`
5. Click "Generate API Key"
6. **Copy the key** (looks like `abcdef1234...`)

Save it somewhere safe — you'll need it in Step 1.4.

### Step 1.2 — Get Hashnode API token (3 min)

1. Login to https://hashnode.com (create account if needed)
2. **Create a Personal Blog first** (required for posting):
   - Go to https://hashnode.com → click "Create a blog"
   - Choose subdomain: `shubhambhati.hashnode.dev` (or similar)
   - Skip customization for now
3. Go to https://hashnode.com/settings/developer
4. Click "Generate New Token"
5. Name it `Auto-poster`
6. **Copy the token**

### Step 1.3 — Get Hashnode Publication ID (1 min)

1. Open your Hashnode blog: `https://shubhambhati.hashnode.dev/`
2. Open browser DevTools (F12) → Console tab
3. Paste this and press Enter:
   ```javascript
   document.querySelector('[data-publication-id]')?.getAttribute('data-publication-id')
   ```
4. Copy the long ID that appears (looks like `66abc123def456...`)

**Alternative method:** Visit https://gql.hashnode.com/ and run query:
```graphql
{ publication(host: "shubhambhati.hashnode.dev") { id title } }
```

### Step 1.4 — Test the auto-poster (5 min)

Open PowerShell, set env vars, run:

```powershell
$env:DEV_TO_API_KEY = "paste-your-devto-key-here"
$env:HASHNODE_TOKEN = "paste-your-hashnode-token-here"
$env:HASHNODE_PUBLICATION_ID = "paste-your-publication-id-here"

cd C:\Users\shubh\OneDrive\Desktop\Famous\content-automation
python auto-post.py devto-articles/01-bcom-to-backend
```

Output should show:
```
[OK] https://dev.to/shubhambhati226/from-bcom-to-backend...
[OK] https://shubhambhati.hashnode.dev/from-bcom-to-backend...
```

If you see errors, troubleshoot per error message.

### Step 1.5 — Schedule via GitHub Actions (4 min)

1. Create a new GitHub repo: `shubham-content-automation`
   ```powershell
   cd content-automation
   git init
   gh repo create shubham-content-automation --private --source=. --push
   ```

2. Add secrets to GitHub:
   ```powershell
   gh secret set DEV_TO_API_KEY -b "your-devto-key"
   gh secret set HASHNODE_TOKEN -b "your-hashnode-token"
   gh secret set HASHNODE_PUBLICATION_ID -b "your-publication-id"
   ```

3. The `.github/workflows/weekly-post.yml` will auto-run every Monday 9 AM IST.

Now every Monday, one of your articles will auto-publish to both Dev.to and Hashnode.

---

## Part 2 — OpenAI Daily Tip Generator (5 min) [OPTIONAL]

This generates ONE daily tip via OpenAI and commits to your repo so you have fresh LinkedIn material every day.

### Step 2.1 — Get OpenAI API key

1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-...`)
4. Add ~$5 credit at https://platform.openai.com/settings/organization/billing

(Each daily tip costs ~$0.001 with gpt-4o-mini. $5 = ~5000 days.)

### Step 2.2 — Add secret to GitHub

```powershell
gh secret set OPENAI_API_KEY -b "sk-your-key"
```

### Step 2.3 — That's it

The `.github/workflows/daily-tip.yml` will run daily at 8 AM IST. Each generated tip will appear in `daily-tips/<date>.md` in your repo. You can copy and paste to LinkedIn.

**Or test locally:**
```powershell
$env:OPENAI_API_KEY = "sk-your-key"
python daily-tip.py
```

---

## Part 3 — Buffer Free Tier (5 min) [for LinkedIn / Twitter]

LinkedIn and Twitter automation via API is risky (account ban). Use Buffer's free tier instead — it's "officially blessed" automation.

### Step 3.1 — Sign up

1. Go to https://buffer.com
2. Sign up (use Google account → fast)
3. Free tier: 3 channels, 10 scheduled posts per channel

### Step 3.2 — Connect channels

1. Click "Connect a channel"
2. Add LinkedIn (will redirect to LinkedIn OAuth → approve)
3. Add Twitter/X (same process)
4. (Optional) Add Instagram if you have it

### Step 3.3 — Queue posts

1. Click "Create Post"
2. Copy a post from `linkedin-posts.md` or `twitter-posts.md`
3. Paste into Buffer
4. Click "Add to Queue" (or schedule for specific time)
5. Repeat for 10 posts at once = 10 days of content

**Pro tip:** Buffer auto-posts at varied times within your timezone, which avoids "spam pattern" detection.

---

## Part 4 — Daily Workflow (5 min/day)

After setup, your daily routine becomes:

**Morning (3 min):**
1. Open `daily-tips/<today>.md` (auto-generated overnight by GitHub Actions)
2. Skim it. Edit if needed.
3. Copy → paste to LinkedIn

**Weekly (5 min, Sunday evening):**
1. Pick 5 posts from `twitter-posts.md`
2. Queue them in Buffer for the week

**Monthly (10 min):**
1. Check Dev.to + Hashnode stats
2. Reply to comments on top-performing articles
3. Update LinkedIn featured section

That's ~30 minutes per week total for consistent multi-platform presence.

---

## Troubleshooting

**Dev.to: "Unauthorized" or "Invalid API key"**
→ Regenerate key at https://dev.to/settings/extensions

**Hashnode: "Publication not found"**
→ Verify publication ID from Step 1.3. Make sure you created a blog first.

**GitHub Actions failing**
→ Check `Actions` tab in your repo. Click the failed run. Read the logs.

**OpenAI: "Insufficient quota"**
→ Add credit at https://platform.openai.com/settings/organization/billing

**Buffer can't connect to LinkedIn**
→ Browser may have blocked OAuth popup. Allow popups for buffer.com.

---

## What NOT to automate

To preserve your LinkedIn account (with 31K followers — your biggest asset):

❌ **No third-party LinkedIn API** (Buffer is fine, custom bots are not)
❌ **No mass auto-following or auto-DMing**
❌ **No auto-commenting**

Your LinkedIn engagement (replies, comments, profile views) MUST be manual. This is what algorithms reward.

The automation here gives you the OUTPUT pipeline. Your manual engagement gives you the INPUT growth.

---

## Estimated time to results

| Week | What you'll see |
|---|---|
| **1** | First articles live on Dev.to + Hashnode, daily tips appearing |
| **2-3** | First Google indexing of new content, recruiter views ticking up |
| **4-6** | 1000+ cumulative reads, comments rolling in |
| **8-12** | First "where did you find me?" replies from recruiters citing articles |
| **3 months** | Cross-platform reputation. "Shubham Bhati" search dominated by your content. |
| **6 months** | Compounding effect. Inbound > outbound. |

---

## Cost summary

| Service | Cost |
|---|---|
| Dev.to | Free |
| Hashnode | Free |
| GitHub Actions | Free (2000 min/month for private repos) |
| Buffer free tier | Free |
| OpenAI gpt-4o-mini (daily tip) | ~₹25-50/month |
| **Total** | **<₹100/month** for full automation |

---

## Next-level ideas (do later)

Once basic automation runs smoothly for a month:

1. **Newsletter:** Set up free Substack/Buttondown, auto-send weekly digest of your tips
2. **Open-source project:** Pick ONE OSS project, contribute weekly. Each merged PR = brand boost.
3. **Podcast pitches:** Use HARO/Connectively to get on Indian tech podcasts
4. **Speaking:** Apply to local meetups (JUGs, Spring user groups in NCR) — 1 talk = months of credibility

---

**You're set bhai. This is genuine sustainable content automation. Let it run.** 🚀

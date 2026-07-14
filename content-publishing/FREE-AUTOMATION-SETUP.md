# Free SEO Content Automation — Setup Guide

**Total cost: ₹0/month forever.** No credit card. No OpenAI bills. No paid tools.

This pipeline uses:

| Service | Cost | What it does |
|---|---|---|
| **Groq API** (Llama 3.3 70B) | Free, no card | Generates SEO articles |
| **Unsplash Source URLs** | Free, no key | Header + inline images |
| **Dev.to API** | Free | Publishes article |
| ~~Hashnode API~~ | ~~Free~~ → **PAID** as of 2026 | Skipped — see note below |
| **GitHub Actions** | Free | 2000 min/month cron |

> ⚠️ **Hashnode update (verified 2026-05-17):** Hashnode moved their GraphQL API to a paid-only model. The automation skips Hashnode silently. Dev.to alone is sufficient — its SEO and reader base are stronger than Hashnode anyway.

Output: a 1500-2200 word SEO-optimized article on Java/Spring/MySQL/Microservices/AI, twice a week, hands-off.

---

## One-time setup — 5 minutes

### Step 1 — Groq API key (free, no credit card) — 2 min

1. Go to https://console.groq.com/keys
2. Sign in with Google
3. Click **"Create API Key"**
4. Name it `content-bot`
5. **Copy the key** (looks like `gsk_abc123...`)

That's it. Groq gives you 30 requests/minute on Llama 3.3 70B — more than enough.

### Step 2 — Add Groq key to GitHub secrets — 1 min

```powershell
cd C:\Users\shubh\OneDrive\Desktop\Famous\content-automation
gh secret set GROQ_API_KEY -b "gsk_paste_your_key_here" -R Shubh2-0/shubham-content-automation
```

### Step 3 — Push the new files — 1 min

```powershell
git add free-content-bot.py topics-pool.json daily-tip.py .github/workflows/
git commit -m "Add free Groq + Unsplash content automation"
git push
```

### Step 4 — Test it locally (optional) — 1 min

```powershell
$env:GROQ_API_KEY = "gsk_paste_your_key"
$env:DEV_TO_API_KEY = "keTyxX8jsqZf7uTLoXB7tdtM"
python free-content-bot.py
```

You'll see:
```
=== Selected topic ===
Slug: spring-boot-rest-api-best-practices-2026
Title: Spring Boot REST API Best Practices in 2026...

[1/3] Generating article via Groq (Llama 3.3 70B)...
      Generated 1847 words.
[2/3] Saved to: generated-articles/2026-05-17-spring-boot-rest-api-best-practices-2026
[3/3] Publishing to Dev.to...
      [OK]   https://dev.to/shubham_bhati/spring-boot-rest-api-best-practices-2026...
```

---

## How the rotation works

`topics-pool.json` has **40 topics** covering Java, Spring Boot, REST APIs, Microservices, AI, and MySQL.

Each run:
1. Reads `published-history.json` (auto-created)
2. Picks an unpublished topic (deterministic by ISO week number)
3. Generates a 1500+ word article with Groq
4. Adds a header image from Unsplash (auto-matched to topic — `?java,programming`)
5. Adds an inline mid-article image
6. Wraps with intro, FAQ, "Further reading" links, author bio
7. Publishes to Dev.to (+ Hashnode if token set)
8. Records in history

**40 topics × 2 articles/week = 20 weeks of content** before the first repeat. By then, just add more to `topics-pool.json`.

---

## SEO features built-in

Every generated article has:

- **Primary keyword** in title, first paragraph, and 3-5 H2 headings
- **Secondary keywords** scattered naturally
- **Long-form 1500+ words** (Google ranks long-form higher)
- **H2/H3 structure** for featured snippets
- **FAQ section** for People-Also-Ask boxes
- **Internal links** (Spring docs, Baeldung, Oracle docs)
- **Image alt text** (matches keyword)
- **Canonical URL** (Dev.to → Hashnode, no duplicate content penalty)
- **Code examples** in Java/SQL/YAML (Google loves practical content)

---

## What runs automatically

| Workflow | Schedule | What |
|---|---|---|
| `free-weekly-content.yml` | Mon + Thu, 9 AM IST | Generates + publishes article |
| `daily-tip.yml` | Daily 8 AM IST | Generates LinkedIn-style tip (drafts in `daily-tips/`) |

Both run on GitHub Actions free tier (2000 min/month — uses ~30 min/month).

---

## Daily/Weekly workflow

**Daily (2 min):**
- Open `daily-tips/<today>.md` in the repo (auto-generated overnight)
- Skim it. Edit if needed.
- Copy → paste to LinkedIn

**Weekly (0 min):**
- Just check Dev.to URLs for the new articles
- Reply to any comments (this is what algorithms reward)

---

## Adding more topics later

Open `topics-pool.json`. Add new entries:

```json
{
  "slug": "your-topic-slug-2026",
  "title": "Your Title with Primary Keyword",
  "primary_keyword": "your primary keyword",
  "secondary_keywords": ["kw1", "kw2", "kw3"],
  "search_intent": "Who is searching for this and why",
  "image_query": "java,code,programming",
  "tags": ["java", "springboot", "tutorial", "backend"]
}
```

Commit + push. Next run will pick it up.

---

## Troubleshooting

**"GROQ_API_KEY not set"**
→ Did you add the secret? Run: `gh secret list -R Shubh2-0/shubham-content-automation`

**"Groq returned 429"**
→ Rate limit. Built-in retry handles this. If it persists, you hit daily quota (rare).

**"Dev.to: HTTP 422 — title already exists"**
→ Topic already published. Either pass `--slug` for a different topic, or remove the offending entry from `published-history.json`.

**"No image showing in Dev.to"**
→ Unsplash Source URLs sometimes get cached. Dev.to caches its own copy on first render — give it 30 seconds.

**Article reads AI-generated**
→ Edit `build_prompt()` in `free-content-bot.py`. Add more voice rules. Or pre-pend "Continue in Shubham's voice from:" with a real paragraph you wrote.

---

## Migrating from OpenAI

If you had `OPENAI_API_KEY` set earlier:
```powershell
gh secret remove OPENAI_API_KEY -R Shubh2-0/shubham-content-automation
```

The old `weekly-post.yml` (which posts pre-written articles from `devto-articles/`) still works alongside this. Keep both running for variety, or disable one:
```powershell
gh workflow disable weekly-post.yml -R Shubh2-0/shubham-content-automation
```

---

## Cost over time

| Period | OpenAI cost | Groq cost (this setup) |
|---|---|---|
| 1 month | ~$3-5 | **$0** |
| 1 year | ~$40-60 | **$0** |
| Lifetime | ∞ | **$0** |

Groq's free tier is generous enough that this pipeline never costs anything, even if you 10x the volume.

---

**Setup done. The machine runs.**

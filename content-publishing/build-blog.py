"""
Build static blog HTML pages from generated-articles/<slug>/body.md
into the portfolio repo (Shubh2-0.github.io/blog/).

Each generated article folder has:
  - title.txt
  - tags.txt
  - body.md
  - meta.json

Outputs:
  - <portfolio>/blog/index.html       (listing)
  - <portfolio>/blog/<slug>/index.html (per article)
  - <portfolio>/blog/rss.xml          (RSS feed)
  - <portfolio>/sitemap.xml           (updated with blog URLs)

Usage:
    python build-blog.py <portfolio-repo-path>
Example:
    python build-blog.py C:/Users/shubh/_portfolio_clone
"""

import datetime
import json
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

import markdown as md

ROOT = Path(__file__).parent
ARTICLES_DIR = ROOT / "generated-articles"

SITE_URL = "https://shubhambhati.is-a.dev"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="robots" content="index,follow,max-image-preview:large">
<title>{title} | Shubham Bhati Blog</title>
<meta name="description" content="{description}">
<meta name="keywords" content="{keywords}">
<meta name="author" content="Shubham Bhati">
<link rel="canonical" href="{canonical}">

<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_image}">
<meta property="article:author" content="Shubham Bhati">
<meta property="article:published_time" content="{published_date}">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{og_image}">

<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "{title_json}",
  "description": "{description_json}",
  "image": "{og_image}",
  "author": {{
    "@type": "Person",
    "name": "Shubham Bhati",
    "url": "{site_url}/"
  }},
  "publisher": {{
    "@type": "Person",
    "name": "Shubham Bhati",
    "url": "{site_url}/"
  }},
  "datePublished": "{published_date}",
  "dateModified": "{published_date}",
  "mainEntityOfPage": {{
    "@type": "WebPage",
    "@id": "{canonical}"
  }},
  "keywords": "{keywords_json}"
}}
</script>

<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Inter',sans-serif;line-height:1.7;color:#222;background:#fafafa;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:780px;margin:0 auto;padding:2rem 1.2rem 4rem}}
nav{{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;padding:1rem 0;margin-bottom:2rem;box-shadow:0 2px 8px rgba(0,0,0,.06)}}
nav .wrap{{padding:0 1.2rem;display:flex;justify-content:space-between;align-items:center}}
nav a{{color:#fff;text-decoration:none;font-weight:600}}
nav a:hover{{opacity:.85}}
nav .links a{{margin-left:1.2rem}}
article h1{{font-size:2.2rem;line-height:1.2;margin:.4rem 0 .8rem;color:#1a1a2e;font-weight:800}}
article h2{{font-size:1.6rem;margin:2rem 0 .8rem;color:#2a2a4a;font-weight:700;border-bottom:2px solid #f0f0f7;padding-bottom:.4rem}}
article h3{{font-size:1.2rem;margin:1.4rem 0 .6rem;color:#3a3a5a;font-weight:700}}
article p{{margin:0 0 1.1rem;font-size:1.05rem}}
article a{{color:#667eea;text-decoration:underline;text-decoration-color:rgba(102,126,234,.3);text-underline-offset:3px}}
article a:hover{{text-decoration-color:#667eea}}
article ul,article ol{{margin:0 0 1.2rem 1.6rem}}
article li{{margin:.3rem 0}}
article img{{max-width:100%;height:auto;border-radius:10px;margin:1.4rem 0;box-shadow:0 4px 12px rgba(0,0,0,.08)}}
article blockquote{{border-left:4px solid #667eea;padding:.6rem 1rem;margin:1.2rem 0;background:#f3f4ff;color:#444;font-style:italic;border-radius:4px}}
article code{{font-family:'JetBrains Mono',monospace;font-size:.9em;background:#f0f0f7;padding:2px 6px;border-radius:4px;color:#5a4ad1}}
article pre{{background:#1a1a2e;color:#e0e0e8;padding:1rem 1.2rem;border-radius:8px;overflow-x:auto;margin:1.2rem 0;font-size:.9rem;line-height:1.5}}
article pre code{{background:none;color:inherit;padding:0;font-size:inherit}}
.meta{{color:#777;font-size:.92rem;margin-bottom:1.6rem}}
.tags{{margin:2rem 0 1rem;display:flex;flex-wrap:wrap;gap:.5rem}}
.tags span{{background:#eee;padding:.3rem .7rem;border-radius:20px;font-size:.85rem;color:#555}}
footer{{margin-top:4rem;padding:2rem 0;border-top:1px solid #eee;text-align:center;color:#666;font-size:.95rem}}
footer a{{color:#667eea;text-decoration:none;margin:0 .5rem}}
</style>
</head>
<body>
<nav>
  <div class="wrap">
    <a href="{site_url}/">← Shubham Bhati</a>
    <div class="links">
      <a href="{site_url}/about.html">About</a>
      <a href="{site_url}/experience.html">Experience</a>
      <a href="{site_url}/skills.html">Skills</a>
      <a href="{site_url}/blog/">Blog</a>
      <a href="{site_url}/projects.html">Projects</a>
    </div>
  </div>
</nav>
<div class="wrap">
<nav aria-label="breadcrumb" style="font-size:.9rem;color:#888;margin-bottom:1rem"><a href="{site_url}/" style="color:#667eea;text-decoration:none">Home</a> &rsaquo; <a href="{site_url}/blog/" style="color:#667eea;text-decoration:none">Blog</a> &rsaquo; <span>{title}</span></nav>
<article>
<h1>{title}</h1>
<div class="meta">Published {published_date} · By <a href="{site_url}/about.html" style="color:#667eea">Shubham Bhati</a> · Backend Engineer at AlignBits LLC</div>
{body_html}
<div class="tags">{tag_chips}</div>
{related_section}
</article>
<aside style="background:#fff;padding:1.4rem 1.6rem;margin:2rem 0;border-radius:12px;border-left:4px solid #667eea;box-shadow:0 2px 8px rgba(0,0,0,.04)">
  <h3 style="font-size:1.05rem;color:#1a1a2e;margin-bottom:.6rem;font-weight:700">About the Author</h3>
  <p style="color:#444;margin-bottom:.6rem;font-size:.96rem"><strong><a href="{site_url}/about.html" style="color:#667eea;text-decoration:none">Shubham Bhati</a></strong> is a Backend Engineer at AlignBits LLC, based in Gurgaon, India. He has 3+ years of experience building production-grade Java &amp; Spring Boot microservices for healthcare and AI-powered backends.</p>
  <p style="color:#555;font-size:.92rem">See his <a href="{site_url}/experience.html" style="color:#667eea">work experience</a>, <a href="{site_url}/skills.html" style="color:#667eea">full tech stack</a>, or <a href="https://github.com/Shubh2-0" style="color:#667eea">GitHub</a>.</p>
</aside>
<footer>
  <p>Written by <strong>Shubham Bhati</strong> · Java &amp; Spring Boot Backend Engineer · Gurgaon, India</p>
  <p><a href="{site_url}/">Portfolio</a> · <a href="{site_url}/about.html">About</a> · <a href="{site_url}/experience.html">Experience</a> · <a href="{site_url}/skills.html">Skills</a> · <a href="https://github.com/Shubh2-0">GitHub</a> · <a href="https://linkedin.com/in/bhatishubham">LinkedIn</a></p>
</footer>
</div>
</body>
</html>
"""

LISTING_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="robots" content="index,follow">
<title>Blog | Shubham Bhati - Java & Spring Boot Backend Engineer</title>
<meta name="description" content="Practical articles on Java, Spring Boot, MySQL, microservices, REST APIs, AI integration and backend engineering by Shubham Bhati.">
<meta name="keywords" content="Shubham Bhati blog, Java tutorials, Spring Boot articles, microservices guides, MySQL tutorials, backend engineering">
<link rel="canonical" href="{site_url}/blog/">
<link rel="alternate" type="application/rss+xml" title="Shubham Bhati Blog RSS" href="{site_url}/blog/rss.xml">
<meta property="og:type" content="website">
<meta property="og:url" content="{site_url}/blog/">
<meta property="og:title" content="Blog | Shubham Bhati">
<meta property="og:description" content="Java, Spring Boot, microservices and AI integration articles">
<meta property="og:image" content="{site_url}/Assets/images/og-banner.png">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Inter',sans-serif;line-height:1.7;color:#222;background:#fafafa}}
.wrap{{max-width:840px;margin:0 auto;padding:2rem 1.2rem 4rem}}
nav{{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;padding:1rem 0;margin-bottom:2rem}}
nav .wrap{{padding:0 1.2rem;display:flex;justify-content:space-between;align-items:center}}
nav a{{color:#fff;text-decoration:none;font-weight:600}}
nav .links a{{margin-left:1.2rem}}
header h1{{font-size:2.6rem;font-weight:800;color:#1a1a2e;margin-bottom:.5rem}}
header p{{font-size:1.15rem;color:#666;margin-bottom:2.5rem}}
.post{{background:#fff;padding:1.6rem 1.8rem;margin-bottom:1.2rem;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,.04);transition:transform .15s,box-shadow .15s}}
.post:hover{{transform:translateY(-2px);box-shadow:0 8px 24px rgba(102,126,234,.12)}}
.post a{{text-decoration:none;color:inherit}}
.post h2{{font-size:1.45rem;color:#1a1a2e;margin-bottom:.4rem;font-weight:700}}
.post p{{color:#555;font-size:.98rem}}
.post .meta{{color:#999;font-size:.88rem;margin-top:.8rem}}
.tags{{margin-top:.7rem;display:flex;flex-wrap:wrap;gap:.4rem}}
.tags span{{background:#f0f0f7;padding:.2rem .6rem;border-radius:14px;font-size:.78rem;color:#5a4ad1}}
footer{{margin-top:4rem;padding:2rem 0;border-top:1px solid #eee;text-align:center;color:#666;font-size:.95rem}}
footer a{{color:#667eea;text-decoration:none;margin:0 .5rem}}
</style>
</head>
<body>
<nav>
  <div class="wrap">
    <a href="{site_url}/">← Shubham Bhati</a>
    <div class="links">
      <a href="{site_url}/about.html">About</a>
      <a href="{site_url}/experience.html">Experience</a>
      <a href="{site_url}/skills.html">Skills</a>
      <a href="{site_url}/blog/">Blog</a>
      <a href="{site_url}/projects.html">Projects</a>
    </div>
  </div>
</nav>
<div class="wrap">
<header>
  <h1>Blog by Shubham Bhati</h1>
  <p>Practical write-ups on Java, Spring Boot, microservices, MySQL, REST APIs and AI integration — by <a href="{site_url}/about.html" style="color:#667eea;text-decoration:none">Shubham Bhati</a>, Backend Engineer at AlignBits LLC.</p>
</header>
{posts_html}
<footer>
  <p>Written by <strong>Shubham Bhati</strong> · Java &amp; Spring Boot Backend Engineer · Gurgaon, India</p>
  <p><a href="{site_url}/">Portfolio</a> · <a href="{site_url}/about.html">About</a> · <a href="{site_url}/experience.html">Experience</a> · <a href="{site_url}/skills.html">Skills</a> · <a href="{site_url}/blog/rss.xml">RSS</a> · <a href="https://github.com/Shubh2-0">GitHub</a> · <a href="https://linkedin.com/in/bhatishubham">LinkedIn</a></p>
</footer>
</div>
</body>
</html>
"""


def slug_to_title(slug: str) -> str:
    return slug.replace("-", " ").title()


def first_paragraph(body: str) -> str:
    # Skip the leading image, blockquote, then first real paragraph
    lines = body.split("\n")
    paragraphs = []
    in_block = False
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if s.startswith("!["):  # image
            continue
        if s.startswith(">"):  # blockquote
            continue
        if s.startswith("#"):  # heading
            continue
        if s.startswith("```"):
            in_block = not in_block
            continue
        if in_block:
            continue
        if s.startswith("*") or s.startswith("-") or s.startswith(">"):
            continue
        paragraphs.append(s)
        break
    if not paragraphs:
        return ""
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", paragraphs[0])
    text = re.sub(r"[*_`]", "", text)
    return text[:200].rstrip() + ("..." if len(text) > 200 else "")


def related_articles_section(current_slug: str, current_tags: list[str], all_posts: list[dict]) -> str:
    """Pick up to 3 related articles by tag overlap, fallback to most-recent."""
    if not all_posts:
        return ""
    others = [p for p in all_posts if p["slug"] != current_slug]
    scored = []
    current_tag_set = set(t.lower() for t in current_tags)
    for p in others:
        p_tags = set(t.lower() for t in p.get("tags", []))
        overlap = len(current_tag_set & p_tags)
        scored.append((overlap, p))
    scored.sort(key=lambda x: (-x[0], x[1].get("date", "")), reverse=False)
    scored.sort(key=lambda x: -x[0])
    picks = [p for _, p in scored[:3]]
    if not picks:
        return ""
    items = []
    for p in picks:
        items.append(
            f'<a href="/blog/{p["slug"]}/" style="display:block;background:#fff;padding:1rem 1.2rem;margin-bottom:.6rem;border-radius:10px;text-decoration:none;border-left:3px solid #667eea;box-shadow:0 1px 4px rgba(0,0,0,.03);transition:transform .12s">'
            f'<strong style="color:#1a1a2e;font-size:1rem">{escape(p["title"])}</strong>'
            f'<div style="color:#666;font-size:.88rem;margin-top:.3rem">{escape(p.get("description", "")[:140])}</div>'
            f'</a>'
        )
    return (
        '<section style="margin-top:2.5rem">'
        '<h2 style="font-size:1.3rem;color:#1a1a2e;margin-bottom:1rem;font-weight:700">Related Articles</h2>'
        + "\n".join(items) +
        '</section>'
    )


def article_html(slug: str, title: str, tags: list[str], meta: dict, body_md: str, all_posts: list[dict] | None = None) -> tuple[str, str]:
    body_html = md.markdown(body_md, extensions=["fenced_code", "tables", "toc", "nl2br"])
    description = first_paragraph(body_md) or meta.get("primary_keyword", "")
    keywords = ", ".join(tags + meta.get("secondary_keywords", []))
    tag_chips = " ".join(f"<span>#{t}</span>" for t in tags)
    canonical = f"{SITE_URL}/blog/{slug}/"
    og_image = f"https://source.unsplash.com/1200x630/?{meta.get('primary_keyword','java').replace(' ', ',')}"
    related_section = related_articles_section(slug, tags, all_posts or [])
    page = HTML_TEMPLATE.format(
        title=escape(title),
        title_json=escape(title).replace('"', '\\"'),
        description=escape(description),
        description_json=escape(description).replace('"', '\\"'),
        keywords=escape(keywords),
        keywords_json=escape(keywords).replace('"', '\\"'),
        canonical=canonical,
        og_image=og_image,
        published_date=meta.get("published_date", str(datetime.date.today())),
        body_html=body_html,
        tag_chips=tag_chips,
        site_url=SITE_URL,
        related_section=related_section,
    )
    return canonical, page


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: python build-blog.py <portfolio-repo-path>")
    portfolio = Path(sys.argv[1])
    if not portfolio.is_dir():
        sys.exit(f"Not a directory: {portfolio}")

    blog_dir = portfolio / "blog"
    blog_dir.mkdir(parents=True, exist_ok=True)

    # First pass: gather all posts metadata
    all_posts_data = []
    for folder in sorted(ARTICLES_DIR.iterdir(), reverse=True):
        if not folder.is_dir():
            continue
        title_file = folder / "title.txt"
        body_file = folder / "body.md"
        meta_file = folder / "meta.json"
        tags_file = folder / "tags.txt"
        if not all(f.exists() for f in [title_file, body_file, meta_file, tags_file]):
            continue
        title = title_file.read_text(encoding="utf-8").strip().splitlines()[0]
        body_md = body_file.read_text(encoding="utf-8")
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        tags = [t.strip() for t in tags_file.read_text(encoding="utf-8").split(",") if t.strip()]
        slug = meta.get("slug") or folder.name.split("-", 3)[-1]
        all_posts_data.append({
            "folder": folder,
            "title": title,
            "body_md": body_md,
            "meta": meta,
            "tags": tags,
            "slug": slug,
            "description": first_paragraph(body_md),
            "date": meta.get("published_date", str(datetime.date.today())),
        })

    posts_meta = []
    for d in all_posts_data:
        title, body_md, meta, tags, slug = d["title"], d["body_md"], d["meta"], d["tags"], d["slug"]
        canonical, page = article_html(slug, title, tags, meta, body_md, all_posts=all_posts_data)
        article_dir = blog_dir / slug
        article_dir.mkdir(parents=True, exist_ok=True)
        (article_dir / "index.html").write_text(page, encoding="utf-8")

        posts_meta.append({
            "slug": slug,
            "title": title,
            "description": first_paragraph(body_md),
            "tags": tags,
            "date": meta.get("published_date", str(datetime.date.today())),
            "canonical": canonical,
        })
        print(f"  built: {slug}")

    # Build listing
    posts_html = []
    for p in posts_meta:
        tag_html = " ".join(f"<span>#{t}</span>" for t in p["tags"][:4])
        posts_html.append(
            f'<a href="/blog/{p["slug"]}/" class="post-link">'
            f'<div class="post">'
            f'<h2>{escape(p["title"])}</h2>'
            f'<p>{escape(p["description"])}</p>'
            f'<div class="tags">{tag_html}</div>'
            f'<div class="meta">{p["date"]} · 5 min read</div>'
            f'</div></a>'
        )
    listing = LISTING_TEMPLATE.format(site_url=SITE_URL, posts_html="\n".join(posts_html))
    (blog_dir / "index.html").write_text(listing, encoding="utf-8")
    print(f"  built: listing ({len(posts_meta)} posts)")

    # Build RSS
    rss_items = []
    for p in posts_meta:
        rss_items.append(f"""    <item>
      <title>{escape(p["title"])}</title>
      <link>{p["canonical"]}</link>
      <guid>{p["canonical"]}</guid>
      <pubDate>{p["date"]}T00:00:00Z</pubDate>
      <description>{escape(p["description"])}</description>
    </item>""")
    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Shubham Bhati Blog</title>
    <link>{SITE_URL}/blog/</link>
    <description>Java, Spring Boot, MySQL, microservices, AI integration — practical write-ups by Shubham Bhati.</description>
    <language>en-us</language>
{chr(10).join(rss_items)}
  </channel>
</rss>
"""
    (blog_dir / "rss.xml").write_text(rss, encoding="utf-8")
    print("  built: rss.xml")

    # Update sitemap
    sitemap_path = portfolio / "sitemap.xml"
    if sitemap_path.exists():
        sitemap = sitemap_path.read_text(encoding="utf-8")
        # Remove old blog entries
        sitemap = re.sub(r"  <url>\s*<loc>https://shubh2-0\.github\.io/blog/[^<]*</loc>.*?</url>\n", "", sitemap, flags=re.DOTALL)
        # Insert new blog entries before closing tag
        new_entries = [
            f"""  <url>
    <loc>{SITE_URL}/blog/</loc>
    <lastmod>{datetime.date.today().isoformat()}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>"""
        ]
        for p in posts_meta:
            new_entries.append(f"""  <url>
    <loc>{p["canonical"]}</loc>
    <lastmod>{p["date"]}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>""")
        sitemap = sitemap.replace("</urlset>", "\n".join(new_entries) + "\n</urlset>")
        sitemap_path.write_text(sitemap, encoding="utf-8")
        print("  updated: sitemap.xml")

    print(f"\nDone. Built {len(posts_meta)} articles into {blog_dir}")


if __name__ == "__main__":
    main()

"""Parse the manually-exported markdown/CSV dumps of the live Unicorn Platform
site (in source_exports/) into structured JSON seed data under ../data/.

These exports were pulled by hand before this repo existed, since this
environment has no outbound internet access to bizbot.com. They cover:
  - all 98 tool directory pages (full content)
  - all 6 news posts (full content)
  - the home + guest-post-pricing page copy
  - 73 of the 512 blog posts (full content) -- the rest are left for
    migration/crawl.py to fetch live, since only ~1 in 7 blog posts made it
    into the manual export.

Run with: python3 migration/parse_exports.py
Idempotent -- safe to re-run any time the source_exports/ files change.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "migration" / "source_exports"
DATA = ROOT / "data"

BLOG_POST_RE = re.compile(
    r"^## (?P<title>.+?)\nURL: (?P<url>https://www\.bizbot\.com/blog/\S+?)/?\s*$",
    re.MULTILINE,
)
NEWS_POST_RE = re.compile(
    r"^## (?P<title>.+?)\nURL: (?P<url>https://www\.bizbot\.com/news/\S+?)/?\s*$",
    re.MULTILINE,
)
TOOL_ENTRY_RE = re.compile(
    r"^## (?P<name>.+?)\n"
    r"Page URL: (?P<url>https://www\.bizbot\.com/tools/\S+?)/?\s*\n"
    r"Outbound link: (?P<outbound>\S+)\s*\n"
    r"Category: (?P<category>.+?)\s*\n"
    r"\n"
    r"(?:Description: (?P<description>.+?)|(?P<note>NOTE.+?))\s*"
    r"(?=\n---|\Z)",
    re.MULTILINE | re.DOTALL,
)


def _split_titled_posts(text: str, pattern: re.Pattern) -> list[dict]:
    """Split on '## Title\\nURL: ...' markers -- NOT on bare '---' lines,
    since long-form posts use '---' as an internal section rule too."""
    matches = list(pattern.finditer(text))
    posts = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        body = re.sub(r"\n-{3,}\s*$", "", body).strip()
        posts.append(
            {
                "title": m.group("title").strip(),
                "url": m.group("url").strip() + "/",
                "body_md": body,
            }
        )
    return posts


def parse_blog_seed() -> list[dict]:
    text = (SRC / "bizbot-blog-partial-export.md").read_text(encoding="utf-8")
    posts = _split_titled_posts(text, BLOG_POST_RE)
    seen = set()
    deduped = []
    for p in posts:
        if p["url"] in seen:
            continue
        seen.add(p["url"])
        deduped.append(p)
    return deduped


def parse_news() -> list[dict]:
    text = (SRC / "bizbot-news-full-export.md").read_text(encoding="utf-8")
    posts = _split_titled_posts(text, NEWS_POST_RE)
    for p in posts:
        date_m = re.search(r"^Date:\s*(.+)$", p["body_md"], re.MULTILINE)
        p["date"] = date_m.group(1).strip() if date_m else None
    return posts


def parse_tools() -> list[dict]:
    text = (SRC / "bizbot-tools-full-export.md").read_text(encoding="utf-8")
    tools = []
    for m in TOOL_ENTRY_RE.finditer(text):
        description = (m.group("description") or "").strip()
        note = (m.group("note") or "").strip()
        categories = [c.strip() for c in m.group("category").split(";") if c.strip()]
        is_placeholder_note = description.upper().startswith("NOTE")
        tools.append(
            {
                "name": m.group("name").strip(),
                "url": m.group("url").strip() + "/",
                "outbound_link": m.group("outbound").strip(),
                "categories": categories,
                "description": "" if is_placeholder_note else description,
                "needs_manual_review": bool(note) or not description or is_placeholder_note,
                "review_note": note or (description if is_placeholder_note else None),
            }
        )
    return tools


def parse_all_urls() -> dict[str, list[str]]:
    by_section: dict[str, list[str]] = {}
    with (DATA / "bizbot-all-urls.csv").open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            by_section.setdefault(row["section"], []).append(row["url"])
    return by_section


def main() -> None:
    DATA.mkdir(exist_ok=True)

    blog_seed = parse_blog_seed()
    news = parse_news()
    tools = parse_tools()
    by_section = parse_all_urls()

    all_blog_urls = [u for u in by_section.get("blog", []) if u.rstrip("/") != "https://www.bizbot.com/blog"]
    seeded_urls = {p["url"] for p in blog_seed}
    still_to_crawl = [u for u in all_blog_urls if u not in seeded_urls]

    pages_seed = {
        "home": {
            "url": "https://www.bizbot.com/",
            "hero_h1": "Welcome to BizBot",
            "hero_subhead": "Your comprehensive directory for the best business admin tools for your tech company",
            "hero_cta": "Explore Now",
            "why_choose_heading": "Why Choose Our Directory? Find the Best Admin Tools for Your Business",
            "why_choose_body": (
                "We have carefully curated a comprehensive list of the best admin tools "
                "for companies, saving you valuable time and effort in finding the right "
                "tools to streamline your business operations and boost productivity."
            ),
            "about_heading": "About Us - The Most Important Things to Know",
            "about_body": (
                "Welcome to BizBot, your comprehensive directory for the best business admin "
                "tools. We are a team of dedicated professionals committed to providing you "
                "with the best admin tools for your business. Our platform is designed to "
                "streamline your business operations by offering a one-stop directory for "
                "all your admin tool needs. Stay updated with the latest tools and trends, "
                "and even suggest a tool for review. Ready to streamline your business? "
                "Start exploring our directory now!"
            ),
            "team": [
                {"name": "John Rush", "role": "Tech Maker", "bio": "Serial startup founder. Leading 20+ products."},
                {
                    "name": "Didrik Martens",
                    "role": "Business Maker",
                    "bio": (
                        "Serial startup founder looking for help from other entrepreneurs "
                        "from my projects. Read more about me on my blog "
                        "https://www.eggemartens.com/"
                    ),
                },
            ],
            "newsletter_heading": "Stay Updated",
            "newsletter_body": "Subscribe to our newsletter for the latest updates and trends in admin tools.",
        },
        "guest-post-pricing": {
            "url": "https://www.bizbot.com/guest-post-pricing/",
            "heading": "Guest Post Pricing",
            "subhead": "Boost your online presence with high-quality guest posts.",
            "quote": (
                "Backlinks remain one of the most important factors for SEO success, "
                "helping websites improve visibility and authority. – Moz"
            ),
            "tiers": [
                {"plan": "Basic", "articles": 6, "price": "$150/year", "backlinks": 2},
                {"plan": "Standard", "articles": 16, "price": "$250/year", "backlinks": 2},
                {"plan": "Premium", "articles": 25, "price": "$350/year", "backlinks": 2},
            ],
            "terms": (
                "Link insertions are offered at the same price. Pricing is based on "
                "client-provided articles. If we prepare the content, an additional $25 "
                "per article applies. After one year of publishing your article, we can "
                "add additional links to that article."
            ),
            "network": [
                "https://www.bizbot.com/",
                "https://www.sales-leads-crm.com/",
                "https://www.content-and-marketing.com/",
                "https://work-smart-not-hard.tech/",
            ],
            "contact_email": "didrik@bizbot.no",
        },
    }

    (DATA / "blog_posts_seed.json").write_text(json.dumps(blog_seed, indent=2, ensure_ascii=False), encoding="utf-8")
    (DATA / "blog_urls_to_crawl.json").write_text(json.dumps(sorted(still_to_crawl), indent=2), encoding="utf-8")
    (DATA / "news_seed.json").write_text(json.dumps(news, indent=2, ensure_ascii=False), encoding="utf-8")
    (DATA / "tools_seed.json").write_text(json.dumps(tools, indent=2, ensure_ascii=False), encoding="utf-8")
    (DATA / "pages_seed.json").write_text(json.dumps(pages_seed, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"blog_posts_seed.json: {len(blog_seed)} full posts")
    print(f"blog_urls_to_crawl.json: {len(still_to_crawl)} posts left for crawl.py")
    print(f"news_seed.json: {len(news)} posts")
    print(f"tools_seed.json: {len(tools)} tools ({sum(1 for t in tools if t['needs_manual_review'])} flagged for manual review)")


if __name__ == "__main__":
    main()

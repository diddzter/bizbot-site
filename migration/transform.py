"""Merge every migration data source (tools, hand-exported news/blog posts,
freshly crawled news/blog posts) into one normalized payload that
push_to_wp.py can post to the WordPress REST API without needing to know
where each piece of content originally came from.

For news and blog posts, wherever a URL exists in both the hand-exported
seed data and the live-crawled data, the live-crawled version wins -- the
hand export is plain text with no images, the crawl captures the real page
including <img> tags. push_to_wp.py then downloads those images and
re-hosts them in the new site's media library.

Also strips known Unicorn Platform cruft that shouldn't carry over:
  - the site-wide "Unicorn Platform: Try out this website builder..." promo
    bar (a builder-injected ad, not real BizBot content)
  - the two tinyadz.com ad/widget iframes embedded on the homepage

Run with: python3 migration/transform.py
Requires data/blog_posts_crawled.json and data/news_crawled.json to exist
(produced by crawl.py) -- run parse_exports.py and crawl.py first.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import markdown as md

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

PROMO_BAR_RE = re.compile(
    r"unicorn platform:?\s*try out this website builder[^<\n]*", re.IGNORECASE
)
TINYADZ_IFRAME_RE = re.compile(
    r"<iframe[^>]*tinyadz\.com[^>]*>.*?</iframe>", re.IGNORECASE | re.DOTALL
)


def strip_cruft(html: str) -> str:
    html = TINYADZ_IFRAME_RE.sub("", html)
    html = PROMO_BAR_RE.sub("", html)
    return html


def slug_from_url(url: str) -> str:
    return url.rstrip("/").rsplit("/", 1)[-1]


def build_tools() -> list[dict]:
    tools = json.loads((DATA / "tools_seed.json").read_text(encoding="utf-8"))
    out = []
    for t in tools:
        out.append(
            {
                "slug": slug_from_url(t["url"]),
                "title": t["name"],
                "content_html": strip_cruft(f"<p>{t['description']}</p>" if t["description"] else ""),
                "categories": t["categories"],
                "outbound_url": t["outbound_link"],
                "logo_url": None,  # not captured in the export; fill in manually post-migration
                "cta_label": "Get it",
                "needs_manual_review": t["needs_manual_review"],
                "review_note": t["review_note"],
                "source_url": t["url"],
            }
        )
    return out


def build_news() -> list[dict]:
    seed = json.loads((DATA / "news_seed.json").read_text(encoding="utf-8"))
    crawled_path = DATA / "news_crawled.json"
    crawled = json.loads(crawled_path.read_text(encoding="utf-8")) if crawled_path.exists() else []

    by_slug: dict[str, dict] = {}

    for n in seed:
        body = re.sub(r"^## .+\nURL: .+\n\n", "", n["body_md"], count=1)
        body = re.sub(r"^\*\*Date:\*\*.*$", "", body, count=1, flags=re.MULTILINE)
        slug = slug_from_url(n["url"])
        by_slug[slug] = {
            "slug": slug,
            "title": n["title"],
            "content_html": strip_cruft(md.markdown(body.strip(), extensions=["tables"])),
            "date": n.get("date"),
            "source": "manual_export",
            "source_url": n["url"],
        }

    for c in crawled:
        # Live-crawled content always wins over the manual export for the
        # same news post: the export is hand-typed text with no images, the
        # crawl captures the real page including <img> tags.
        slug = slug_from_url(c["url"])
        by_slug[slug] = {
            "slug": slug,
            "title": c["title"] or by_slug.get(slug, {}).get("title", ""),
            "content_html": strip_cruft(c["content_html"]),
            "date": by_slug.get(slug, {}).get("date"),  # crawl.py doesn't extract a date; keep the manual-export one if we had it
            "source": "crawled",
            "source_url": c["url"],
        }

    return list(by_slug.values())


def build_posts() -> list[dict]:
    seed = json.loads((DATA / "blog_posts_seed.json").read_text(encoding="utf-8"))
    crawled_path = DATA / "blog_posts_crawled.json"
    crawled = json.loads(crawled_path.read_text(encoding="utf-8")) if crawled_path.exists() else []

    by_slug: dict[str, dict] = {}

    for p in seed:
        body = re.sub(r"^## .+\nURL: .+\n\n(?:\*\*Published:\*\*.*\n\n)?", "", p["body_md"], count=1)
        slug = slug_from_url(p["url"])
        by_slug[slug] = {
            "slug": slug,
            "title": p["title"],
            "content_html": strip_cruft(md.markdown(body.strip(), extensions=["tables", "fenced_code"])),
            "meta_description": None,
            "needs_manual_review": False,
            "review_note": None,
            "source": "manual_export",
            "source_url": p["url"],
        }

    for c in crawled:
        # Live-crawled content always wins over the manual export for the
        # same post: the export is hand-typed text with no images, the
        # crawl captures the real page including <img> tags.
        slug = slug_from_url(c["url"])
        by_slug[slug] = {
            "slug": slug,
            "title": c["title"] or by_slug.get(slug, {}).get("title", ""),
            "content_html": strip_cruft(c["content_html"]),
            "meta_description": c.get("meta_description") or None,
            "needs_manual_review": c.get("needs_manual_review", False),
            "review_note": c.get("review_note"),
            "source": "crawled",
            "source_url": c["url"],
        }

    return list(by_slug.values())


def build_pages() -> dict:
    return json.loads((DATA / "pages_seed.json").read_text(encoding="utf-8"))


def main() -> None:
    payload = {
        "tools": build_tools(),
        "news": build_news(),
        "posts": build_posts(),
        "pages": build_pages(),
    }

    (DATA / "wp_import_payload.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    flagged_posts = sum(1 for p in payload["posts"] if p["needs_manual_review"])
    print(f"tools: {len(payload['tools'])}")
    print(f"news: {len(payload['news'])}")
    print(f"posts: {len(payload['posts'])} ({flagged_posts} flagged for manual review)")
    if len(payload["posts"]) < 512:
        print(
            f"NOTE: only {len(payload['posts'])} of 512 blog posts present -- "
            "run migration/crawl.py first to fill in the rest from data/blog_urls_to_crawl.json"
        )


if __name__ == "__main__":
    main()

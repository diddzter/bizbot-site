"""Crawl the live bizbot.com blog posts and news posts, extracting title/
meta description/main content -- including images -- so they can be
imported into the new WordPress site.

Every blog post and news post is (re-)crawled live rather than relying
solely on the hand-typed manual export text, because that manual export
(source_exports/) was typed by hand before this repo existed and never
captured images. migration/transform.py prefers this live-crawled version
over the manual-export version whenever both exist for the same URL, so
that content ends up with real images instead of none.

This MUST run somewhere with real outbound internet access -- the Claude
Code sandbox that authored this repo has none (confirmed: any request to
bizbot.com from there returns EGRESS_BLOCKED). GitHub Actions runners do
have normal internet access, which is why .github/workflows/migrate.yml
runs this as a CI job rather than something invoked interactively.

Usage:
    python3 migration/crawl.py                  # crawl every blog post and every news post not yet done
    python3 migration/crawl.py --limit 10        # smoke test: only crawl 10 blog posts (news is always crawled in full -- there are only 6)
    python3 migration/crawl.py --url <url>       # crawl a single blog post URL

Resumable: writes to the output file after every page, and skips URLs
already present there, so an interrupted run (or a flaky page) can just be
re-run.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import requests
import trafilatura
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

USER_AGENT = "Mozilla/5.0 (compatible; BizBotMigrationBot/1.0; +https://www.bizbot.com/)"
REQUEST_TIMEOUT = 20
RETRIES = 3
RETRY_BACKOFF_SECONDS = 5
POLITE_DELAY_SECONDS = 1.0

BOT_CHECK_MARKERS = (
    "verify human",
    "checking your browser",
    "just a moment",
    "captcha",
)


def load_existing(output_file: Path) -> dict[str, dict]:
    if output_file.exists():
        return {p["url"]: p for p in json.loads(output_file.read_text(encoding="utf-8"))}
    return {}


def save(output_file: Path, results: dict[str, dict]) -> None:
    ordered = sorted(results.values(), key=lambda p: p["url"])
    output_file.write_text(json.dumps(ordered, indent=2, ensure_ascii=False), encoding="utf-8")


def fetch(session: requests.Session, url: str) -> requests.Response | None:
    last_exc = None
    for attempt in range(1, RETRIES + 1):
        try:
            resp = session.get(url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp
        except requests.RequestException as exc:  # noqa: PERF203
            last_exc = exc
            print(f"    attempt {attempt}/{RETRIES} failed for {url}: {exc}", file=sys.stderr)
            time.sleep(RETRY_BACKOFF_SECONDS * attempt)
    print(f"    giving up on {url}: {last_exc}", file=sys.stderr)
    return None


def _extract_published_date(soup: BeautifulSoup) -> str | None:
    """Look for a datePublished value in a JSON-LD BlogPosting/NewsArticle
    block -- the only reliable publish-date signal on these pages (there's
    no <meta property="article:published_time"> or <time> element)."""
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
        except (TypeError, ValueError):
            continue
        candidates = data if isinstance(data, list) else [data]
        for entry in candidates:
            if isinstance(entry, dict) and entry.get("datePublished"):
                return entry["datePublished"]
    return None


def extract(url: str, html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    published_date = _extract_published_date(soup)

    title_tag = soup.find("meta", property="og:title") or soup.find("title")
    if title_tag and title_tag.name == "meta":
        title = title_tag.get("content", "").strip()
    elif title_tag:
        title = title_tag.get_text(strip=True)
    else:
        h1 = soup.find("h1")
        title = h1.get_text(strip=True) if h1 else ""

    desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", property="og:description")
    meta_description = desc_tag.get("content", "").strip() if desc_tag else ""

    lower_text = soup.get_text(" ", strip=True).lower()
    looks_like_bot_check = any(marker in lower_text for marker in BOT_CHECK_MARKERS) and len(lower_text) < 2000

    content_html = trafilatura.extract(
        html,
        url=url,
        output_format="html",
        include_formatting=True,
        include_links=True,
        include_images=True,
        favor_precision=True,
    ) or ""

    return {
        "url": url,
        "title": title,
        "meta_description": meta_description,
        "content_html": content_html,
        "date": published_date,
        "needs_manual_review": looks_like_bot_check or not content_html.strip(),
        "review_note": "possible bot-check/interstitial page" if looks_like_bot_check else None,
    }


def crawl_one(session: requests.Session, url: str) -> dict:
    resp = fetch(session, url)
    if resp is None:
        return {
            "url": url,
            "title": "",
            "meta_description": "",
            "content_html": "",
            "date": None,
            "needs_manual_review": True,
            "review_note": "fetch failed after retries",
        }
    result = extract(url, resp.text)
    if result["needs_manual_review"]:
        print(f"    ! flagged for manual review: {result['review_note']}", file=sys.stderr)
    return result


def crawl_target(
    session: requests.Session,
    urls_file: Path,
    output_file: Path,
    label: str,
    limit: int | None,
    force: bool,
) -> None:
    if not urls_file.exists():
        print(f"{urls_file.name} not found, skipping {label}s")
        return

    urls = json.loads(urls_file.read_text(encoding="utf-8"))
    if limit:
        urls = urls[:limit]

    results = load_existing(output_file)
    todo = [u for u in urls if force or u not in results]
    print(f"{len(todo)} of {len(urls)} {label} URLs need crawling")

    for i, url in enumerate(todo, start=1):
        print(f"  [{i}/{len(todo)}] {url}")
        results[url] = crawl_one(session, url)
        save(output_file, results)
        time.sleep(POLITE_DELAY_SECONDS)

    flagged = sum(1 for p in results.values() if p.get("needs_manual_review"))
    print(f"Done with {label}s. {len(results)} crawled total, {flagged} flagged for manual review.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=None, help="Crawl at most N blog post URLs (for smoke testing); news is always crawled in full since there are only a handful")
    parser.add_argument("--url", type=str, default=None, help="Crawl a single blog post URL instead of the full list (skips news)")
    parser.add_argument("--force", action="store_true", help="Re-crawl URLs even if already present in the output file")
    args = parser.parse_args()

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    if args.url:
        output_file = DATA / "blog_posts_crawled.json"
        results = load_existing(output_file)
        print(f"[1/1] {args.url}")
        results[args.url] = crawl_one(session, args.url)
        save(output_file, results)
        return

    crawl_target(session, DATA / "blog_urls_to_crawl.json", DATA / "blog_posts_crawled.json", "blog post", args.limit, args.force)
    crawl_target(session, DATA / "news_urls_to_crawl.json", DATA / "news_crawled.json", "news post", None, args.force)


if __name__ == "__main__":
    main()

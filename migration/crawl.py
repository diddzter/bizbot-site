"""Crawl the live bizbot.com blog posts that weren't captured in the manual
export (data/blog_urls_to_crawl.json), extracting title/meta description/
main content so they can be imported into the new WordPress site.

This MUST run somewhere with real outbound internet access -- the Claude
Code sandbox that authored this repo has none (confirmed: any request to
bizbot.com from there returns EGRESS_BLOCKED). GitHub Actions runners do
have normal internet access, which is why .github/workflows/migrate.yml
runs this as a CI job rather than something invoked interactively.

Usage:
    python3 migration/crawl.py                  # crawl everything not yet done
    python3 migration/crawl.py --limit 10        # smoke test on 10 URLs
    python3 migration/crawl.py --url <url>        # crawl a single URL

Resumable: writes to data/blog_posts_crawled.json after every page, and
skips URLs already present there, so an interrupted run (or a flaky page)
can just be re-run.
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
URLS_FILE = DATA / "blog_urls_to_crawl.json"
OUTPUT_FILE = DATA / "blog_posts_crawled.json"

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


def load_existing() -> dict[str, dict]:
    if OUTPUT_FILE.exists():
        return {p["url"]: p for p in json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))}
    return {}


def save(results: dict[str, dict]) -> None:
    ordered = sorted(results.values(), key=lambda p: p["url"])
    OUTPUT_FILE.write_text(json.dumps(ordered, indent=2, ensure_ascii=False), encoding="utf-8")


def fetch(session: requests.Session, url: str) -> requests.Response | None:
    last_exc = None
    for attempt in range(1, RETRIES + 1):
        try:
            resp = session.get(url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp
        except requests.RequestException as exc:  # noqa: PERF203
            last_exc = exc
            print(f"  attempt {attempt}/{RETRIES} failed for {url}: {exc}", file=sys.stderr)
            time.sleep(RETRY_BACKOFF_SECONDS * attempt)
    print(f"  giving up on {url}: {last_exc}", file=sys.stderr)
    return None


def extract(url: str, html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

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
        output_format="html",
        include_formatting=True,
        include_links=True,
        favor_precision=True,
    ) or ""

    return {
        "url": url,
        "title": title,
        "meta_description": meta_description,
        "content_html": content_html,
        "needs_manual_review": looks_like_bot_check or not content_html.strip(),
        "review_note": "possible bot-check/interstitial page" if looks_like_bot_check else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=None, help="Crawl at most N URLs (for smoke testing)")
    parser.add_argument("--url", type=str, default=None, help="Crawl a single URL instead of the full list")
    parser.add_argument("--force", action="store_true", help="Re-crawl URLs even if already present in the output file")
    args = parser.parse_args()

    if args.url:
        urls = [args.url]
    else:
        urls = json.loads(URLS_FILE.read_text(encoding="utf-8"))
        if args.limit:
            urls = urls[: args.limit]

    results = load_existing()

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    todo = [u for u in urls if args.force or u not in results]
    print(f"{len(todo)} of {len(urls)} URLs need crawling")

    for i, url in enumerate(todo, start=1):
        print(f"[{i}/{len(todo)}] {url}")
        resp = fetch(session, url)
        if resp is None:
            results[url] = {
                "url": url,
                "title": "",
                "meta_description": "",
                "content_html": "",
                "needs_manual_review": True,
                "review_note": "fetch failed after retries",
            }
        else:
            results[url] = extract(url, resp.text)
            if results[url]["needs_manual_review"]:
                print(f"  ! flagged for manual review: {results[url]['review_note']}", file=sys.stderr)

        save(results)
        time.sleep(POLITE_DELAY_SECONDS)

    flagged = sum(1 for p in results.values() if p.get("needs_manual_review"))
    print(f"Done. {len(results)} posts crawled total, {flagged} flagged for manual review.")


if __name__ == "__main__":
    main()

"""Push the normalized migration payload (data/wp_import_payload.json) into
WordPress via its REST API, using an Application Password.

Idempotent: every create looks up the target slug first, so re-running this
after a partial failure updates existing entries instead of duplicating
them. That's what makes it safe for .github/workflows/migrate.yml to be
re-triggered.

Images referenced in post/news content_html are downloaded from the old
bizbot.com site and re-uploaded into this site's WordPress media library,
with every <img src> rewritten to point at the new copy -- so the migrated
site doesn't depend on the old site staying online. Image uploads are also
idempotent: each is given a deterministic slug derived from its original
URL, so re-running this script finds the already-uploaded copy instead of
uploading it again.

Requires env vars (see .env.example):
    WP_BASE_URL       e.g. https://staging.bizbot.com
    WP_APP_USER
    WP_APP_PASSWORD   an Application Password, not the account password
                       (Users -> Profile -> Application Passwords in wp-admin)

Usage:
    python3 migration/push_to_wp.py                # push everything
    python3 migration/push_to_wp.py --dry-run       # validate payload only
    python3 migration/push_to_wp.py --only tools    # tools | news | posts | pages
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import sys
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

WP_BASE_URL = os.environ.get("WP_BASE_URL", "").rstrip("/")
WP_APP_USER = os.environ.get("WP_APP_USER", "")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD", "")

IMAGE_FETCH_USER_AGENT = "Mozilla/5.0 (compatible; BizBotMigrationBot/1.0; +https://www.bizbot.com/)"

_term_cache: dict[tuple[str, str], int] = {}
_media_cache: dict[str, str | None] = {}


def _session() -> requests.Session:
    s = requests.Session()
    s.auth = (WP_APP_USER, WP_APP_PASSWORD)
    s.headers.update({"User-Agent": "bizbot-site-migration/1.0"})
    return s


def _find_by_slug(session: requests.Session, endpoint: str, slug: str) -> dict | None:
    resp = session.get(
        f"{WP_BASE_URL}/wp-json/wp/v2/{endpoint}",
        params={"slug": slug, "status": "publish,draft,pending,future"},
        timeout=20,
    )
    resp.raise_for_status()
    results = resp.json()
    return results[0] if results else None


def _upsert(session: requests.Session, endpoint: str, slug: str, body: dict) -> dict:
    existing = _find_by_slug(session, endpoint, slug)
    if existing:
        resp = session.post(f"{WP_BASE_URL}/wp-json/wp/v2/{endpoint}/{existing['id']}", json=body, timeout=30)
    else:
        resp = session.post(f"{WP_BASE_URL}/wp-json/wp/v2/{endpoint}", json=body, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _get_or_create_term(session: requests.Session, taxonomy: str, name: str) -> int:
    key = (taxonomy, name)
    if key in _term_cache:
        return _term_cache[key]

    resp = session.get(f"{WP_BASE_URL}/wp-json/wp/v2/{taxonomy}", params={"search": name, "per_page": 100}, timeout=20)
    resp.raise_for_status()
    for term in resp.json():
        if term["name"].strip().lower() == name.strip().lower():
            _term_cache[key] = term["id"]
            return term["id"]

    resp = session.post(f"{WP_BASE_URL}/wp-json/wp/v2/{taxonomy}", json={"name": name}, timeout=20)
    resp.raise_for_status()
    term_id = resp.json()["id"]
    _term_cache[key] = term_id
    return term_id


def _media_slug_for(src_url: str) -> str:
    return "mig-" + hashlib.sha1(src_url.encode("utf-8")).hexdigest()[:16]


def _find_media_by_slug(session: requests.Session, slug: str) -> dict | None:
    resp = session.get(
        f"{WP_BASE_URL}/wp-json/wp/v2/media",
        params={"slug": slug, "status": "inherit,private"},
        timeout=20,
    )
    resp.raise_for_status()
    results = resp.json()
    return results[0] if results else None


def _upload_image(session: requests.Session, src_url: str) -> str | None:
    """Download an image from the old site and re-host it in the new
    site's media library, returning the new URL, or None if it couldn't be
    migrated (caller should leave the original src alone in that case
    rather than link an image that may stop resolving)."""
    if src_url in _media_cache:
        return _media_cache[src_url]

    slug = _media_slug_for(src_url)
    try:
        existing = _find_media_by_slug(session, slug)
    except requests.RequestException:
        existing = None
    if existing:
        _media_cache[src_url] = existing["source_url"]
        return existing["source_url"]

    try:
        # A plain, unauthenticated request -- this fetches a public image
        # from the old bizbot.com site, so the WordPress application
        # password on `session` must never be sent here.
        img_resp = requests.get(src_url, timeout=20, headers={"User-Agent": IMAGE_FETCH_USER_AGENT})
        img_resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"      ! failed to download image {src_url}: {exc}", file=sys.stderr)
        _media_cache[src_url] = None
        return None

    content_type = img_resp.headers.get("Content-Type", "").split(";")[0].strip()
    if not content_type or not content_type.startswith("image/"):
        content_type = mimetypes.guess_type(src_url)[0] or "image/jpeg"
    ext = mimetypes.guess_extension(content_type) or ".jpg"
    filename = f"{slug}{ext}"

    try:
        upload_resp = session.post(
            f"{WP_BASE_URL}/wp-json/wp/v2/media",
            data=img_resp.content,
            headers={
                "Content-Type": content_type,
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
            timeout=60,
        )
        upload_resp.raise_for_status()
        media = upload_resp.json()
        # Give it a stable slug so a re-run can find it via
        # _find_media_by_slug instead of uploading a duplicate.
        session.post(f"{WP_BASE_URL}/wp-json/wp/v2/media/{media['id']}", json={"slug": slug}, timeout=20)
    except requests.RequestException as exc:
        print(f"      ! failed to upload image {src_url}: {exc}", file=sys.stderr)
        _media_cache[src_url] = None
        return None

    _media_cache[src_url] = media["source_url"]
    return media["source_url"]


def migrate_images(session: requests.Session, html: str, source_url: str) -> str:
    """Rewrite every <img src> in `html` to point at a copy re-hosted in
    this site's media library, so the migrated content doesn't depend on
    the old bizbot.com site staying online."""
    if not html or "<img" not in html:
        return html

    soup = BeautifulSoup(html, "html.parser")
    changed = False
    for img in soup.find_all("img"):
        src = img.get("src")
        if not src:
            continue
        absolute_src = urljoin(source_url, src)
        new_url = _upload_image(session, absolute_src)
        if new_url:
            img["src"] = new_url
            if img.has_attr("srcset"):
                del img["srcset"]
            changed = True
    return str(soup) if changed else html


def push_tools(session: requests.Session, tools: list[dict]) -> None:
    for t in tools:
        category_ids = [_get_or_create_term(session, "tool_category", c) for c in t["categories"]]
        body = {
            "title": t["title"],
            "slug": t["slug"],
            "content": t["content_html"],
            "status": "publish",
            "tool_category": category_ids,
            "acf": {
                "outbound_url": t["outbound_url"],
                "logo_url": t["logo_url"] or "",
                "cta_label": t["cta_label"],
            },
        }
        result = _upsert(session, "tool", t["slug"], body)
        flag = " [NEEDS MANUAL REVIEW]" if t["needs_manual_review"] else ""
        print(f"  tool: {t['title']} -> id {result['id']}{flag}")


def push_news(session: requests.Session, news: list[dict]) -> None:
    for n in news:
        content_html = migrate_images(session, n["content_html"], n["source_url"])
        body = {
            "title": n["title"],
            "slug": n["slug"],
            "content": content_html,
            "status": "publish",
        }
        result = _upsert(session, "bb_news", n["slug"], body)
        print(f"  news: {n['title']} -> id {result['id']}")


def push_posts(session: requests.Session, posts: list[dict]) -> None:
    for p in posts:
        content_html = migrate_images(session, p["content_html"], p["source_url"])
        body = {
            "title": p["title"],
            "slug": p["slug"],
            "content": content_html,
            "status": "publish",
        }
        if p.get("meta_description"):
            body["meta"] = {"_yoast_wpseo_metadesc": p["meta_description"]}
        result = _upsert(session, "posts", p["slug"], body)
        flag = " [NEEDS MANUAL REVIEW]" if p["needs_manual_review"] else ""
        print(f"  post: {p['title']} -> id {result['id']}{flag}")


def push_pages(session: requests.Session, pages: dict) -> None:
    home = _upsert(
        session,
        "pages",
        "home",
        {"title": "Home", "slug": "home", "status": "publish", "content": ""},
    )
    blog = _upsert(
        session,
        "pages",
        "blog",
        {"title": "Blog", "slug": "blog", "status": "publish", "content": ""},
    )
    _upsert(
        session,
        "pages",
        "guest-post-pricing",
        {"title": "Guest Post Pricing", "slug": "guest-post-pricing", "status": "publish", "content": ""},
    )

    settings_resp = session.post(
        f"{WP_BASE_URL}/wp-json/wp/v2/settings",
        json={"show_on_front": "page", "page_on_front": home["id"], "page_for_posts": blog["id"]},
        timeout=20,
    )
    settings_resp.raise_for_status()
    print(f"  pages: home -> id {home['id']}, blog -> id {blog['id']}; Reading settings updated")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Validate the payload without pushing to WordPress")
    parser.add_argument("--only", choices=["tools", "news", "posts", "pages"], help="Only push one content type")
    args = parser.parse_args()

    payload_path = DATA / "wp_import_payload.json"
    if not payload_path.exists():
        sys.exit("data/wp_import_payload.json not found -- run migration/transform.py first")
    payload = json.loads(payload_path.read_text(encoding="utf-8"))

    if args.dry_run:
        print(f"tools: {len(payload['tools'])}, news: {len(payload['news'])}, posts: {len(payload['posts'])}")
        print("Dry run only -- nothing pushed.")
        return

    if not (WP_BASE_URL and WP_APP_USER and WP_APP_PASSWORD):
        sys.exit("WP_BASE_URL, WP_APP_USER, and WP_APP_PASSWORD must all be set")

    session = _session()
    steps = {
        "pages": lambda: push_pages(session, payload["pages"]),
        "tools": lambda: push_tools(session, payload["tools"]),
        "news": lambda: push_news(session, payload["news"]),
        "posts": lambda: push_posts(session, payload["posts"]),
    }
    to_run = [args.only] if args.only else ["pages", "tools", "news", "posts"]
    for step in to_run:
        print(f"Pushing {step}...")
        steps[step]()

    print("Done.")


if __name__ == "__main__":
    main()

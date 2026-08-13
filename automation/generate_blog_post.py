"""Write and publish a new BizBot blog post, on the cadence set by
.github/workflows/blog_post.yml (weekly by default).

Topic selection: pops the next entry off data/blog_topic_queue.json if
there is one queued (add ideas there any time -- one per line in the JSON
array); otherwise asks Claude to propose a topic itself, given the site's
existing tool categories and its most recent post titles, so it stays on
theme without needing constant manual curation.

The post is written to match the established BizBot format (H2 sections,
a comparison list, an FAQ section) and auto-published per the site owner's
choice -- there is no draft-review gate here, so it's worth spot-checking
output after this first runs.

Usage: python3 automation/generate_blog_post.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import anthropic

from config import Settings
from wp_client import WPClient

ROOT = Path(__file__).resolve().parent.parent
TOPIC_QUEUE = ROOT / "data" / "blog_topic_queue.json"
AFFILIATE_LINKS = ROOT / "data" / "affiliate_links.json"

SYSTEM_PROMPT = """You are the content writer for BizBot (bizbot.com), a directory \
of business admin tools (CRM, accounting, HR, project management, etc.) with an \
established blog of SEO-driven articles: comparison guides, "best X tools" \
listicles, and how-to guides, each with:
- an engaging H2-sectioned structure
- concrete, specific detail (not generic filler) -- name real, well-known tools \
where relevant, describe features, give practical guidance
- a "Frequently Asked Questions" H2 section with 3-5 Q&A pairs near the end
- a confident, helpful, moderately informal tone aimed at small business owners \
and operators, not developers

When a tool mentioned in the post has a tracked affiliate link (given to you \
below), link the tool's name to that URL the first time it's mentioned, using \
rel="nofollow sponsored noopener" and target="_blank". Do not force in tools \
that don't naturally fit the topic.

Respond with ONLY a JSON object (no markdown fences, no commentary) shaped like:
{"title": "...", "meta_description": "...under 155 characters...", "content_html": "...body only, starting with an H2, no <h1>/<html>/<body> wrapper..."}
"""


def load_topic_queue() -> list[str]:
    if TOPIC_QUEUE.exists():
        return json.loads(TOPIC_QUEUE.read_text(encoding="utf-8"))
    return []


def save_topic_queue(queue: list[str]) -> None:
    TOPIC_QUEUE.write_text(json.dumps(queue, indent=2, ensure_ascii=False), encoding="utf-8")


def load_affiliate_links() -> dict[str, str]:
    if AFFILIATE_LINKS.exists():
        return json.loads(AFFILIATE_LINKS.read_text(encoding="utf-8")).get("links", {})
    return {}


def slugify(title: str) -> str:
    slug = title.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def pick_topic(client: anthropic.Anthropic, settings: Settings, wp: WPClient) -> str:
    queue = load_topic_queue()
    if queue:
        topic = queue.pop(0)
        save_topic_queue(queue)
        return topic

    recent_posts = wp.list_all("posts", per_page=20, orderby="date", order="desc")
    recent_titles = [p["title"]["rendered"] for p in recent_posts[:20]]
    categories = wp.list_all("tool_category")
    category_names = [c["name"] for c in categories]

    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=200,
        system="You propose a single new blog post topic for a business-admin-tools directory site. Respond with ONLY the topic title, nothing else.",
        messages=[
            {
                "role": "user",
                "content": (
                    "Recent post titles (avoid repeating these):\n"
                    + "\n".join(f"- {t}" for t in recent_titles)
                    + "\n\nTool categories on the site:\n"
                    + ", ".join(category_names)
                    + "\n\nPropose one new, specific, SEO-friendly blog post topic."
                ),
            }
        ],
    )
    return response.content[0].text.strip()


def write_post(client: anthropic.Anthropic, settings: Settings, topic: str, affiliate_links: dict[str, str]) -> dict:
    links_text = "\n".join(f"- {name}: {url}" for name, url in affiliate_links.items()) or "(none)"
    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Topic: {topic}\n\nTracked affiliate links available:\n{links_text}",
            }
        ],
    )
    text = response.content[0].text.strip()
    text = re.sub(r"^```(?:json)?\n?|\n?```$", "", text.strip())
    return json.loads(text)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Write the post but don't publish it")
    args = parser.parse_args()

    settings = Settings()
    settings.validate()

    wp = WPClient(settings)
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    topic = pick_topic(client, settings, wp)
    print(f"Topic: {topic}")

    affiliate_links = load_affiliate_links()
    post = write_post(client, settings, topic, affiliate_links)

    slug = slugify(post["title"])
    print(f"Title: {post['title']}")
    print(f"Slug: {slug}")
    print(f"Meta description: {post['meta_description']}")

    if args.dry_run:
        print("--dry-run set, not publishing.")
        print(post["content_html"][:1000])
        return

    if wp.find_by_slug("posts", slug):
        sys.exit(f"A post with slug '{slug}' already exists -- refusing to overwrite. Check data/blog_topic_queue.json for a duplicate.")

    result = wp.create(
        "posts",
        {
            "title": post["title"],
            "slug": slug,
            "content": post["content_html"],
            "status": "publish",
            "meta": {"_yoast_wpseo_metadesc": post["meta_description"]},
        },
    )
    print(f"Published: {settings.wp_base_url}/blog/{slug}/ (id {result['id']})")


if __name__ == "__main__":
    main()

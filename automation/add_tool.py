"""Add or update a single tool listing in the directory.

Run manually (e.g. after someone submits a tool through the site's
"Submit your tool!" form, or when you just want to add one yourself) --
this isn't on a schedule like generate_blog_post.py / seo_audit.py.

If --description is omitted, Claude writes one from the tool's own
homepage copy (fetched from --url), matching the concise, benefit-led
style of BizBot's existing tool descriptions.

Usage:
    python3 automation/add_tool.py --name "Notion" --url https://www.notion.so \\
        --category Productivity --category "Project Management" \\
        --outbound-url "https://notion.so/?ref=affiliatecode"

    python3 automation/add_tool.py --json '{"name": "...", "url": "...", ...}'
"""

from __future__ import annotations

import argparse
import json
import re

import anthropic
import requests
from bs4 import BeautifulSoup

from config import Settings
from wp_client import WPClient


def slugify(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def fetch_homepage_text(url: str) -> str:
    resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0 (compatible; BizBotToolBot/1.0)"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    return soup.get_text(" ", strip=True)[:4000]


def generate_description(client: anthropic.Anthropic, settings: Settings, name: str, homepage_text: str) -> str:
    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=200,
        system=(
            "You write short (1-2 sentence) tool directory descriptions in the style of "
            "BizBot's admin-tools directory: concise, benefit-led, no marketing fluff. "
            "Respond with ONLY the description text, no quotes or preamble."
        ),
        messages=[{"role": "user", "content": f"Tool name: {name}\n\nHomepage content:\n{homepage_text}"}],
    )
    return response.content[0].text.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", help="A JSON object with name/url/description/categories/outbound_url/logo_url")
    parser.add_argument("--name")
    parser.add_argument("--url", help="Tool's own homepage, used to auto-write the description if --description is omitted")
    parser.add_argument("--description")
    parser.add_argument("--category", action="append", default=[], help="Repeatable")
    parser.add_argument("--outbound-url", help="Defaults to --url if omitted")
    parser.add_argument("--logo-url")
    args = parser.parse_args()

    if args.json:
        data = json.loads(args.json)
    else:
        if not args.name:
            parser.error("--name is required (or pass --json)")
        data = {
            "name": args.name,
            "url": args.url,
            "description": args.description,
            "categories": args.category,
            "outbound_url": args.outbound_url or args.url,
            "logo_url": args.logo_url,
        }

    settings = Settings()
    settings.validate()
    wp = WPClient(settings)

    if not data.get("description"):
        if not data.get("url"):
            raise SystemExit("Need either --description or --url (to auto-generate one)")
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        homepage_text = fetch_homepage_text(data["url"])
        data["description"] = generate_description(client, settings, data["name"], homepage_text)
        print(f"Generated description: {data['description']}")

    slug = slugify(data["name"])
    category_ids = [wp.get_or_create_term("tool_category", c) for c in data.get("categories", [])]

    body = {
        "title": data["name"],
        "slug": slug,
        "content": f"<p>{data['description']}</p>",
        "status": "publish",
        "tool_category": category_ids,
        "acf": {
            "outbound_url": data.get("outbound_url") or data.get("url") or "",
            "logo_url": data.get("logo_url") or "",
            "cta_label": "Get it",
        },
    }

    existing = wp.find_by_slug("tool", slug)
    result = wp.update("tool", existing["id"], body) if existing else wp.create("tool", body)
    action = "Updated" if existing else "Created"
    print(f"{action} tool '{data['name']}' -> {settings.wp_base_url}/tools/{slug}/ (id {result['id']})")


if __name__ == "__main__":
    main()

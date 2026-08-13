"""Find blog posts that mention a tool with a tracked affiliate link
(data/affiliate_links.json) but don't yet link to it, and link the first
mention.

Deliberately conservative: only touches the first plain-text occurrence of
the tool's name per post, skips text that's already inside a link, and
skips a post entirely if the tracked URL already appears anywhere in it
(so it never double-links or fights with an editor's manual placement).

Usage:
    python3 automation/affiliate_link_sweep.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString

from config import Settings
from wp_client import WPClient

ROOT = Path(__file__).resolve().parent.parent
AFFILIATE_LINKS = ROOT / "data" / "affiliate_links.json"


def load_affiliate_links() -> dict[str, str]:
    return json.loads(AFFILIATE_LINKS.read_text(encoding="utf-8")).get("links", {})


def link_first_mention(html: str, tool_name: str, url: str) -> str | None:
    """Return updated HTML with the first plain-text mention of tool_name
    linked to url, or None if no eligible mention was found."""
    if url in html:
        return None  # already linked somewhere in this post

    soup = BeautifulSoup(html, "html.parser")
    pattern = re.compile(rf"\b{re.escape(tool_name)}\b")

    for node in soup.find_all(string=True):
        if node.find_parent("a"):
            continue
        match = pattern.search(str(node))
        if not match:
            continue

        before, matched, after = node[: match.start()], match.group(0), node[match.end() :]
        anchor = soup.new_tag("a", href=url, rel="nofollow sponsored noopener", target="_blank")
        anchor.string = matched

        # bs4 >= 4.9 lets replace_with() take multiple replacement nodes,
        # splicing them in as siblings in order.
        node.replace_with(NavigableString(before), anchor, NavigableString(after))
        return str(soup)

    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Report what would change without writing to WordPress")
    args = parser.parse_args()

    settings = Settings()
    settings.validate()
    wp = WPClient(settings)

    links = load_affiliate_links()
    posts = wp.list_all("posts", status="publish")

    updated_count = 0
    for post in posts:
        content = post["content"]["rendered"]
        changed = False
        for tool_name, url in links.items():
            new_content = link_first_mention(content, tool_name, url)
            if new_content:
                content = new_content
                changed = True
                print(f"post '{post['title']['rendered']}' (id {post['id']}): linked first mention of {tool_name}")

        if changed:
            updated_count += 1
            if not args.dry_run:
                wp.update("posts", post["id"], {"content": content})

    suffix = " (dry run, nothing written)" if args.dry_run else ""
    print(f"\n{updated_count} post(s) updated{suffix}.")


if __name__ == "__main__":
    main()

"""Generate the 301 redirect map for paths that don't carry over as-is.

Blog posts, tool pages, and news posts keep identical slugs/paths on the
new site (see theme/functions.php's CPT rewrite rules), so almost nothing
needs a redirect -- this only covers pages that were intentionally dropped
during the rebuild (see the plan: /home-clone was a duplicate; /devtools
and /nocode were never published so were never in the live sitemap and
need nothing).

Outputs data/redirects.csv in the format the free "Redirection" plugin
accepts via its Tools -> Redirection -> Import (CSV) screen -- a couple of
manual clicks in wp-admin, rather than depending on an undocumented REST
endpoint for a one-time, three-row import.

Run with: python3 migration/redirects.py
"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# (source path, target path) -- paths only, not full URLs, since Redirection
# matches against the site's own domain regardless of environment (staging
# vs. production).
REDIRECTS: list[tuple[str, str]] = [
    ("/home-clone/", "/"),
]


def main() -> None:
    out_path = DATA / "redirects.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["source", "target"])
        writer.writerows(REDIRECTS)
    print(f"Wrote {len(REDIRECTS)} redirect(s) to {out_path}")


if __name__ == "__main__":
    main()

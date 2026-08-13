"""Small WordPress REST API client shared by the ongoing automation scripts
(generate_blog_post.py, seo_audit.py, add_tool.py, affiliate_link_sweep.py).

Not shared with migration/push_to_wp.py -- that script is a one-time bulk
importer with different needs (upserting a large pre-built payload) and has
its own lifecycle separate from this ongoing-automation package.
"""

from __future__ import annotations

import requests

from config import Settings


class WPClient:
    def __init__(self, settings: Settings):
        settings.validate()
        self.base_url = settings.wp_base_url
        self.session = requests.Session()
        self.session.auth = (settings.wp_app_user, settings.wp_app_password)
        self.session.headers.update({"User-Agent": "bizbot-site-automation/1.0"})

    def _url(self, endpoint: str) -> str:
        return f"{self.base_url}/wp-json/wp/v2/{endpoint}"

    def list_all(self, endpoint: str, **params) -> list[dict]:
        results = []
        page = 1
        while True:
            resp = self.session.get(self._url(endpoint), params={**params, "page": page, "per_page": 100}, timeout=30)
            if resp.status_code == 400 and page > 1:
                break  # WP returns 400 "invalid page number" past the last page
            resp.raise_for_status()
            batch = resp.json()
            if not batch:
                break
            results.extend(batch)
            page += 1
        return results

    def find_by_slug(self, endpoint: str, slug: str) -> dict | None:
        resp = self.session.get(
            self._url(endpoint),
            params={"slug": slug, "status": "publish,draft,pending,future"},
            timeout=20,
        )
        resp.raise_for_status()
        results = resp.json()
        return results[0] if results else None

    def create(self, endpoint: str, body: dict) -> dict:
        resp = self.session.post(self._url(endpoint), json=body, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def update(self, endpoint: str, item_id: int, body: dict) -> dict:
        resp = self.session.post(f"{self._url(endpoint)}/{item_id}", json=body, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_or_create_term(self, taxonomy: str, name: str) -> int:
        resp = self.session.get(self._url(taxonomy), params={"search": name, "per_page": 100}, timeout=20)
        resp.raise_for_status()
        for term in resp.json():
            if term["name"].strip().lower() == name.strip().lower():
                return term["id"]
        resp = self.session.post(self._url(taxonomy), json={"name": name}, timeout=20)
        resp.raise_for_status()
        return resp.json()["id"]

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    wp_base_url: str = field(default_factory=lambda: os.environ.get("WP_BASE_URL", "").rstrip("/"))
    wp_app_user: str = field(default_factory=lambda: os.environ.get("WP_APP_USER", ""))
    wp_app_password: str = field(default_factory=lambda: os.environ.get("WP_APP_PASSWORD", ""))

    anthropic_api_key: str = field(default_factory=lambda: os.environ.get("ANTHROPIC_API_KEY", ""))
    anthropic_model: str = field(default_factory=lambda: os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5"))

    def validate(self) -> None:
        missing = [
            name
            for name, val in (
                ("WP_BASE_URL", self.wp_base_url),
                ("WP_APP_USER", self.wp_app_user),
                ("WP_APP_PASSWORD", self.wp_app_password),
                ("ANTHROPIC_API_KEY", self.anthropic_api_key),
            )
            if not val
        ]
        if missing:
            raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")

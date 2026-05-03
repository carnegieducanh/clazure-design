from __future__ import annotations

from .built_in import TEMPLATES


def get_all() -> list[dict]:
    return TEMPLATES


def get_by_id(template_id: str) -> dict | None:
    return next((t for t in TEMPLATES if t["id"] == template_id), None)

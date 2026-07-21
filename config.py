"""Small, offline-friendly configuration helpers for the welcome plugin."""

from __future__ import annotations

import os
from pathlib import Path


def parse_image_paths(value: str | None) -> list[Path]:
    """Parse a comma-separated image path setting.

    The default is intentionally empty: a deployment must opt in to local
    images instead of inheriting a machine-specific absolute path.
    """

    raw_value = os.getenv("AMIA_WELCOME_IMAGES", "") if value is None else value
    return [
        Path(item.strip())
        for item in raw_value.split(",")
        if item.strip()
    ]


def parse_probability(value: str | None, default: float = 0.0) -> float:
    """Return a bounded image probability without raising at import time."""

    raw_value = os.getenv("AMIA_WELCOME_IMAGE_PROBABILITY") if value is None else value
    if raw_value in (None, ""):
        return default
    try:
        return min(1.0, max(0.0, float(raw_value)))
    except (TypeError, ValueError):
        return default


WELCOME_IMAGES = parse_image_paths(None)
IMAGE_PROBABILITY = parse_probability(None)

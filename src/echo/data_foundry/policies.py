"""License/use classification for the MK1 Foundry.

This module encodes project governance, not legal advice.  The JSON policy is
still the audit artifact; the defaults here make the core independently
executable and are covered by tests.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .contracts import UseDecision


ALIASES = {
    "CC0": "CC0",
    "CC0-1.0": "CC0-1.0",
    "CC BY": "CC-BY",
    "CC-BY": "CC-BY",
    "CC BY 4.0": "CC-BY-4.0",
    "CC-BY-4.0": "CC-BY-4.0",
    "CC BY-SA 4.0": "CC-BY-SA-4.0",
    "CC-BY-SA-4.0": "CC-BY-SA-4.0",
    "CC BY-NC": "CC-BY-NC",
    "CC-BY-NC": "CC-BY-NC",
    "CC BY-NC 3.0": "CC-BY-NC-3.0",
    "CC-BY-NC-3.0": "CC-BY-NC-3.0",
    "CC BY-NC 4.0": "CC-BY-NC-4.0",
    "CC-BY-NC-4.0": "CC-BY-NC-4.0",
    "CC SAMPLING+": "CC-SAMPLING+",
    "CC-SAMPLING+": "CC-SAMPLING+",
    "PUBLIC DOMAIN": "PUBLIC-DOMAIN",
    "PUBLIC-DOMAIN": "PUBLIC-DOMAIN",
}


DEFAULT_DECISIONS: dict[str, dict[str, str]] = {
    "CC0": {"release_safe": "ALLOW_RELEASE_SAFE", "research_extended": "ALLOW_RELEASE_SAFE"},
    "CC0-1.0": {"release_safe": "ALLOW_RELEASE_SAFE", "research_extended": "ALLOW_RELEASE_SAFE"},
    "PUBLIC-DOMAIN": {"release_safe": "ALLOW_RELEASE_SAFE", "research_extended": "ALLOW_RELEASE_SAFE"},
    "CC-BY": {"release_safe": "ALLOW_RELEASE_SAFE", "research_extended": "ALLOW_RELEASE_SAFE"},
    "CC-BY-4.0": {"release_safe": "ALLOW_RELEASE_SAFE", "research_extended": "ALLOW_RELEASE_SAFE"},
    "CC-BY-SA-4.0": {"release_safe": "REVIEW_REQUIRED", "research_extended": "ALLOW_RESEARCH_ONLY"},
    "CC-BY-NC": {"release_safe": "RESEARCH_ONLY", "research_extended": "ALLOW_RESEARCH_ONLY"},
    "CC-BY-NC-3.0": {"release_safe": "RESEARCH_ONLY", "research_extended": "ALLOW_RESEARCH_ONLY"},
    "CC-BY-NC-4.0": {"release_safe": "RESEARCH_ONLY", "research_extended": "ALLOW_RESEARCH_ONLY"},
    "CC-SAMPLING+": {"release_safe": "REVIEW_REQUIRED", "research_extended": "REVIEW_REQUIRED"},
    "UNKNOWN": {"release_safe": "QUARANTINE", "research_extended": "QUARANTINE"},
    "CUSTOM": {"release_safe": "REVIEW_REQUIRED", "research_extended": "REVIEW_REQUIRED"},
    "DENIED": {"release_safe": "DENY", "research_extended": "DENY"},
}


def normalize_license_id(value: str | None) -> str:
    if value is None or not str(value).strip():
        return "UNKNOWN"
    raw = " ".join(str(value).strip().upper().replace("_", " ").split())
    # Use a second lookup that is case-insensitive without weakening explicit policy.
    for alias, canonical in ALIASES.items():
        if raw == alias.upper():
            return canonical
    return str(value).strip()


def classify_license(
    license_id: str | None,
    profile: str = "release_safe",
    decisions: Mapping[str, Mapping[str, Any]] | None = None,
) -> UseDecision:
    table = decisions or DEFAULT_DECISIONS
    canonical = normalize_license_id(license_id)
    row = table.get(canonical)
    if row is None:
        return UseDecision.QUARANTINE
    value = row.get(profile)
    if value is None:
        return UseDecision.QUARANTINE
    return UseDecision(str(value))


def load_policy(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if payload.get("schema_version") != "echo.license-policy.v1":
        raise ValueError("unsupported license policy schema")
    if not isinstance(payload.get("decisions"), dict):
        raise ValueError("license policy must contain decisions object")
    return payload

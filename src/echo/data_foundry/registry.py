"""Source-registry loading and structural validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


REQUIRED_SOURCE_KEYS = {
    "source_id",
    "name",
    "release",
    "role",
    "license_model",
    "default_profile",
    "target_coverage",
}


def load_source_registry(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    validate_source_registry(payload)
    return payload


def validate_source_registry(payload: Mapping[str, Any]) -> None:
    if payload.get("schema_version") != "echo.source-registry.v1":
        raise ValueError("unsupported source registry schema")
    sources = payload.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("source registry requires a non-empty sources list")

    seen: set[str] = set()
    for index, source in enumerate(sources):
        if not isinstance(source, Mapping):
            raise ValueError(f"source entry {index} must be an object")
        missing = REQUIRED_SOURCE_KEYS - set(source)
        if missing:
            raise ValueError(f"source entry {index} missing keys: {sorted(missing)}")
        source_id = str(source["source_id"]).strip()
        if not source_id:
            raise ValueError(f"source entry {index} has empty source_id")
        if source_id in seen:
            raise ValueError(f"duplicate source_id: {source_id}")
        seen.add(source_id)
        if not isinstance(source.get("role"), list) or not source["role"]:
            raise ValueError(f"source {source_id} requires at least one role")
        if not isinstance(source.get("target_coverage"), Mapping):
            raise ValueError(f"source {source_id} target_coverage must be an object")
        if source_id != "echo-field-v1" and not source.get("canonical_url"):
            raise ValueError(f"source {source_id} requires canonical_url")


def index_sources(payload: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    validate_source_registry(payload)
    return {str(source["source_id"]): source for source in payload["sources"]}

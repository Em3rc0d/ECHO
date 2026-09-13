"""Dataset-source certification policy for ECHO Data Foundry.

This is a source-level stop-line policy. It complements per-asset licensing and
never turns source/release evidence into a claim that a concrete corpus has
already been acquired or validated.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping


_ALLOWED_PROFILE_STATES = {
    "ALLOW",
    "CONDITIONAL",
    "DENY",
    "REFERENCE_ONLY",
    "EXTERNAL_GATE",
}

_CERTIFIED_RELEASE_EVIDENCE_STATES = {
    "SOURCE_RELEASE_EVIDENCE_CERTIFIED",
}


def _normalize_release(value: object) -> str:
    text = str(value or "").strip().casefold()
    if text.startswith("v") and len(text) > 1 and text[1].isdigit():
        text = text[1:]
    return text


def load_dataset_certification(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if payload.get("schema_version") != "echo.dataset-certification.v1":
        raise ValueError("unsupported dataset certification schema")
    sources = payload.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("dataset certification requires a non-empty sources object")
    for source_id, row in sources.items():
        if not isinstance(row, Mapping):
            raise ValueError(f"dataset certification row must be an object: {source_id}")
        profiles = row.get("profiles")
        if not isinstance(profiles, Mapping) or not profiles:
            raise ValueError(f"dataset certification profiles missing: {source_id}")
        if not str(row.get("release") or "").strip():
            raise ValueError(f"dataset certification release missing: {source_id}")
        if not str(row.get("source_release_status") or "").strip():
            raise ValueError(f"dataset certification release evidence status missing: {source_id}")
        for profile, state in profiles.items():
            if str(state) not in _ALLOWED_PROFILE_STATES:
                raise ValueError(
                    f"unsupported source profile state {state!r} for {source_id}:{profile}"
                )
    return payload


def source_profile_state(
    policy: Mapping[str, Any], *, source_id: str, profile: str
) -> str:
    sources = policy.get("sources", {})
    row = sources.get(source_id)
    if not isinstance(row, Mapping):
        return "DENY"
    profiles = row.get("profiles", {})
    if not isinstance(profiles, Mapping):
        return "DENY"
    return str(profiles.get(profile, "DENY"))


def assert_sources_allowed(
    source_ids: Iterable[str], *, profile: str, policy: Mapping[str, Any]
) -> None:
    failures: dict[str, str] = {}
    for source_id in sorted({str(value) for value in source_ids if str(value)}):
        state = source_profile_state(policy, source_id=source_id, profile=profile)
        if state != "ALLOW":
            failures[source_id] = state
    if failures:
        detail = ", ".join(f"{source_id}={state}" for source_id, state in failures.items())
        raise ValueError(
            f"source certification stop-line for profile {profile!r}: {detail}. "
            "Resolve source-level conditions before freezing this corpus profile."
        )


def assert_source_records_allowed(
    source_releases: Iterable[tuple[str, str]],
    *,
    profile: str,
    policy: Mapping[str, Any],
) -> None:
    """Require source profile permission, certified release evidence and pin match."""
    failures: list[str] = []
    sources = policy.get("sources", {})
    pairs = sorted({(str(source_id), str(release)) for source_id, release in source_releases})
    for source_id, actual_release in pairs:
        row = sources.get(source_id) if isinstance(sources, Mapping) else None
        if not isinstance(row, Mapping):
            failures.append(f"{source_id}=DENY_UNKNOWN_SOURCE")
            continue

        state = source_profile_state(policy, source_id=source_id, profile=profile)
        if state != "ALLOW":
            failures.append(f"{source_id}={state}")
            continue

        evidence_status = str(row.get("source_release_status") or "")
        if evidence_status not in _CERTIFIED_RELEASE_EVIDENCE_STATES:
            failures.append(f"{source_id}=RELEASE_EVIDENCE_NOT_CERTIFIED:{evidence_status or 'MISSING'}")
            continue

        expected_release = str(row.get("release") or "")
        if _normalize_release(actual_release) != _normalize_release(expected_release):
            failures.append(
                f"{source_id}=RELEASE_MISMATCH:actual={actual_release},expected={expected_release}"
            )

    if failures:
        raise ValueError(
            f"source/release certification stop-line for profile {profile!r}: "
            + "; ".join(failures)
        )


def source_policy_summary(policy: Mapping[str, Any], *, profile: str) -> dict[str, str]:
    sources = policy.get("sources", {})
    return {
        str(source_id): source_profile_state(policy, source_id=str(source_id), profile=profile)
        for source_id in sorted(sources)
    }

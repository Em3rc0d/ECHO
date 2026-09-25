#!/usr/bin/env python3
"""Fail closed if the frozen ECHO-MVP-001 dataset snapshot has drifted."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
MAT = ROOT / "MK1/mining-site/materialization"

LEDGER = MAT / "canonical-release-safe-asset-ledger.jsonl"
MANIFEST = MAT / "mvp-benchmark-manifest.jsonl"
SUMMARY = MAT / "mvp-benchmark-manifest-summary.json"
LOCATORS = MAT / "mvp-direct-media-locators.json"
SPLIT = MAT / "split-integrity.json"
COVERAGE = MAT / "coverage-gate.json"

TARGETS = ("GLASS_SHATTER", "SIREN", "VEHICLE_HORN")
SPLITS = ("train", "validation", "test")


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected JSON object")
    return value


def git_blob_sha1(path: Path) -> str:
    """Fallback Git-blob identity for non-repository execution."""
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()  # nosec B324 - Git object identity


def tracked_blob_sha1(path: Path) -> tuple[str, bool]:
    """Return the committed Git blob SHA and whether the worktree path is dirty.

    Using HEAD:<path> avoids false drift on Windows checkouts where Git may
    materialize LF-tracked text as CRLF bytes in the worktree.
    """
    relative = path.relative_to(ROOT).as_posix()

    try:
        dirty_probe = subprocess.run(
            ["git", "diff", "--quiet", "--", relative],
            cwd=ROOT,
            check=False,
        )
        dirty = dirty_probe.returncode != 0

        result = subprocess.run(
            ["git", "rev-parse", f"HEAD:{relative}"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip(), dirty
    except (FileNotFoundError, subprocess.CalledProcessError):
        return git_blob_sha1(path), False


def line_count(path: Path) -> int:
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def main() -> int:
    summary = load(SUMMARY)
    locators = load(LOCATORS)
    split = load(SPLIT)
    coverage = load(COVERAGE)

    gaps: list[str] = []

    current_ledger_blob, ledger_dirty = tracked_blob_sha1(LEDGER)
    expected_ledger_blob = str(summary.get("ledger_blob_sha") or "")
    if ledger_dirty:
        gaps.append("LEDGER_WORKTREE_MODIFIED")
    if current_ledger_blob != expected_ledger_blob:
        gaps.append(
            f"LEDGER_BLOB_DRIFT:{current_ledger_blob}!={expected_ledger_blob}"
        )

    current_manifest_blob, manifest_dirty = tracked_blob_sha1(MANIFEST)
    expected_manifest_blob = str(locators.get("manifest_blob_sha") or "")
    if manifest_dirty:
        gaps.append("MANIFEST_WORKTREE_MODIFIED")
    if current_manifest_blob != expected_manifest_blob:
        gaps.append(
            f"MANIFEST_BLOB_DRIFT:{current_manifest_blob}!={expected_manifest_blob}"
        )

    rows = line_count(MANIFEST)
    expected_rows = int(summary.get("row_count", -1))
    if rows != expected_rows:
        gaps.append(f"MANIFEST_ROW_COUNT_DRIFT:{rows}!={expected_rows}")

    locator_count = int(locators.get("locator_count", -1))
    if locator_count != 428:
        gaps.append(f"DIRECT_LOCATOR_COUNT_DRIFT:{locator_count}!=428")

    split_identity = str(split.get("assignment_sha256") or "")
    expected_split_identity = str(summary.get("split_assignment_sha256") or "")
    if split_identity != expected_split_identity:
        gaps.append(
            f"SPLIT_ASSIGNMENT_DRIFT:{split_identity}!={expected_split_identity}"
        )

    classes = coverage.get("classes") or {}
    frozen_counts = summary.get("positive_counts_by_split") or {}
    for split_name in SPLITS:
        frozen_row = frozen_counts.get(split_name) or {}
        for target in TARGETS:
            actual = int(
                (classes.get(target) or {})
                .get("split_assets", {})
                .get(split_name, 0)
                or 0
            )
            expected = int(frozen_row.get(target, -1))
            if actual != expected:
                gaps.append(
                    f"{target}_{split_name.upper()}_COUNT_DRIFT:{actual}!={expected}"
                )

    status = "PASS" if not gaps else "FAIL"
    print(
        json.dumps(
            {
                "schema_version": "echo.mvp-frozen-snapshot-check.v1",
                "profile_id": "ECHO-MVP-001",
                "status": status,
                "ledger_blob_sha": current_ledger_blob,
                "manifest_blob_sha": current_manifest_blob,
                "split_assignment_sha256": split_identity,
                "manifest_rows": rows,
                "direct_locator_count": locator_count,
                "gap_codes": gaps,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not gaps else 3


if __name__ == "__main__":
    raise SystemExit(main())

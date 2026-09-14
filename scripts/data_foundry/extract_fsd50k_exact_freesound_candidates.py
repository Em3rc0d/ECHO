#!/usr/bin/env python3
"""Derive exact-positive and governed hard-negative Freesound IDs from FSD50K.

No FSD50K audio is downloaded. The official checksum-pinned ground-truth ZIP
is used only as label provenance. Media/rights are re-resolved from the current
Freesound page later, under the zero-cost per-asset path.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
import hashlib
import io
import json
from pathlib import Path
import shutil
import time
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "configs/data_foundry/acquisition_registry.v1.json"
HARD_NEGATIVE_POLICY = ROOT / "configs/data_foundry/hard_negative_mapping.v1.json"
SOURCE_ID = "fsd50k-1.0"
USER_AGENT = "ECHO-Data-Foundry/1.0 (+https://github.com/Em3rc0d/ECHO)"
TARGET_ORDER = ("GLASS_SHATTER", "SIREN", "FIRE_ALARM", "VEHICLE_HORN", "TIRE_SQUEAL")


def digest(path: Path, algo: str) -> str:
    h = hashlib.new(algo)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def publisher_url(record_url: str, filename: str) -> str:
    record_id = urlparse(record_url).path.rstrip("/").split("/")[-1]
    return f"https://zenodo.org/api/records/{record_id}/files/{quote(filename, safe='')}/content"


def download(url: str, target: Path, attempts: int = 5) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(request, timeout=180) as response, target.open("wb") as out:  # nosec B310 - pinned public publisher URL
                shutil.copyfileobj(response, out, length=1024 * 1024)
            return
        except Exception as exc:
            last = exc
            target.unlink(missing_ok=True)
            if attempt < attempts:
                time.sleep(min(20, 2 ** attempt))
    raise RuntimeError(f"download failed: {url}: {last}") from last


def target_labels(labels: set[str]) -> list[str]:
    targets = []
    if "Siren" in labels:
        targets.append("SIREN")
    if "Vehicle_horn_and_car_horn_and_honking" in labels:
        targets.append("VEHICLE_HORN")
    # Generic Shatter is too broad. ECHO requires explicit glass evidence.
    if "Shatter" in labels and "Glass" in labels:
        targets.append("GLASS_SHATTER")
    return targets


def hard_negative_roles(
    labels: set[str],
    *,
    positives: set[str],
    policy: dict,
    accepted_per_source_label: Counter[tuple[str, str]],
) -> tuple[list[str], dict[str, list[str]]]:
    """Select deterministic hard-negative roles without semantic relabeling.

    Each target/source-label pair is bounded by the frozen policy. A recording
    can be a hard negative for a target only if one of that target's explicit
    confuser labels is present, none of its exclusion labels are present, and
    the same recording is not a positive for that target.
    """
    max_per_label = int(policy.get("max_candidates_per_source_label") or 0)
    if max_per_label <= 0:
        raise ValueError("hard-negative policy max_candidates_per_source_label must be positive")

    roles: list[str] = []
    matched_by_target: dict[str, list[str]] = {}
    for target in TARGET_ORDER:
        cfg = (policy.get("targets") or {}).get(target) or {}
        if target in positives:
            continue
        excluded = {str(value) for value in cfg.get("exclude_if_labels_include") or []}
        if labels & excluded:
            continue
        matched = []
        for source_label in cfg.get("source_labels") or []:
            source_label = str(source_label)
            if source_label not in labels:
                continue
            key = (target, source_label)
            if accepted_per_source_label[key] >= max_per_label:
                continue
            matched.append(source_label)
        if not matched:
            continue
        # Debit all matched labels that still had capacity. This prevents a
        # highly multi-labelled clip from silently bypassing the per-label cap.
        for source_label in matched:
            accepted_per_source_label[(target, source_label)] += 1
        roles.append(target)
        matched_by_target[target] = sorted(matched)
    return roles, matched_by_target


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    hn_policy = json.loads(HARD_NEGATIVE_POLICY.read_text(encoding="utf-8"))
    source = registry["sources"][SOURCE_ID]
    entry = next(row for row in source["files"] if row["name"] == "FSD50K.ground_truth.zip")
    work = Path(args.work_root)
    work.mkdir(parents=True, exist_ok=True)
    archive = work / entry["name"]
    download(publisher_url(source["record_url"], entry["name"]), archive)
    actual_md5 = digest(archive, "md5")
    if actual_md5.casefold() != str(entry["md5"]).casefold():
        raise SystemExit(f"publisher MD5 mismatch: {actual_md5} != {entry['md5']}")

    candidates: dict[str, dict] = {}
    split_counts: dict[str, dict[str, int]] = {}
    hard_negative_split_counts: dict[str, Counter[str]] = defaultdict(Counter)
    accepted_per_source_label: Counter[tuple[str, str]] = Counter()

    with zipfile.ZipFile(archive) as zf:
        for member in ("FSD50K.ground_truth/dev.csv", "FSD50K.ground_truth/eval.csv"):
            raw = zf.read(member)
            reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
            for row in reader:
                labels = {value.strip() for value in str(row.get("labels") or "").split(",") if value.strip()}
                positives = set(target_labels(labels))
                hard_negatives, hard_negative_labels = hard_negative_roles(
                    labels,
                    positives=positives,
                    policy=hn_policy,
                    accepted_per_source_label=accepted_per_source_label,
                )
                if not positives and not hard_negatives:
                    continue

                sound_id = str(row["fname"]).strip()
                split = str(row.get("split") or ("eval" if member.endswith("eval.csv") else "unknown"))
                item = candidates.setdefault(sound_id, {
                    "sound_id": int(sound_id),
                    "freesound_page": f"https://freesound.org/s/{sound_id}/",
                    "targets": [],
                    "hard_negative_for": [],
                    "hard_negative_source_labels_by_target": {},
                    "fsd50k_labels": sorted(labels),
                    "fsd50k_mids": [value.strip() for value in str(row.get("mids") or "").split(",") if value.strip()],
                    "fsd50k_split": split,
                    "label_provenance": f"FSD50K v1.0 {member}",
                    "semantic_policy": "Exact positives remain narrow; hard negatives use MK1-HARD-NEGATIVE-MAPPING-001 and are never relabeled as positives.",
                })
                item["targets"] = sorted(set(item["targets"]) | positives)
                item["hard_negative_for"] = sorted(set(item["hard_negative_for"]) | set(hard_negatives))
                for target, matched in hard_negative_labels.items():
                    existing = set(item["hard_negative_source_labels_by_target"].get(target) or [])
                    item["hard_negative_source_labels_by_target"][target] = sorted(existing | set(matched))
                for target in positives:
                    split_counts.setdefault(target, {})[split] = split_counts.setdefault(target, {}).get(split, 0) + 1
                for target in hard_negatives:
                    hard_negative_split_counts[target][split] += 1

    by_target = {
        target: sorted(int(sound_id) for sound_id, row in candidates.items() if target in row["targets"])
        for target in TARGET_ORDER
    }
    by_hard_negative_target = {
        target: sorted(int(sound_id) for sound_id, row in candidates.items() if target in row["hard_negative_for"])
        for target in TARGET_ORDER
    }
    payload = {
        "schema_version": "echo.fsd50k-exact-and-hard-negative-freesound-candidates.v2",
        "status": "PASS",
        "source_evidence": {
            "dataset": "FSD50K",
            "release": "1.0",
            "ground_truth_zip_publisher_md5": entry["md5"],
            "ground_truth_zip_actual_md5": actual_md5,
            "ground_truth_zip_sha256": digest(archive, "sha256"),
            "hard_negative_policy": "MK1-HARD-NEGATIVE-MAPPING-001",
            "hard_negative_policy_sha256": digest(HARD_NEGATIVE_POLICY, "sha256"),
        },
        "candidate_count": len(candidates),
        "target_candidate_counts": {target: len(ids) for target, ids in by_target.items()},
        "hard_negative_candidate_counts": {target: len(ids) for target, ids in by_hard_negative_target.items()},
        "target_split_counts": split_counts,
        "hard_negative_split_counts": {target: dict(sorted(counts.items())) for target, counts in sorted(hard_negative_split_counts.items())},
        "hard_negative_source_label_usage": {
            f"{target}:{label}": count
            for (target, label), count in sorted(accepted_per_source_label.items())
        },
        "by_target_sound_ids": by_target,
        "by_hard_negative_target_sound_ids": by_hard_negative_target,
        "candidates": sorted(candidates.values(), key=lambda row: row["sound_id"]),
        "admission_boundary": "Label provenance only. Candidate media must be independently re-acquired from Freesound, current per-asset rights must be release-safe, bytes must be hashed/probed/fingerprinted, and global grouping/dedup/split/coverage gates still apply.",
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "candidate_count": len(candidates),
        "target_counts": payload["target_candidate_counts"],
        "hard_negative_counts": payload["hard_negative_candidate_counts"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

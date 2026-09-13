#!/usr/bin/env python3
"""Derive semantically exact Freesound candidate IDs from FSD50K ground truth.

No FSD50K audio is downloaded. The official, checksum-pinned ground-truth ZIP
is used only as label provenance. Media/rights are re-resolved from the current
Freesound page later, under the free-tier per-asset path.
"""

from __future__ import annotations

import csv
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
SOURCE_ID = "fsd50k-1.0"
USER_AGENT = "ECHO-Data-Foundry/1.0 (+https://github.com/Em3rc0d/ECHO)"


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
    # ECHO does not accept generic Shatter alone. Requiring both ontology labels
    # narrows FSD50K candidates to explicit glass-shatter semantics.
    if "Shatter" in labels and "Glass" in labels:
        targets.append("GLASS_SHATTER")
    return targets


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
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
    with zipfile.ZipFile(archive) as zf:
        for member in ("FSD50K.ground_truth/dev.csv", "FSD50K.ground_truth/eval.csv"):
            raw = zf.read(member)
            reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
            for row in reader:
                labels = {value.strip() for value in str(row.get("labels") or "").split(",") if value.strip()}
                targets = target_labels(labels)
                if not targets:
                    continue
                sound_id = str(row["fname"]).strip()
                split = str(row.get("split") or ("eval" if member.endswith("eval.csv") else "unknown"))
                item = candidates.setdefault(sound_id, {
                    "sound_id": int(sound_id),
                    "freesound_page": f"https://freesound.org/s/{sound_id}/",
                    "targets": [],
                    "fsd50k_labels": sorted(labels),
                    "fsd50k_mids": [value.strip() for value in str(row.get("mids") or "").split(",") if value.strip()],
                    "fsd50k_split": split,
                    "label_provenance": f"FSD50K v1.0 {member}",
                    "semantic_policy": "SIREN/HORN require exact ontology label; GLASS_SHATTER requires Shatter+Glass co-label.",
                })
                item["targets"] = sorted(set(item["targets"]) | set(targets))
                for target in targets:
                    split_counts.setdefault(target, {})[split] = split_counts.setdefault(target, {}).get(split, 0) + 1

    by_target = {
        target: sorted(int(sound_id) for sound_id, row in candidates.items() if target in row["targets"])
        for target in ("GLASS_SHATTER", "SIREN", "VEHICLE_HORN")
    }
    payload = {
        "schema_version": "echo.fsd50k-exact-freesound-candidates.v1",
        "status": "PASS",
        "source_evidence": {
            "dataset": "FSD50K",
            "release": "1.0",
            "ground_truth_zip_publisher_md5": entry["md5"],
            "ground_truth_zip_actual_md5": actual_md5,
            "ground_truth_zip_sha256": digest(archive, "sha256"),
        },
        "candidate_count": len(candidates),
        "target_candidate_counts": {target: len(ids) for target, ids in by_target.items()},
        "target_split_counts": split_counts,
        "by_target_sound_ids": by_target,
        "candidates": sorted(candidates.values(), key=lambda row: row["sound_id"]),
        "admission_boundary": "Label provenance only. Candidate media must be independently re-acquired from Freesound, current per-asset rights must be release-safe, bytes must be hashed/probed, and global grouping/dedup/split/coverage gates still apply.",
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "candidate_count": len(candidates), "target_counts": payload["target_candidate_counts"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

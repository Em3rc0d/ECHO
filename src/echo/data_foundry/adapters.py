"""Metadata adapters for public ECHO MK1 dataset candidates.

Adapters only normalize upstream metadata into RawAssetCandidate. They do not
make final admission, license or semantic decisions.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Mapping

from .contracts import RawAssetCandidate


def _load_fsd_vocabulary(path: str | Path | None) -> dict[str, str]:
    if path is None:
        return {}
    mapping: dict[str, str] = {}
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            mid = str(row.get("mid") or row.get("mids") or "").strip()
            label = str(row.get("display_name") or row.get("label") or row.get("name") or "").strip()
            if mid and label:
                mapping[mid] = label
    return mapping


def parse_esc50_metadata(csv_path: str | Path, *, audio_root: str | Path | None = None) -> list[RawAssetCandidate]:
    rows: list[RawAssetCandidate] = []
    with Path(csv_path).open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            filename = str(row.get("filename") or "").strip()
            if not filename:
                continue
            src_file = str(row.get("src_file") or filename).strip()
            local = str(Path(audio_root) / filename) if audio_root else filename
            rows.append(RawAssetCandidate(
                source_dataset="esc50",
                source_release="official",
                source_asset_id=filename,
                local_relpath=local,
                license_id="CC-BY-NC",
                original_labels=(str(row.get("category") or "").strip(),),
                label_provenance="source_ground_truth",
                recording_group_id=f"esc50:{src_file}",
                uploader_or_source_id=src_file,
                original_split=str(row.get("fold") or "").strip() or None,
                extra={"take": row.get("take"), "target": row.get("target"), "esc10": row.get("esc10")},
            ))
    return rows


def parse_urbansound8k_metadata(csv_path: str | Path, *, audio_root: str | Path | None = None) -> list[RawAssetCandidate]:
    rows: list[RawAssetCandidate] = []
    with Path(csv_path).open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            filename = str(row.get("slice_file_name") or "").strip()
            if not filename:
                continue
            fsid = str(row.get("fsID") or "unknown").strip()
            occurrence = str(row.get("occurrenceID") or "unknown").strip()
            fold = str(row.get("fold") or "").strip()
            local = str(Path(audio_root) / f"fold{fold}" / filename) if audio_root else filename
            duration = None
            try:
                if row.get("start") not in (None, "") and row.get("end") not in (None, ""):
                    duration = float(row["end"]) - float(row["start"])
            except (ValueError, TypeError):
                duration = None
            rows.append(RawAssetCandidate(
                source_dataset="urbansound8k-1.0",
                source_release="1.0",
                source_asset_id=filename,
                local_relpath=local,
                license_id="CC-BY-NC-3.0",
                original_labels=(str(row.get("class") or "").strip(),),
                label_provenance="source_ground_truth",
                recording_group_id=f"urbansound8k:{fsid}:{occurrence}",
                uploader_or_source_id=fsid,
                original_split=fold or None,
                duration_seconds=duration if duration and duration > 0 else None,
                extra={"salience": row.get("salience"), "classID": row.get("classID")},
            ))
    return rows


def parse_fsd50k_ground_truth(
    csv_path: str | Path,
    *,
    partition: str,
    vocabulary_csv: str | Path | None = None,
    clip_info_json: str | Path | None = None,
    audio_root: str | Path | None = None,
) -> list[RawAssetCandidate]:
    """Parse FSD50K using AudioSet MIDs to avoid ambiguity in display names.

    FSD50K ground truth exposes comma-separated MIDs; display names themselves
    can contain commas. Therefore ``vocabulary.csv`` is the preferred route
    to reconstruct labels rather than splitting the human-readable labels cell.
    """

    vocabulary = _load_fsd_vocabulary(vocabulary_csv)
    clip_info: Mapping[str, object] = {}
    if clip_info_json:
        with Path(clip_info_json).open("r", encoding="utf-8") as handle:
            loaded = json.load(handle)
        if isinstance(loaded, dict):
            clip_info = loaded

    rows: list[RawAssetCandidate] = []
    with Path(csv_path).open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            source_id = str(row.get("fname") or row.get("filename") or "").strip()
            if not source_id:
                continue
            mids = tuple(part.strip() for part in str(row.get("mids") or "").split(",") if part.strip())
            if vocabulary:
                labels = tuple(sorted({vocabulary[mid] for mid in mids if mid in vocabulary}))
            else:
                labels = mids
            info_raw = clip_info.get(source_id, {})
            info = info_raw if isinstance(info_raw, dict) else {}
            uploader = str(info.get("uploader_name") or info.get("uploader") or "").strip() or None
            license_id = str(info.get("license") or row.get("license") or "UNKNOWN").strip()
            group = f"fsd50k:uploader:{uploader}" if uploader else f"fsd50k:clip:{source_id}"
            filename = f"{source_id}.wav" if not source_id.lower().endswith(".wav") else source_id
            local = str(Path(audio_root) / filename) if audio_root else filename
            rows.append(RawAssetCandidate(
                source_dataset="fsd50k-1.0",
                source_release="1.0",
                source_asset_id=source_id,
                local_relpath=local,
                license_id=license_id,
                original_labels=labels,
                label_provenance="source_ground_truth",
                recording_group_id=group,
                uploader_or_source_id=uploader,
                original_split=str(row.get("split") or partition).strip() or partition,
                extra={"mids": mids, "source_clip_info": info},
            ))
    return rows


def _presence_label(column: str) -> str | None:
    if not column.endswith("_presence"):
        return None
    stem = column[: -len("_presence")]
    if "_" in stem:
        prefix, suffix = stem.split("_", 1)
        if "-" in prefix and suffix:
            return suffix
    return stem


def parse_sonyc_annotations(csv_path: str | Path, *, audio_root: str | Path | None = None) -> list[RawAssetCandidate]:
    aggregated: dict[str, dict[str, object]] = {}
    with Path(csv_path).open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            filename = str(row.get("audio_filename") or row.get("filename") or "").strip()
            if not filename:
                continue
            item = aggregated.setdefault(filename, {"labels": set(), "sensor_id": row.get("sensor_id"), "split": row.get("split")})
            labels = item["labels"]
            assert isinstance(labels, set)
            for key, value in row.items():
                label = _presence_label(str(key))
                try:
                    present = float(value or 0) > 0
                except (ValueError, TypeError):
                    present = False
                if label and present:
                    labels.add(label)

    result: list[RawAssetCandidate] = []
    for filename, item in sorted(aggregated.items()):
        sensor = str(item.get("sensor_id") or "unknown")
        labels = tuple(sorted(str(v) for v in item["labels"]))
        local = str(Path(audio_root) / filename) if audio_root else filename
        result.append(RawAssetCandidate(
            source_dataset="sonyc-ust-v2",
            source_release="2.3",
            source_asset_id=filename,
            local_relpath=local,
            license_id="CC-BY-4.0",
            original_labels=labels,
            label_provenance="source_annotations",
            recording_group_id=f"sonyc:{sensor}:{filename}",
            uploader_or_source_id=sensor,
            device_id=sensor,
            original_split=str(item.get("split") or "").strip() or None,
        ))
    return result


def parse_singapura(
    metadata_csv: str | Path,
    labels_dir: str | Path,
    *,
    audio_root: str | Path | None = None,
) -> list[RawAssetCandidate]:
    label_root = Path(labels_dir)
    result: list[RawAssetCandidate] = []
    with Path(metadata_csv).open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            filename = str(row.get("filename") or row.get("audio_filename") or "").strip()
            if not filename:
                continue
            sensor = str(row.get("sensor_id") or row.get("sensor") or "unknown").strip()
            label_file = label_root / f"{Path(filename).stem}.csv"
            labels: set[str] = set()
            intervals: list[dict[str, object]] = []
            if label_file.exists():
                with label_file.open("r", encoding="utf-8-sig", newline="") as label_handle:
                    for event in csv.DictReader(label_handle):
                        label = str(event.get("event_label") or event.get("label") or "").strip()
                        if label:
                            labels.add(label)
                        intervals.append({"event_label": label, "onset": event.get("onset"), "offset": event.get("offset")})
            local = str(Path(audio_root) / filename) if audio_root else filename
            result.append(RawAssetCandidate(
                source_dataset="singapura-v1.0a",
                source_release="v1.0a",
                source_asset_id=filename,
                local_relpath=local,
                license_id="CC-BY-SA-4.0",
                original_labels=tuple(sorted(labels)),
                label_provenance="strong_source_annotations",
                recording_group_id=f"singapura:{sensor}:{filename}",
                uploader_or_source_id=sensor,
                device_id=sensor,
                extra={"strong_intervals": intervals},
            ))
    return result

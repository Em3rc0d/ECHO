"""Typed access to the frozen ECHO MVP benchmark manifest."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable, Mapping

MVP_TARGETS = ("GLASS_SHATTER", "SIREN", "VEHICLE_HORN")
VALID_SPLITS = {"train", "validation", "test"}


@dataclass(frozen=True)
class BenchmarkRow:
    asset_id: str
    split: str
    source_dataset: str
    recording_group_id: str
    media_sha256: str
    duration_seconds: float
    positive_labels: tuple[str, ...]
    explicit_negative_labels: tuple[str, ...]
    supervision: Mapping[str, int | None]
    origin_uri: str | None = None

    def __post_init__(self) -> None:
        if not self.asset_id:
            raise ValueError("asset_id is required")
        if self.split not in VALID_SPLITS:
            raise ValueError(f"unsupported benchmark split: {self.split}")
        if len(self.media_sha256) != 64:
            raise ValueError(f"invalid media_sha256 for {self.asset_id}")
        if set(self.positive_labels) - set(MVP_TARGETS):
            raise ValueError(f"unexpected positive label in {self.asset_id}")
        if set(self.explicit_negative_labels) - set(MVP_TARGETS):
            raise ValueError(f"unexpected explicit negative label in {self.asset_id}")

    @property
    def known_target_count(self) -> int:
        return sum(self.supervision.get(target) is not None for target in MVP_TARGETS)


def _row(payload: Mapping[str, object]) -> BenchmarkRow:
    raw_supervision = payload.get("supervision")
    if not isinstance(raw_supervision, Mapping):
        raise ValueError("benchmark row missing supervision object")
    supervision = {
        target: (
            None
            if raw_supervision.get(target) is None
            else int(raw_supervision.get(target))
        )
        for target in MVP_TARGETS
    }
    for target, value in supervision.items():
        if value not in {None, 0, 1}:
            raise ValueError(f"invalid supervision value for {target}: {value!r}")

    return BenchmarkRow(
        asset_id=str(payload.get("asset_id") or ""),
        split=str(payload.get("split") or ""),
        source_dataset=str(payload.get("source_dataset") or ""),
        recording_group_id=str(payload.get("recording_group_id") or ""),
        media_sha256=str(payload.get("media_sha256") or ""),
        duration_seconds=float(payload.get("duration_seconds") or 0.0),
        positive_labels=tuple(str(v) for v in (payload.get("positive_labels") or [])),
        explicit_negative_labels=tuple(
            str(v) for v in (payload.get("explicit_negative_labels") or [])
        ),
        supervision=supervision,
        origin_uri=(
            str(payload.get("origin_uri"))
            if payload.get("origin_uri") is not None
            else None
        ),
    )


def load_benchmark_manifest(path: str | Path) -> list[BenchmarkRow]:
    rows: list[BenchmarkRow] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, 1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON") from exc
            if not isinstance(payload, Mapping):
                raise ValueError(f"{path}:{line_no}: expected JSON object")
            row = _row(payload)
            if row.known_target_count == 0:
                raise ValueError(f"{path}:{line_no}: row has no known supervision")
            rows.append(row)
    if not rows:
        raise ValueError(f"{path}: benchmark manifest is empty")
    return rows


def by_split(rows: Iterable[BenchmarkRow]) -> dict[str, list[BenchmarkRow]]:
    result = {split: [] for split in sorted(VALID_SPLITS)}
    for row in rows:
        result[row.split].append(row)
    return result

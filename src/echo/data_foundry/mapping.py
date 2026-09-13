"""Semantic label mapping driven by the versioned Foundry registry."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from .contracts import MappingStatus, normalize_labels


@dataclass(frozen=True)
class MappingDecision:
    echo_labels: tuple[str, ...]
    status: MappingStatus
    review_required: bool
    matched_source_labels: tuple[str, ...]
    unmapped_source_labels: tuple[str, ...]
    uses: tuple[str, ...]
    confuses: tuple[str, ...]


class LabelMapper:
    def __init__(self, payload: Mapping[str, Any]) -> None:
        if payload.get("schema_version") != "echo.label-mapping.v1":
            raise ValueError("unsupported label mapping schema")
        self._sources = payload.get("sources", {})
        if not isinstance(self._sources, Mapping):
            raise ValueError("label mapping sources must be an object")

    @classmethod
    def from_json(cls, path: str | Path) -> "LabelMapper":
        with Path(path).open("r", encoding="utf-8") as handle:
            return cls(json.load(handle))

    def map_labels(self, source_id: str, labels: Iterable[str]) -> MappingDecision:
        source_table = self._sources.get(source_id, {})
        if not isinstance(source_table, Mapping):
            source_table = {}

        echo_labels: set[str] = set()
        matched: list[str] = []
        unmapped: list[str] = []
        statuses: list[MappingStatus] = []
        uses: set[str] = set()
        confuses: set[str] = set()
        review_required = False

        # Build case-insensitive index while keeping exact source spellings.
        index = {str(key).casefold(): (str(key), value) for key, value in source_table.items()}

        for raw_label in labels:
            label = str(raw_label).strip()
            if not label:
                continue
            entry_pair = index.get(label.casefold())
            if entry_pair is None:
                unmapped.append(label)
                continue
            _, entry = entry_pair
            matched.append(label)
            try:
                status = MappingStatus(str(entry.get("status", "UNUSABLE")))
            except ValueError:
                status = MappingStatus.UNUSABLE
            statuses.append(status)
            echo_labels.update(str(v) for v in entry.get("echo_labels", []))
            review_required = review_required or bool(entry.get("review_required", False))
            if entry.get("use"):
                uses.add(str(entry["use"]))
            confuses.update(str(v) for v in entry.get("confuses", []))

        if not statuses:
            overall = MappingStatus.UNUSABLE
        elif len(set(statuses)) == 1:
            overall = statuses[0]
        else:
            # A polyphonic clip can contain positive and negative/context labels.
            overall = MappingStatus.MIXED

        return MappingDecision(
            echo_labels=normalize_labels(echo_labels),
            status=overall,
            review_required=review_required,
            matched_source_labels=normalize_labels(matched),
            unmapped_source_labels=normalize_labels(unmapped),
            uses=normalize_labels(uses),
            confuses=normalize_labels(confuses),
        )

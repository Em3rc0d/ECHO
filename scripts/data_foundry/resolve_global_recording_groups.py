#!/usr/bin/env python3
"""Resolve leakage-safe recording groups from source groups + acoustic identity.

This step never merges or deletes acoustic content. It only strengthens the split
protection relation: existing source/curated groups are preserved, while exact or
near-duplicate acoustic relationships are unioned into deterministic global groups.
Fallback clip IDs with no detected acoustic relation become explicitly screened
singletons rather than silently claiming curated recording-family provenance.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from echo.data_foundry.canonical_fingerprints import fingerprint_distance
from echo.data_foundry.ledger import summarize_ledger, validate_ledger
from echo.data_foundry.source_policy import load_dataset_certification
from scripts.data_foundry.build_canonical_asset_ledger import recompute_stage

ROOT = Path(__file__).resolve().parents[2]
MAT = ROOT / "MK1/mining-site/materialization"
LEDGER = MAT / "canonical-release-safe-asset-ledger.jsonl"
SUMMARY = MAT / "canonical-release-safe-asset-ledger-summary.json"
NEAR_POLICY = ROOT / "configs/data_foundry/near_duplicate_policy.v1.json"
SOURCE_POLICY = ROOT / "configs/data_foundry/dataset_certification.v1.json"


class UnionFind:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))
        self.rank = [0] * size

    def find(self, value: int) -> int:
        while self.parent[value] != value:
            self.parent[value] = self.parent[self.parent[value]]
            value = self.parent[value]
        return value

    def union(self, left: int, right: int) -> None:
        a, b = self.find(left), self.find(right)
        if a == b:
            return
        if self.rank[a] < self.rank[b]:
            a, b = b, a
        self.parent[b] = a
        if self.rank[a] == self.rank[b]:
            self.rank[a] += 1


def _digest(values: list[str]) -> str:
    encoded = "\n".join(sorted(values)).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:20]


def _is_fallback(row: Mapping[str, Any]) -> bool:
    return (
        str(row.get("grouping_status") or "").upper().startswith("FALLBACK")
        or "GROUPING_GLOBAL_AUDIT_REQUIRED" in (row.get("blocking_reasons") or [])
    )


def resolve_groups(rows: list[dict[str, Any]], *, threshold: float) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = [dict(row) for row in rows]
    uf = UnionFind(len(rows))
    by_existing: dict[str, int] = {}
    by_media: dict[str, int] = {}
    by_pcm: dict[str, int] = {}

    for index, row in enumerate(rows):
        group = str(row.get("recording_group_id") or "")
        if group:
            if group in by_existing:
                uf.union(index, by_existing[group])
            else:
                by_existing[group] = index
        media = str(row.get("media_sha256") or "")
        if media:
            if media in by_media:
                uf.union(index, by_media[media])
            else:
                by_media[media] = index
        fp = row.get("canonical_fingerprint")
        pcm = str(fp.get("canonical_pcm_sha256") or "") if isinstance(fp, Mapping) else ""
        if pcm:
            if pcm in by_pcm:
                uf.union(index, by_pcm[pcm])
            else:
                by_pcm[pcm] = index

    fp_indexes = [i for i, row in enumerate(rows) if isinstance(row.get("canonical_fingerprint"), Mapping)]
    near_edges = 0
    cross_group_edges = 0
    for offset, left_i in enumerate(fp_indexes):
        left = rows[left_i]
        left_fp = left["canonical_fingerprint"]
        for right_i in fp_indexes[offset + 1:]:
            right = rows[right_i]
            right_fp = right["canonical_fingerprint"]
            if left_fp.get("canonical_pcm_sha256") == right_fp.get("canonical_pcm_sha256"):
                continue
            distance = fingerprint_distance(left_fp, right_fp)
            if distance > threshold:
                continue
            near_edges += 1
            if str(left.get("recording_group_id") or "") != str(right.get("recording_group_id") or ""):
                cross_group_edges += 1
            uf.union(left_i, right_i)

    components: dict[int, list[int]] = defaultdict(list)
    for index in range(len(rows)):
        components[uf.find(index)].append(index)

    fallback_before = sum(1 for row in rows if _is_fallback(row))
    acoustic_components = 0
    screened_singletons = 0
    members_reassigned = 0

    for indexes in components.values():
        member_ids = [str(rows[i].get("ledger_asset_id") or "") for i in indexes]
        existing_groups = {str(rows[i].get("recording_group_id") or "") for i in indexes if rows[i].get("recording_group_id")}
        has_fallback = any(_is_fallback(rows[i]) for i in indexes)
        needs_global = len(existing_groups) > 1

        if needs_global:
            global_id = f"global-acoustic:{_digest(member_ids)}"
            acoustic_components += 1
            for i in indexes:
                if rows[i].get("recording_group_id") != global_id:
                    members_reassigned += 1
                rows[i]["recording_group_id"] = global_id
                rows[i]["grouping_status"] = "GLOBAL_ACOUSTIC_COMPONENT"
        elif has_fallback:
            # A component with one source group and no cross-group acoustic edge is
            # conservatively accepted only as a screened source-asset family.
            screened_singletons += 1
            for i in indexes:
                if _is_fallback(rows[i]):
                    rows[i]["grouping_status"] = "GLOBAL_ACOUSTIC_SCREENED_SOURCE_GROUP"

        for i in indexes:
            rows[i]["blocking_reasons"] = [
                str(reason) for reason in (rows[i].get("blocking_reasons") or [])
                if str(reason) != "GROUPING_GLOBAL_AUDIT_REQUIRED"
            ]

    source_policy = load_dataset_certification(SOURCE_POLICY)
    for row in rows:
        recompute_stage(row, source_policy)

    audit = {
        "schema_version": "echo.global-recording-group-resolution.v1",
        "status": "PASS",
        "near_duplicate_threshold": threshold,
        "asset_count": len(rows),
        "component_count": len(components),
        "near_duplicate_edge_count": near_edges,
        "cross_source_group_near_duplicate_edge_count": cross_group_edges,
        "global_acoustic_component_count": acoustic_components,
        "screened_fallback_source_group_count": screened_singletons,
        "fallback_asset_count_before": fallback_before,
        "fallback_asset_count_after": sum(1 for row in rows if _is_fallback(row)),
        "members_reassigned_to_global_acoustic_component": members_reassigned,
        "content_merge_performed": False,
        "content_deleted": False,
        "policy_note": "Acoustic candidates force shared split protection; they do not prove content identity or authorize deletion.",
    }
    return rows, audit


def main() -> int:
    near_policy = json.loads(NEAR_POLICY.read_text(encoding="utf-8"))
    threshold = float(near_policy.get("comparison", {}).get("candidate_max_distance", 0.02))
    rows: list[dict[str, Any]] = []
    with LEDGER.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    rows = validate_ledger(rows)
    resolved, audit = resolve_groups(rows, threshold=threshold)
    resolved = validate_ledger(resolved)

    previous = json.loads(SUMMARY.read_text(encoding="utf-8"))
    refreshed = dict(previous)
    refreshed.update(summarize_ledger(resolved))
    refreshed["global_recording_group_resolution"] = audit

    with LEDGER.open("w", encoding="utf-8") as handle:
        for row in resolved:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")
    SUMMARY.write_text(json.dumps(refreshed, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(audit, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Deterministically balance dominant source families in the MK1 corpus-facing ledger.

This stage never changes source evidence or coverage floors. It operates after global
recording-family resolution, removes only excess target credit from configured
source families, and fails closed unless the resulting target still satisfies the
frozen global coverage floors.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping

from echo.data_foundry.ledger import summarize_ledger, validate_ledger
from echo.data_foundry.coverage_policy import load_coverage_policy

ROOT = Path(__file__).resolve().parents[2]
MAT = ROOT / "MK1/mining-site/materialization"
LEDGER = MAT / "canonical-release-safe-asset-ledger.jsonl"
SUMMARY = MAT / "canonical-release-safe-asset-ledger-summary.json"
BALANCE_POLICY = ROOT / "configs/data_foundry/source_balance_policy.v1.json"
COVERAGE_POLICY = ROOT / "configs/data_foundry/coverage_policy.v1.json"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"expected JSON object at {path}:{number}")
            rows.append(row)
    return rows


def stable_key(*parts: object) -> str:
    payload = "\0".join(str(part) for part in parts).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def max_allowed_dominant(other_count: int, max_fraction: float) -> int:
    if other_count < 0:
        raise ValueError("other_count must be non-negative")
    if not 0.0 < max_fraction < 1.0:
        raise ValueError("max_fraction must be in (0, 1)")
    raw = max_fraction * other_count / (1.0 - max_fraction)
    return max(0, math.floor(raw + 1e-12))


def select_dominant_asset_ids(
    rows: Iterable[Mapping[str, Any]],
    *,
    keep_count: int,
    policy_id: str,
    target: str,
    family: str,
) -> set[str]:
    materialized = [dict(row) for row in rows]
    if keep_count < 0 or keep_count > len(materialized):
        raise ValueError("invalid dominant keep_count")
    by_group: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in materialized:
        group = str(row.get("recording_group_id") or "")
        asset_id = str(row.get("ledger_asset_id") or "")
        if not group or not asset_id:
            raise ValueError("balanced rows require recording_group_id and ledger_asset_id")
        by_group[group].append(row)

    selected: list[str] = []
    ordered_groups = sorted(
        by_group,
        key=lambda group: (stable_key(policy_id, target, family, group), group),
    )
    # First pass: at most one member from each recording group.
    for group in ordered_groups:
        if len(selected) >= keep_count:
            break
        members = sorted(
            by_group[group],
            key=lambda row: (
                stable_key(policy_id, target, family, group, row["ledger_asset_id"]),
                str(row["ledger_asset_id"]),
            ),
        )
        selected.append(str(members[0]["ledger_asset_id"]))

    # Second pass: only when the requested keep count exceeds group count.
    if len(selected) < keep_count:
        already = set(selected)
        remaining = sorted(
            (row for row in materialized if str(row["ledger_asset_id"]) not in already),
            key=lambda row: (
                stable_key(policy_id, target, family, row["ledger_asset_id"]),
                str(row["ledger_asset_id"]),
            ),
        )
        selected.extend(str(row["ledger_asset_id"]) for row in remaining[: keep_count - len(selected)])

    if len(selected) != keep_count or len(set(selected)) != keep_count:
        raise ValueError("deterministic source-balance selection cardinality drift")
    return set(selected)


def remove_target_role(row: Mapping[str, Any], target: str) -> dict[str, Any] | None:
    updated = dict(row)
    updated["echo_labels"] = sorted({str(v) for v in (row.get("echo_labels") or []) if str(v) != target})
    updated["candidate_targets"] = sorted({str(v) for v in (row.get("candidate_targets") or []) if str(v) != target})
    semantics = dict(row.get("semantic_status_by_target") or {})
    semantics.pop(target, None)
    updated["semantic_status_by_target"] = dict(sorted(semantics.items()))
    if not updated["echo_labels"] and not (updated.get("hard_negative_for") or []):
        return None
    return updated


def target_metrics(rows: Iterable[Mapping[str, Any]], target: str) -> dict[str, Any]:
    positives = [row for row in rows if target in (row.get("echo_labels") or [])]
    groups = {str(row.get("recording_group_id") or "") for row in positives if row.get("recording_group_id")}
    sources = Counter(str(row.get("underlying_source_family") or "") for row in positives)
    duration = sum(float((row.get("audio_probe") or {}).get("duration_seconds") or 0.0) for row in positives)
    largest = max(sources.values(), default=0)
    return {
        "asset_count": len(positives),
        "independent_group_count": len(groups),
        "source_count": len(sources),
        "source_asset_counts": dict(sorted(sources.items())),
        "max_single_source_fraction": (largest / len(positives)) if positives else 0.0,
        "clip_duration_seconds": duration,
    }


def enforce_target_floor(metrics: Mapping[str, Any], req: Mapping[str, Any], max_fraction: float, target: str) -> None:
    checks = (
        ("assets", int(metrics["asset_count"]), int(req.get("min_assets", 0))),
        ("groups", int(metrics["independent_group_count"]), int(req.get("min_independent_groups", 0))),
        ("sources", int(metrics["source_count"]), int(req.get("min_sources", 0))),
        ("duration", float(metrics["clip_duration_seconds"]), float(req.get("min_clip_duration_seconds", 0.0))),
    )
    for name, actual, minimum in checks:
        if actual < minimum:
            raise ValueError(f"{target} source balance would violate {name} floor: {actual} < {minimum}")
    if float(metrics["max_single_source_fraction"]) > max_fraction + 1e-12:
        raise ValueError(
            f"{target} source balance failed concentration floor: "
            f"{metrics['max_single_source_fraction']:.6f} > {max_fraction:.6f}"
        )


def main() -> int:
    for path in (LEDGER, SUMMARY, BALANCE_POLICY, COVERAGE_POLICY):
        if not path.is_file():
            raise SystemExit(f"required source-balance input missing: {path.relative_to(ROOT)}")

    policy = read_json(BALANCE_POLICY)
    if policy.get("schema_version") != "echo.source-balance-policy.v1":
        raise SystemExit("unsupported source-balance policy schema")
    coverage = load_coverage_policy(COVERAGE_POLICY)
    if policy.get("coverage_policy_id") != coverage.get("policy_id"):
        raise SystemExit("source-balance policy is not bound to current coverage policy")

    profile = (coverage.get("profiles") or {}).get("release_safe") or {}
    target_requirements = profile.get("target_labels") or {}
    max_fraction = float(profile.get("max_single_source_fraction_per_class", 1.0))
    policy_id = str(policy.get("policy_id") or "")
    rows = validate_ledger(read_jsonl(LEDGER))
    audit_targets: dict[str, Any] = {}

    for target, cfg in sorted((policy.get("targets") or {}).items()):
        if not isinstance(cfg, Mapping) or cfg.get("enabled") is not True:
            continue
        family = str(cfg.get("dominant_underlying_source_family") or "")
        if not family:
            raise SystemExit(f"{target}: dominant family missing")
        positives = [row for row in rows if target in (row.get("echo_labels") or [])]
        source_counts = Counter(str(row.get("underlying_source_family") or "") for row in positives)
        if not positives or family not in source_counts:
            raise SystemExit(f"{target}: configured dominant family has no positives")
        actual_largest = max(source_counts.values())
        if source_counts[family] != actual_largest:
            raise SystemExit(f"{target}: configured family {family} is no longer the dominant family")

        dominant = [row for row in positives if str(row.get("underlying_source_family") or "") == family]
        other_count = len(positives) - len(dominant)
        allowed = max_allowed_dominant(other_count, max_fraction)
        keep_count = min(len(dominant), allowed)
        before = target_metrics(rows, target)

        if keep_count < len(dominant):
            selected = select_dominant_asset_ids(
                dominant,
                keep_count=keep_count,
                policy_id=policy_id,
                target=target,
                family=family,
            )
            next_rows: list[dict[str, Any]] = []
            removed_asset_ids: list[str] = []
            role_removed_but_row_kept: list[str] = []
            for row in rows:
                if (
                    target in (row.get("echo_labels") or [])
                    and str(row.get("underlying_source_family") or "") == family
                    and str(row.get("ledger_asset_id")) not in selected
                ):
                    changed = remove_target_role(row, target)
                    removed_asset_ids.append(str(row["ledger_asset_id"]))
                    if changed is not None:
                        role_removed_but_row_kept.append(str(row["ledger_asset_id"]))
                        next_rows.append(changed)
                else:
                    next_rows.append(row)
            rows = validate_ledger(next_rows)
        else:
            selected = {str(row["ledger_asset_id"]) for row in dominant}
            removed_asset_ids = []
            role_removed_but_row_kept = []

        after = target_metrics(rows, target)
        req = target_requirements.get(target)
        if not isinstance(req, Mapping):
            raise SystemExit(f"{target}: coverage requirements missing")
        enforce_target_floor(after, req, max_fraction, target)

        audit_targets[target] = {
            "status": "PASS",
            "dominant_underlying_source_family": family,
            "before": before,
            "after": after,
            "dominant_asset_keep_count": len(selected),
            "removed_target_credit_count": len(removed_asset_ids),
            "rows_preserved_for_other_roles_count": len(role_removed_but_row_kept),
            "removed_target_credit_asset_ids": sorted(removed_asset_ids),
            "selection": str(cfg.get("selection") or ""),
        }

    previous = read_json(SUMMARY)
    refreshed = dict(previous)
    refreshed.update(summarize_ledger(rows))
    refreshed["source_balance_selection"] = {
        "schema_version": "echo.source-balance-selection.v1",
        "policy_id": policy_id,
        "coverage_policy_id": coverage.get("policy_id"),
        "status": "PASS",
        "targets": audit_targets,
        "stop_line": "Source materialization evidence is unchanged; this audit selects the corpus-facing benchmark subset only.",
    }

    with LEDGER.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")
    SUMMARY.write_text(json.dumps(refreshed, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": "PASS",
        "entry_count": refreshed["entry_count"],
        "positive_counts": refreshed["positive_counts"],
        "targets": audit_targets,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

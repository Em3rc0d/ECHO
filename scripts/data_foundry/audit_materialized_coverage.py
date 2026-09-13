#!/usr/bin/env python3
"""Audit current real-byte materialization evidence without overstating admission.

The output separates direct release-safe evidence, research-only evidence and
review-required candidates. It is intentionally not the corpus coverage gate:
only Foundry admission + dedup + grouping + split + freeze may certify corpus
coverage.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "MK1/mining-site/materialization"
TARGETS = ("GLASS_SHATTER", "SIREN", "FIRE_ALARM", "VEHICLE_HORN", "TIRE_SQUEAL")
RELEASE_SAFE_LICENSES = {"CC0", "CC0-1.0", "PUBLIC-DOMAIN", "CC-BY", "CC-BY-4.0"}
EXACT_PUBLIC_SEMANTICS = {
    "GLASS_SHATTER": {"glass_shatter", "glass_break", "broken_glass"},
    "SIREN": {"siren", "vehicle_siren"},
    "FIRE_ALARM": {"fire_alarm"},
    "VEHICLE_HORN": {"vehicle_horn", "car_horn"},
    "TIRE_SQUEAL": {"tire_squeal"},
}


def load(name: str) -> dict:
    path = EVIDENCE / name
    if not path.is_file():
        return {"_missing": True, "_path": str(path)}
    return json.loads(path.read_text(encoding="utf-8"))


def public_exact_assets(report: dict) -> list[dict]:
    rows = []
    for row in report.get("assets", []):
        target = str(row.get("target") or "")
        semantic = str(row.get("semantic") or "").casefold()
        license_id = str(row.get("license_id") or "").upper()
        probe = row.get("audio_probe") or {}
        if (
            target in TARGETS
            and semantic in EXACT_PUBLIC_SEMANTICS.get(target, set())
            and license_id in RELEASE_SAFE_LICENSES
            and probe.get("ok") is True
            and row.get("media_sha256")
        ):
            rows.append(row)
    return rows


def main() -> int:
    sonyc = load("sonyc-v2.3-full-materialization-summary.json")
    singa = load("singapura-v1.0a-materialization-summary.json")
    esc = load("esc50-pinned-materialization-summary.json")
    public = load("public-gap-assets-report.json")
    freesound = load("freesound-cc0-gap-assets-report.json")
    fsd = load("fsd50k-metadata-inspection.json")

    missing = [
        name for name, payload in {
            "SONYC": sonyc,
            "SINGA:PURA": singa,
            "ESC-50": esc,
            "public-gap": public,
            "Freesound-CC0": freesound,
            "FSD50K-metadata": fsd,
        }.items() if payload.get("_missing")
    ]
    if missing:
        raise SystemExit("materialization evidence missing: " + ", ".join(missing))

    release_counts = Counter()
    release_sources: dict[str, set[str]] = defaultdict(set)
    release_groups: dict[str, set[str]] = defaultdict(set)
    release_duration = Counter()
    research_counts = Counter()
    review_counts = Counter()
    review_duration = Counter()

    # SONYC is source-level release-safe and these counts come from annotator-0
    # ground truth. Duplicate/global split filtering still happens downstream.
    for target, count in (sonyc.get("target_ground_truth_counts") or {}).items():
        if target in TARGETS:
            release_counts[target] += int(count)
            release_sources[target].add("sonyc-ust-v2")
    for target, groups in (sonyc.get("target_independent_group_candidates") or {}).items():
        if target in TARGETS:
            # The summary contains counts rather than identities, so encode
            # conservative synthetic identity placeholders only for readiness
            # arithmetic; final Foundry grouping remains authoritative.
            for index in range(int(groups)):
                release_groups[target].add(f"sonyc-group-candidate:{index}")

    # Public curated sources only get direct credit where semantic is exact,
    # license is release-safe, real bytes were hashed, and probe passed.
    for row in public_exact_assets(public):
        target = str(row["target"])
        release_counts[target] += 1
        release_sources[target].add(str(row.get("source_dataset") or "public-gap"))
        family = str(row.get("recording_family") or row.get("asset_key") or row.get("media_sha256"))
        release_groups[target].add(f"{row.get('source_dataset')}:{family}")
        release_duration[target] += float((row.get("audio_probe") or {}).get("duration_seconds") or 0.0)

    # Freesound CC0 previews are real, rights-compatible candidate bytes, but
    # exact-category candidate membership is not equivalent to semantic review.
    for target, row in (freesound.get("targets") or {}).items():
        if target in TARGETS:
            review_counts[target] += int(row.get("cc0_materialized_count") or 0)
            review_duration[target] += float(row.get("materialized_duration_seconds") or 0.0)

    # Research-only evidence is useful for model science but cannot silently
    # repair release-safe lineage.
    for source_payload in (singa, esc):
        for target, count in (source_payload.get("target_counts") or {}).items():
            if target in TARGETS:
                research_counts[target] += int(count)

    floor = json.loads((ROOT / "configs/data_foundry/coverage_policy.v1.json").read_text(encoding="utf-8"))["profiles"]["release_safe"]
    classes = {}
    blocking = []
    for target in TARGETS:
        req = floor["target_labels"][target]
        direct_assets = release_counts[target]
        direct_groups = len(release_groups[target])
        direct_sources = len(release_sources[target])
        candidate_after_review = review_counts[target]
        reasons = []
        if direct_assets < int(req["min_assets"]):
            reasons.append(f"DIRECT_ASSETS_{direct_assets}_LT_{req['min_assets']}")
        if direct_groups < int(req["min_independent_groups"]):
            reasons.append(f"DIRECT_GROUPS_{direct_groups}_LT_{req['min_independent_groups']}")
        if direct_sources < int(req["min_sources"]):
            reasons.append(f"DIRECT_SOURCES_{direct_sources}_LT_{req['min_sources']}")
        if reasons:
            blocking.extend(f"{target}:{reason}" for reason in reasons)
        classes[target] = {
            "release_safe_direct_real_asset_count_before_global_dedup": direct_assets,
            "release_safe_direct_source_count": direct_sources,
            "release_safe_direct_sources": sorted(release_sources[target]),
            "release_safe_group_candidate_count_before_global_group_audit": direct_groups,
            "release_safe_direct_duration_seconds_known_from_public_gap_only": round(float(release_duration[target]), 6),
            "cc0_real_assets_pending_semantic_review": candidate_after_review,
            "cc0_pending_review_duration_seconds": round(float(review_duration[target]), 6),
            "research_only_real_asset_count": research_counts[target],
            "current_readiness": "NOT_READY" if reasons else "MINIMUM_DIRECT_PRECHECK_PASS",
            "precheck_blockers": reasons,
        }

    payload = {
        "schema_version": "echo.materialized-coverage-audit.v1",
        "status": "OPEN" if blocking else "PRECHECK_PASS",
        "scope": "Pre-admission empirical materialization audit. Not a substitute for Foundry coverage-gate.json.",
        "materialized_sources": {
            "sonyc": {"status": sonyc.get("status"), "asset_count": sonyc.get("asset_count"), "shards": sonyc.get("shards_materialized")},
            "singapura": {"status": singa.get("status"), "selected_recording_count": singa.get("selected_recording_count"), "profile": singa.get("profile")},
            "esc50": {"status": esc.get("status"), "selected_asset_count": esc.get("selected_asset_count"), "profile": esc.get("profile")},
            "public_gap": {"status": public.get("status"), "materialized_count": public.get("materialized_count")},
            "freesound_cc0": {"materialized_count": freesound.get("materialized_count"), "candidate_count": freesound.get("candidate_count")},
            "fsd50k": {"status": fsd.get("status"), "mode": "metadata_ground_truth_only_due_free_tier_boundary"},
        },
        "classes": classes,
        "blocking_precheck_nodes": blocking,
        "next_rule": "Do not weaken thresholds. Close blockers using free, rights-defensible real media; then run full Foundry admission/dedup/group/split/freeze and require coverage-gate.json PASS with gap_codes=[].",
    }
    output = EVIDENCE / "materialized-coverage-audit.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "blockers": len(blocking), "output": str(output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

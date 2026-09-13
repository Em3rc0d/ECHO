"""Stdlib-only CLI for deterministic ECHO MK1 Data Foundry operations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .acquisition import files_for_stage, load_acquisition_registry, verification_summary, verify_source_release
from .coverage_policy import load_coverage_policy
from .dataset import load_benchmark_split, validate_frozen_bundle
from .hashing import canonical_json_sha256, sha256_file
from .intake import load_intake_spec, run_intake_spec, write_candidate_manifest
from .pipeline import admit_from_files, freeze_corpus, load_split_policy, read_record_manifest
from .publisher_snapshot import verify_snapshot_from_files
from .registry import load_source_registry
from .source_policy import load_dataset_certification, source_policy_summary
from .splits import SplitRatios, assign_group


_DEFAULT_COVERAGE_POLICY = "configs/data_foundry/coverage_policy.v1.json"


def _load_json(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"JSON object required: {path}")
    return payload


def _cmd_validate_registry(args: argparse.Namespace) -> int:
    payload = load_source_registry(args.path)
    print(json.dumps({"status": "PASS", "sources": len(payload["sources"]), "schema_version": payload["schema_version"]}, sort_keys=True))
    return 0


def _cmd_source_policy(args: argparse.Namespace) -> int:
    payload = load_dataset_certification(args.path)
    print(json.dumps({
        "status": "PASS",
        "schema_version": payload["schema_version"],
        "profile": args.profile,
        "sources": source_policy_summary(payload, profile=args.profile),
    }, indent=2, sort_keys=True))
    return 0


def _cmd_verify_publisher_snapshot(args: argparse.Namespace) -> int:
    snapshot = args.snapshot or f"configs/data_foundry/publisher_snapshots/{args.source_id}.json"
    result = verify_snapshot_from_files(
        source_id=args.source_id,
        snapshot_path=snapshot,
        acquisition_registry_path=args.acquisition_registry,
        certification_path=args.certification,
        source_registry_path=args.source_registry,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def _cmd_hash_file(args: argparse.Namespace) -> int:
    path = Path(args.path)
    print(json.dumps({"path": str(path), "sha256": sha256_file(path)}, sort_keys=True))
    return 0


def _cmd_digest_json(args: argparse.Namespace) -> int:
    payload = _load_json(args.path)
    print(json.dumps({"path": str(args.path), "canonical_sha256": canonical_json_sha256(payload)}, sort_keys=True))
    return 0


def _cmd_plan_split(args: argparse.Namespace) -> int:
    ratios = SplitRatios(args.train, args.validation, args.test)
    split = assign_group(args.group_id, seed=args.seed, ratios=ratios)
    print(json.dumps({"group_id": args.group_id, "seed": args.seed, "split": split}, sort_keys=True))
    return 0


def _cmd_acquisition_plan(args: argparse.Namespace) -> int:
    registry = load_acquisition_registry(args.registry)
    try:
        source = registry["sources"][args.source_id]
    except KeyError as exc:
        raise SystemExit(f"unknown source_id: {args.source_id}") from exc
    files = files_for_stage(source, args.stage)
    print(json.dumps({
        "source_id": args.source_id,
        "stage": args.stage,
        "record_url": source.get("record_url"),
        "expected_files": [{"name": row.get("name"), "md5": row.get("md5"), "size_display": row.get("size_display")} for row in files],
        "file_count": len(files),
        "estimated_total_display": source.get("estimated_total_display"),
        "manual_download_required": bool(source.get("manual_download_required", False)),
    }, indent=2, sort_keys=True))
    return 0


def _cmd_verify_acquisition(args: argparse.Namespace) -> int:
    registry = load_acquisition_registry(args.registry)
    results = verify_source_release(registry=registry, source_id=args.source_id, root=args.root, stage=args.stage)
    summary = verification_summary(results)
    payload = {
        "source_id": args.source_id,
        "stage": args.stage,
        "root": str(args.root),
        "summary": summary,
        "files": [{
            "name": row.name,
            "present": row.present,
            "checksum_expected": row.checksum_expected,
            "checksum_actual": row.checksum_actual,
            "checksum_ok": row.checksum_ok,
            "size_bytes": row.size_bytes,
        } for row in results],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if summary["status"] == "PASS" else 2


def _cmd_intake(args: argparse.Namespace) -> int:
    spec = load_intake_spec(args.spec)
    candidates = run_intake_spec(spec)
    digest = write_candidate_manifest(args.output, candidates)
    print(json.dumps({"status": "PASS", "candidates": len(candidates), "candidate_manifest_sha256": digest, "output": str(args.output)}, sort_keys=True))
    return 0


def _cmd_admit(args: argparse.Namespace) -> int:
    digest = admit_from_files(
        candidate_manifest=args.candidates,
        mapping_path=args.mapping,
        license_policy_path=args.license_policy,
        profile=args.profile,
        output_path=args.output,
        audio_root=args.audio_root,
        reviews_path=args.reviews,
    )
    print(json.dumps({"status": "PASS", "asset_record_manifest_sha256": digest, "output": str(args.output)}, sort_keys=True))
    return 0


def _cmd_freeze(args: argparse.Namespace) -> int:
    records = read_record_manifest(args.records)
    coverage_policy = None
    if args.coverage_policy:
        coverage_policy = load_coverage_policy(args.coverage_policy)
    elif args.profile == "release_safe":
        coverage_policy = load_coverage_policy(_DEFAULT_COVERAGE_POLICY)

    result = freeze_corpus(
        records=records,
        output_dir=args.output_dir,
        manifest_id=args.manifest_id,
        profile=args.profile,
        taxonomy_version=args.taxonomy_version,
        source_registry=_load_json(args.source_registry),
        license_policy=_load_json(args.license_policy),
        label_mapping=_load_json(args.mapping),
        split_policy=load_split_policy(args.split_policy),
        source_certification=load_dataset_certification(args.source_certification),
        coverage_policy=coverage_policy,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"].startswith("PASS") else 2


def _cmd_validate_bundle(args: argparse.Namespace) -> int:
    result = validate_frozen_bundle(args.bundle_dir)
    print(json.dumps({"status": "PASS", **result}, indent=2, sort_keys=True))
    return 0


def _cmd_list_split(args: argparse.Namespace) -> int:
    rows = load_benchmark_split(args.bundle_dir, args.split)
    if args.ids_only:
        print("\n".join(str(row["asset_id"]) for row in rows))
    else:
        print(json.dumps(rows, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="echo-data-foundry", description="ECHO MK1 Data Foundry utilities")
    sub = parser.add_subparsers(dest="command", required=True)

    registry = sub.add_parser("validate-source-registry", help="validate the versioned source registry")
    registry.add_argument("path")
    registry.set_defaults(func=_cmd_validate_registry)

    source_policy = sub.add_parser("source-policy", help="show source certification decisions for one corpus profile")
    source_policy.add_argument("--path", default="configs/data_foundry/dataset_certification.v1.json")
    source_policy.add_argument("--profile", choices=["release_safe", "research_extended", "field_holdout"], required=True)
    source_policy.set_defaults(func=_cmd_source_policy)

    snapshot = sub.add_parser("verify-publisher-snapshot", help="verify pinned official publisher evidence against all source registries")
    snapshot.add_argument("source_id")
    snapshot.add_argument("--snapshot")
    snapshot.add_argument("--acquisition-registry", default="configs/data_foundry/acquisition_registry.v1.json")
    snapshot.add_argument("--certification", default="configs/data_foundry/dataset_certification.v1.json")
    snapshot.add_argument("--source-registry", default="configs/data_foundry/source_registry.v1.json")
    snapshot.set_defaults(func=_cmd_verify_publisher_snapshot)

    hash_file = sub.add_parser("hash-file", help="compute SHA-256 for one local asset")
    hash_file.add_argument("path")
    hash_file.set_defaults(func=_cmd_hash_file)

    digest = sub.add_parser("digest-json", help="compute canonical SHA-256 for JSON policy/config")
    digest.add_argument("path")
    digest.set_defaults(func=_cmd_digest_json)

    split = sub.add_parser("plan-split", help="deterministically assign one group to an explicit split profile")
    split.add_argument("group_id")
    split.add_argument("--seed", required=True)
    split.add_argument("--train", type=float, required=True)
    split.add_argument("--validation", type=float, required=True)
    split.add_argument("--test", type=float, required=True)
    split.set_defaults(func=_cmd_plan_split)

    plan = sub.add_parser("acquisition-plan", help="show publisher files required for one source/stage")
    plan.add_argument("source_id")
    plan.add_argument("--registry", default="configs/data_foundry/acquisition_registry.v1.json")
    plan.add_argument("--stage", choices=["metadata", "full"], default="metadata")
    plan.set_defaults(func=_cmd_acquisition_plan)

    verify = sub.add_parser("verify-acquisition", help="verify already downloaded publisher bundles")
    verify.add_argument("source_id")
    verify.add_argument("root")
    verify.add_argument("--registry", default="configs/data_foundry/acquisition_registry.v1.json")
    verify.add_argument("--stage", choices=["metadata", "full"], default="metadata")
    verify.set_defaults(func=_cmd_verify_acquisition)

    intake = sub.add_parser("intake", help="parse source metadata using a versioned intake spec")
    intake.add_argument("spec")
    intake.add_argument("output")
    intake.set_defaults(func=_cmd_intake)

    admit = sub.add_parser("admit", help="probe/hash/license/map/review candidates into asset records")
    admit.add_argument("candidates")
    admit.add_argument("output")
    admit.add_argument("--profile", choices=["release_safe", "research_extended"], required=True)
    admit.add_argument("--mapping", default="configs/data_foundry/label_mapping.v1.json")
    admit.add_argument("--license-policy", default="configs/data_foundry/license_policy.v1.json")
    admit.add_argument("--audio-root")
    admit.add_argument("--reviews")
    admit.set_defaults(func=_cmd_admit)

    freeze = sub.add_parser("freeze", help="assign splits, enforce source/coverage policy, audit leakage and freeze corpus evidence")
    freeze.add_argument("records")
    freeze.add_argument("output_dir")
    freeze.add_argument("--manifest-id", required=True)
    freeze.add_argument("--profile", choices=["release_safe", "research_extended", "field_holdout"], required=True)
    freeze.add_argument("--taxonomy-version", default="echo.taxonomy.v1")
    freeze.add_argument("--source-registry", default="configs/data_foundry/source_registry.v1.json")
    freeze.add_argument("--source-certification", default="configs/data_foundry/dataset_certification.v1.json")
    freeze.add_argument("--coverage-policy", default=None, help="coverage policy path; release_safe automatically uses configs/data_foundry/coverage_policy.v1.json when omitted")
    freeze.add_argument("--license-policy", default="configs/data_foundry/license_policy.v1.json")
    freeze.add_argument("--mapping", default="configs/data_foundry/label_mapping.v1.json")
    freeze.add_argument("--split-policy", default="configs/data_foundry/split_policy.v1.json")
    freeze.set_defaults(func=_cmd_freeze)

    bundle = sub.add_parser("validate-bundle", help="validate frozen manifest hashes and split identities")
    bundle.add_argument("bundle_dir")
    bundle.set_defaults(func=_cmd_validate_bundle)

    view = sub.add_parser("list-split", help="enumerate benchmark assets exclusively from a frozen bundle")
    view.add_argument("bundle_dir")
    view.add_argument("split", choices=["train", "validation", "test", "field_holdout"])
    view.add_argument("--ids-only", action="store_true")
    view.set_defaults(func=_cmd_list_split)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())

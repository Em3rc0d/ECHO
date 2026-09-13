"""Small stdlib-only CLI for deterministic Foundry foundation operations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .hashing import canonical_json_sha256, sha256_file
from .registry import load_source_registry
from .splits import SplitRatios, assign_group


def _cmd_validate_registry(args: argparse.Namespace) -> int:
    payload = load_source_registry(args.path)
    print(json.dumps({"status": "PASS", "sources": len(payload["sources"]), "schema_version": payload["schema_version"]}, sort_keys=True))
    return 0


def _cmd_hash_file(args: argparse.Namespace) -> int:
    path = Path(args.path)
    print(json.dumps({"path": str(path), "sha256": sha256_file(path)}, sort_keys=True))
    return 0


def _cmd_digest_json(args: argparse.Namespace) -> int:
    with Path(args.path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    print(json.dumps({"path": str(args.path), "canonical_sha256": canonical_json_sha256(payload)}, sort_keys=True))
    return 0


def _cmd_plan_split(args: argparse.Namespace) -> int:
    ratios = SplitRatios(args.train, args.validation, args.test)
    split = assign_group(args.group_id, seed=args.seed, ratios=ratios)
    print(json.dumps({"group_id": args.group_id, "seed": args.seed, "split": split}, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="echo-data-foundry", description="ECHO MK1 Data Foundry utilities")
    sub = parser.add_subparsers(dest="command", required=True)

    registry = sub.add_parser("validate-source-registry", help="validate the versioned source registry")
    registry.add_argument("path")
    registry.set_defaults(func=_cmd_validate_registry)

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

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())

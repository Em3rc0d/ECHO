#!/usr/bin/env python3
"""Index locally materialized ECHO MVP media by governed SHA-256.

The benchmark never trusts filenames or source-specific folder layouts. Any
local media cache is acceptable when bytes match the SHA-256 frozen in the MVP
manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def wanted_hashes(manifest: Path) -> set[str]:
    result: set[str] = set()
    with manifest.open("r", encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, 1):
            if not raw.strip():
                continue
            row = json.loads(raw)
            digest = str(row.get("media_sha256") or "")
            if len(digest) != 64:
                raise ValueError(f"{manifest}:{line_no}: invalid media_sha256")
            result.add(digest)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("MK1/mining-site/materialization/mvp-benchmark-manifest.jsonl"),
    )
    parser.add_argument("--audio-root", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("MK1/mining-site/materialization/mvp-media-index.json"),
    )
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()

    wanted = wanted_hashes(args.manifest)
    found: dict[str, str] = {}
    duplicate_paths: dict[str, list[str]] = {}

    for path in sorted(p for p in args.audio_root.rglob("*") if p.is_file()):
        digest = sha256_file(path)
        if digest not in wanted:
            continue
        rel = str(path.resolve())
        if digest in found:
            duplicate_paths.setdefault(digest, [found[digest]]).append(rel)
        else:
            found[digest] = rel

    missing = sorted(wanted - set(found))
    payload = {
        "schema_version": "echo.mvp-media-index.v1",
        "manifest": str(args.manifest),
        "audio_root": str(args.audio_root.resolve()),
        "wanted_sha256_count": len(wanted),
        "resolved_sha256_count": len(found),
        "missing_sha256_count": len(missing),
        "duplicate_sha256_path_count": len(duplicate_paths),
        "by_sha256": dict(sorted(found.items())),
        "missing_sha256": missing,
        "duplicate_paths": duplicate_paths,
        "status": "COMPLETE" if not missing else "INCOMPLETE",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "wanted": len(wanted),
                "resolved": len(found),
                "missing": len(missing),
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )
    if args.require_complete and missing:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

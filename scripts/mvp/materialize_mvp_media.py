#!/usr/bin/env python3
"""Rehydrate exactly the frozen ECHO-MVP-001 media bytes.

The canonical benchmark manifest already freezes asset identity by SHA-256.
This utility restores those exact bytes into a local object cache without
changing corpus semantics or durable evidence:

- direct/public assets are downloaded from URLs already captured in durable
  materialization evidence and accepted only when SHA-256 matches the manifest;
- SONYC assets are restored from the publisher's pinned v2.3 shards, with both
  publisher MD5 and durable archive SHA-256 verification, then only the 599
  manifest-selected WAV members are retained;
- completed objects are content-addressed and resumable;
- no documentation/evidence file in the repository is rewritten.

It is an execution/materialization helper, not a new admission or certification
path.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import tarfile
import time
from typing import Any, Iterable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
MAT = ROOT / "MK1/mining-site/materialization"
DEFAULT_MANIFEST = MAT / "mvp-benchmark-manifest.jsonl"
ACQUISITION_REGISTRY = ROOT / "configs/data_foundry/acquisition_registry.v1.json"
SONYC_DIGESTS = MAT / "sonyc-v2.3-shard-digests.json"
SONYC_TARGETS = MAT / "sonyc-v2.3-target-candidates.jsonl"
SONYC_CONFUSERS = MAT / "sonyc-v2.3-confuser-candidates.jsonl"

DIRECT_LOCATORS = MAT / "mvp-direct-media-locators.json"

USER_AGENT = "ECHO-MVP-Rehydrator/1.0 (+https://github.com/Em3rc0d/ECHO)"
DIRECT_URL_KEYS = (
    "resolved_media_url",
    "resolved_transport_url",
    "media_url",
    "transport_url",
)
AUDIO_SUFFIXES = {".wav", ".mp3", ".ogg", ".flac", ".m4a", ".aac", ".aiff", ".aif"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def md5_file(path: Path) -> str:
    h = hashlib.md5()  # nosec B303 - publisher checksum compatibility only
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected JSON object")
    return payload


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, 1):
            if not raw.strip():
                continue
            payload = json.loads(raw)
            if not isinstance(payload, dict):
                raise ValueError(f"{path}:{line_no}: expected JSON object")
            result.append(payload)
    return result


def publisher_url(record_url: str, filename: str) -> str:
    parsed = urlparse(record_url)
    record_id = parsed.path.rstrip("/").split("/")[-1]
    if parsed.netloc != "zenodo.org" or not record_id.isdigit():
        raise ValueError(f"unsupported publisher record: {record_url}")
    return (
        f"https://zenodo.org/api/records/{record_id}/files/"
        f"{quote(filename, safe='')}/content"
    )


def download_to(
    url: str,
    target: Path,
    *,
    attempts: int = 6,
    expected_sha256: str | None = None,
) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    part = target.with_suffix(target.suffix + ".part")
    last: Exception | None = None

    for attempt in range(1, attempts + 1):
        sha = hashlib.sha256()
        try:
            request = Request(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "application/octet-stream,*/*;q=0.8",
                },
            )
            with urlopen(request, timeout=180) as response, part.open("wb") as out:  # nosec B310
                final_url = response.geturl()
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    sha.update(chunk)
                    out.write(chunk)
            digest = sha.hexdigest()
            if expected_sha256 and digest != expected_sha256:
                part.unlink(missing_ok=True)
                raise RuntimeError(
                    f"SHA-256 mismatch for {url}: {digest} != {expected_sha256}"
                )
            part.replace(target)
            return final_url
        except (HTTPError, URLError, TimeoutError, OSError, RuntimeError) as exc:
            last = exc
            part.unlink(missing_ok=True)
            if attempt < attempts:
                time.sleep(min(20, 2 ** (attempt - 1)))
    raise RuntimeError(f"download failed after {attempts} attempts: {url}: {last}")


def direct_url_index() -> dict[str, str]:
    payload = load_json(DIRECT_LOCATORS)
    if payload.get("profile_id") != "ECHO-MVP-001":
        raise ValueError("direct locator bundle is not ECHO-MVP-001")
    raw = payload.get("locators")
    if not isinstance(raw, Mapping):
        raise ValueError("direct locator bundle missing locators")
    result: dict[str, str] = {}
    for digest, row in raw.items():
        if len(str(digest)) != 64 or not isinstance(row, Mapping):
            raise ValueError("invalid direct locator row")
        url = str(row.get("url") or "")
        if not url.startswith(("https://", "http://")):
            raise ValueError(f"invalid direct locator URL for {digest}")
        result[str(digest)] = url
    if int(payload.get("locator_count", -1)) != len(result):
        raise ValueError("direct locator count mismatch")
    return result

def extension_for_url(url: str, default: str = ".bin") -> str:
    suffix = PurePosixPath(urlparse(url).path).suffix.casefold()
    return suffix if suffix in AUDIO_SUFFIXES else default


def restore_direct(
    *,
    digest: str,
    url: str,
    object_dir: Path,
) -> tuple[str, str]:
    suffix = extension_for_url(url)
    target = object_dir / f"{digest}{suffix}"

    if target.is_file():
        if sha256_file(target) == digest:
            return digest, str(target.resolve())
        target.unlink()

    # A previous run may have used another extension. Content identity wins.
    for candidate in object_dir.glob(f"{digest}.*"):
        if candidate.is_file() and sha256_file(candidate) == digest:
            return digest, str(candidate.resolve())

    download_to(url, target, expected_sha256=digest)
    return digest, str(target.resolve())


def sonyc_evidence_index() -> dict[str, dict[str, str]]:
    rows = load_jsonl(SONYC_TARGETS) + load_jsonl(SONYC_CONFUSERS)
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        digest = str(row.get("sha256") or "")
        archive = str(row.get("archive") or "")
        member = str(row.get("archive_member") or "")
        if len(digest) == 64 and archive and member:
            result[digest] = {
                "archive": archive,
                "member": member,
                "asset": str(row.get("source_asset_id") or ""),
            }
    return result


def sonyc_archive_contract() -> tuple[str, dict[str, dict[str, str]]]:
    registry = load_json(ACQUISITION_REGISTRY)
    source = registry.get("sources", {}).get("sonyc-ust-v2")
    if not isinstance(source, Mapping):
        raise ValueError("SONYC source missing from acquisition registry")

    entries = {
        str(row["name"]): row
        for row in source.get("files", [])
        if isinstance(row, Mapping) and str(row.get("name") or "").startswith("audio-")
    }

    durable = load_json(SONYC_DIGESTS)
    shard_rows = durable.get("shards")
    if not isinstance(shard_rows, list):
        raise ValueError("SONYC durable shard digest evidence missing")

    result: dict[str, dict[str, str]] = {}
    for row in shard_rows:
        name = str(row.get("shard_file") or "")
        registry_row = entries.get(name)
        if not registry_row:
            raise ValueError(f"SONYC shard {name} missing from acquisition registry")
        expected_md5 = str(registry_row.get("md5") or "").lower()
        durable_md5 = str(row.get("publisher_md5") or "").lower()
        if expected_md5 != durable_md5:
            raise ValueError(f"SONYC publisher MD5 evidence mismatch for {name}")
        result[name] = {
            "md5": expected_md5,
            "sha256": str(row.get("archive_sha256") or ""),
        }
    return str(source["record_url"]), result


def restore_sonyc_shard(
    *,
    archive_name: str,
    wanted: list[tuple[str, str]],
    record_url: str,
    contract: Mapping[str, Mapping[str, str]],
    object_dir: Path,
    download_dir: Path,
    keep_archives: bool,
) -> list[tuple[str, str]]:
    entry = contract.get(archive_name)
    if not entry:
        raise ValueError(f"no verified archive contract for {archive_name}")

    unresolved: list[tuple[str, str]] = []
    resolved: list[tuple[str, str]] = []
    for digest, member in wanted:
        target = object_dir / f"{digest}.wav"
        if target.is_file() and sha256_file(target) == digest:
            resolved.append((digest, str(target.resolve())))
        else:
            target.unlink(missing_ok=True)
            unresolved.append((digest, member))

    if not unresolved:
        return resolved

    archive = download_dir / archive_name
    if archive.is_file():
        md5_ok = md5_file(archive) == str(entry["md5"])
        sha_ok = sha256_file(archive) == str(entry["sha256"])
        if not (md5_ok and sha_ok):
            archive.unlink()

    if not archive.is_file():
        download_to(
            publisher_url(record_url, archive_name),
            archive,
            expected_sha256=str(entry["sha256"]),
        )

    actual_md5 = md5_file(archive)
    if actual_md5 != str(entry["md5"]):
        archive.unlink(missing_ok=True)
        raise RuntimeError(
            f"publisher MD5 mismatch for {archive_name}: "
            f"{actual_md5} != {entry['md5']}"
        )

    with tarfile.open(archive, "r:gz") as tf:
        members_by_name = {member.name: member for member in tf.getmembers() if member.isfile()}
        for digest, member_name in unresolved:
            member = members_by_name.get(member_name)
            if member is None:
                # Durable evidence sometimes records a normalized extraction path;
                # accept a unique suffix match, never an ambiguous one.
                matches = [
                    member
                    for name, member in members_by_name.items()
                    if name.endswith("/" + member_name) or name == member_name
                ]
                if len(matches) != 1:
                    raise RuntimeError(
                        f"{archive_name}: cannot resolve durable member {member_name!r}"
                    )
                member = matches[0]

            source = tf.extractfile(member)
            if source is None:
                raise RuntimeError(f"{archive_name}: failed to read {member.name}")

            target = object_dir / f"{digest}.wav"
            temp = target.with_suffix(".wav.part")
            sha = hashlib.sha256()
            with source, temp.open("wb") as out:
                while True:
                    chunk = source.read(1024 * 1024)
                    if not chunk:
                        break
                    sha.update(chunk)
                    out.write(chunk)
            actual = sha.hexdigest()
            if actual != digest:
                temp.unlink(missing_ok=True)
                raise RuntimeError(
                    f"{archive_name}:{member.name}: SHA-256 {actual} != {digest}"
                )
            temp.replace(target)
            resolved.append((digest, str(target.resolve())))

    if not keep_archives:
        archive.unlink(missing_ok=True)
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--direct-workers", type=int, default=6)
    parser.add_argument("--keep-sonyc-archives", action="store_true")
    parser.add_argument("--skip-direct", action="store_true")
    parser.add_argument("--skip-sonyc", action="store_true")
    args = parser.parse_args()

    if args.direct_workers < 1:
        raise SystemExit("--direct-workers must be >= 1")

    root = args.root.resolve()
    object_dir = root / "objects"
    download_dir = root / "downloads" / "sonyc"
    report_dir = root / "reports"
    object_dir.mkdir(parents=True, exist_ok=True)
    download_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    manifest = load_jsonl(args.manifest)
    expected = {str(row["media_sha256"]): row for row in manifest}
    sonyc_wanted = {
        digest
        for digest, row in expected.items()
        if str(row.get("source_dataset") or "") == "sonyc-ust-v2"
    }
    direct_wanted = set(expected) - sonyc_wanted

    media_index: dict[str, str] = {}
    failures: dict[str, str] = {}

    if not args.skip_direct:
        urls = direct_url_index()
        missing_url = sorted(direct_wanted - set(urls))
        if missing_url:
            raise SystemExit(
                f"durable direct-media URL evidence missing for {len(missing_url)} MVP assets"
            )

        with ThreadPoolExecutor(max_workers=args.direct_workers) as pool:
            futures = {
                pool.submit(
                    restore_direct,
                    digest=digest,
                    url=urls[digest],
                    object_dir=object_dir,
                ): digest
                for digest in sorted(direct_wanted)
            }
            completed = 0
            for future in as_completed(futures):
                digest = futures[future]
                try:
                    restored_digest, path = future.result()
                    media_index[restored_digest] = path
                except Exception as exc:
                    failures[digest] = f"{type(exc).__name__}:{exc}"
                completed += 1
                if completed % 50 == 0 or completed == len(futures):
                    print(
                        f"direct {completed}/{len(futures)} failures={len(failures)}",
                        flush=True,
                    )

    if not args.skip_sonyc:
        evidence = sonyc_evidence_index()
        missing_evidence = sorted(sonyc_wanted - set(evidence))
        if missing_evidence:
            raise SystemExit(
                f"durable SONYC member evidence missing for {len(missing_evidence)} MVP assets"
            )

        by_archive: dict[str, list[tuple[str, str]]] = {}
        for digest in sorted(sonyc_wanted):
            row = evidence[digest]
            by_archive.setdefault(row["archive"], []).append((digest, row["member"]))

        record_url, contract = sonyc_archive_contract()
        for index, archive_name in enumerate(sorted(by_archive), 1):
            print(
                f"SONYC shard {index}/{len(by_archive)} {archive_name} "
                f"wanted={len(by_archive[archive_name])}",
                flush=True,
            )
            try:
                restored = restore_sonyc_shard(
                    archive_name=archive_name,
                    wanted=by_archive[archive_name],
                    record_url=record_url,
                    contract=contract,
                    object_dir=object_dir,
                    download_dir=download_dir,
                    keep_archives=args.keep_sonyc_archives,
                )
                media_index.update(dict(restored))
            except Exception as exc:
                for digest, _member in by_archive[archive_name]:
                    if digest not in media_index:
                        failures[digest] = f"{type(exc).__name__}:{exc}"

    # Include already-restored/resumed content even when a lane was skipped.
    for digest in expected:
        if digest in media_index:
            continue
        candidates = list(object_dir.glob(f"{digest}.*"))
        for candidate in candidates:
            if candidate.is_file() and sha256_file(candidate) == digest:
                media_index[digest] = str(candidate.resolve())
                break

    missing = sorted(set(expected) - set(media_index))
    index_payload = {
        "schema_version": "echo.mvp-media-index.v1",
        "profile_id": "ECHO-MVP-001",
        "manifest": str(args.manifest),
        "root": str(root),
        "wanted_sha256_count": len(expected),
        "direct_wanted_count": len(direct_wanted),
        "sonyc_wanted_count": len(sonyc_wanted),
        "resolved_sha256_count": len(media_index),
        "missing_sha256_count": len(missing),
        "failure_count": len(failures),
        "status": "COMPLETE" if not missing and not failures else "INCOMPLETE",
        "by_sha256": dict(sorted(media_index.items())),
        "missing_sha256": missing,
        "failures": dict(sorted(failures.items())),
    }
    index_path = root / "mvp-media-index.json"
    index_path.write_text(
        json.dumps(index_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    summary = {
        key: index_payload[key]
        for key in (
            "profile_id",
            "wanted_sha256_count",
            "direct_wanted_count",
            "sonyc_wanted_count",
            "resolved_sha256_count",
            "missing_sha256_count",
            "failure_count",
            "status",
        )
    }
    summary["media_index"] = str(index_path)
    (report_dir / "rehydration-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, sort_keys=True))
    return 0 if index_payload["status"] == "COMPLETE" else 3


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Download a publisher metadata stage declared by the ECHO acquisition registry.

Only small metadata-stage bundles are intended for CI. Full multi-gigabyte audio
acquisition remains an explicit operator action outside hosted CI.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import time
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

from echo.data_foundry.acquisition import files_for_stage, load_acquisition_registry, md5_file
from echo.data_foundry.hashing import sha256_file


USER_AGENT = "ECHO-Data-Foundry/1.0 (+https://github.com/Em3rc0d/ECHO)"


def publisher_file_url(source: dict, filename: str) -> str:
    """Return Zenodo's published-record Files API content endpoint.

    The human-facing ``/records/<id>/files/...`` route can intermittently time
    out on automated runners.  Published record metadata exposes files via the
    public REST API, whose canonical content route is
    ``/api/records/<id>/files/<key>/content``.
    """

    record_url = str(source.get("record_url") or "").rstrip("/")
    parsed = urlparse(record_url)
    if parsed.netloc == "zenodo.org" and "/records/" in parsed.path:
        record_id = parsed.path.rstrip("/").split("/")[-1]
        if not record_id.isdigit():
            raise ValueError(f"invalid Zenodo record id in {record_url!r}")
        return f"https://zenodo.org/api/records/{record_id}/files/{quote(filename, safe='')}/content"
    explicit = source.get("download_base_url")
    if explicit:
        return f"{str(explicit).rstrip('/')}/{quote(filename, safe='')}"
    raise ValueError(f"no deterministic download route for source record {record_url!r}")


def _download(url: str, destination: Path, retries: int = 5) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(destination.suffix + ".part")
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            request = Request(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "application/octet-stream,*/*;q=0.8",
                },
            )
            with urlopen(request, timeout=60) as response, partial.open("wb") as handle:
                shutil.copyfileobj(response, handle, length=1024 * 1024)
                final_url = response.geturl()
            partial.replace(destination)
            return final_url
        except Exception as exc:  # network errors vary by runner/platform
            last_error = exc
            partial.unlink(missing_ok=True)
            if attempt < retries:
                time.sleep(min(2**attempt, 10))
    raise RuntimeError(f"download failed after {retries} attempts: {url}") from last_error


def fetch_stage(*, registry_path: str, source_id: str, stage: str, root: str) -> dict:
    registry = load_acquisition_registry(registry_path)
    source = registry["sources"].get(source_id)
    if source is None:
        raise KeyError(f"unknown source_id: {source_id}")
    if stage != "metadata":
        raise ValueError("hosted source-certification fetch is intentionally limited to metadata stage")

    out = Path(root)
    evidence: list[dict] = []
    for entry in files_for_stage(source, stage):
        filename = str(entry["name"])
        destination = out / filename
        expected_md5 = str(entry.get("md5") or "").lower() or None
        url = publisher_file_url(source, filename)

        reused = False
        final_url = url
        if destination.is_file() and expected_md5 and md5_file(destination) == expected_md5:
            reused = True
        else:
            destination.unlink(missing_ok=True)
            final_url = _download(url, destination)

        actual_md5 = md5_file(destination) if expected_md5 else None
        if expected_md5 and actual_md5 != expected_md5:
            destination.unlink(missing_ok=True)
            raise ValueError(
                f"publisher checksum mismatch for {source_id}/{filename}: "
                f"expected {expected_md5}, got {actual_md5}"
            )
        evidence.append(
            {
                "name": filename,
                "publisher_url": url,
                "final_url": final_url,
                "reused": reused,
                "size_bytes": destination.stat().st_size,
                "publisher_md5": expected_md5,
                "actual_md5": actual_md5,
                "sha256": sha256_file(destination),
            }
        )

    return {
        "schema_version": "echo.source-metadata-acquisition-evidence.v1",
        "source_id": source_id,
        "stage": stage,
        "record_url": source.get("record_url"),
        "status": "PASS",
        "files": evidence,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_id")
    parser.add_argument("root")
    parser.add_argument("--registry", default="configs/data_foundry/acquisition_registry.v1.json")
    parser.add_argument("--stage", default="metadata", choices=["metadata"])
    parser.add_argument("--report")
    args = parser.parse_args()

    result = fetch_stage(
        registry_path=args.registry,
        source_id=args.source_id,
        stage=args.stage,
        root=args.root,
    )
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.report:
        report = Path(args.report)
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

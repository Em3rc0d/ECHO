#!/usr/bin/env python3
"""Materialize a pinned independent CC0 acoustic source for MK1 gap closure.

The canonical rights/provenance authority is the OpenGameArt submission. A
pinned public GitHub mirror is used only as byte transport. The mirror never
creates source-diversity credit. Raw media stays in CI scratch; only evidence,
probes and canonical fingerprints are durable.

This script performs acquisition/evidence capture only. It does not admit any
row into the canonical corpus ledger.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import time
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from echo.data_foundry.canonical_fingerprints import canonical_audio_fingerprint
from echo.data_foundry.probe import probe_audio

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/data_foundry/opengameart_rubberduck_cc0.v1.json"
REPORT = ROOT / "MK1/mining-site/materialization/opengameart-rubberduck-cc0-materialization.json"
OUTPUT_ROOT = Path(
    os.environ.get(
        "ECHO_OPENGAMEART_CC0_ROOT",
        ROOT / ".materialized-opengameart-rubberduck-cc0",
    )
)

USER_AGENT = "ECHO-Data-Foundry/1.0 (+https://github.com/Em3rc0d/ECHO)"


def fetch(url: str, *, attempts: int = 6) -> tuple[bytes, str | None, str]:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
        try:
            with urlopen(request, timeout=120) as response:  # nosec B310 - governed public evidence URLs
                return response.read(), response.headers.get_content_type(), response.geturl()
        except HTTPError as exc:
            last_error = exc
            if exc.code not in {408, 425, 429, 500, 502, 503, 504}:
                raise
        except (URLError, TimeoutError) as exc:
            last_error = exc
        if attempt < attempts:
            time.sleep(min(20, 2 ** (attempt - 1)))
    raise RuntimeError(f"fetch failed after {attempts} attempts: {url}: {last_error}") from last_error


def normalize_html_text(raw: str) -> str:
    text = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", text).strip().casefold()


def canonical_page_evidence_ok(page_text: str, config: Mapping[str, Any]) -> tuple[bool, list[str]]:
    normalized = normalize_html_text(page_text)
    missing: list[str] = []
    creator = str(config.get("creator") or "").casefold()
    if creator and creator not in normalized:
        missing.append("CREATOR_MARKER_MISSING")
    if "cc0" not in normalized and "creative commons zero" not in normalized:
        missing.append("CC0_MARKER_MISSING")
    # Keep the authorship claim explicit. This protects source-family identity:
    # hosting/mirroring alone is never enough to claim an independent origin.
    if "i made 75 breaking, falling and hit sounds" not in normalized:
        missing.append("AUTHORSHIP_CLAIM_MISSING")
    return not missing, missing


def validate_config(config: Mapping[str, Any]) -> None:
    if config.get("declared_license") != "CC0":
        raise ValueError("OpenGameArt gap source must remain CC0 in this materializer")
    transport = config.get("acquisition_transport")
    if not isinstance(transport, Mapping):
        raise ValueError("acquisition_transport missing")
    commit = str(transport.get("commit") or "")
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("transport commit must be an exact 40-character SHA")
    directory = str(transport.get("directory") or "")
    if not directory or directory.startswith("/") or ".." in Path(directory).parts:
        raise ValueError("transport directory must be a safe relative path")

    assets = config.get("assets")
    if not isinstance(assets, list) or not assets:
        raise ValueError("assets must be a non-empty list")
    seen: set[str] = set()
    for row in assets:
        if not isinstance(row, Mapping):
            raise ValueError("asset row must be an object")
        path = str(row.get("path") or "")
        if not path.endswith(".ogg") or "/" in path or "\\" in path or path in seen:
            raise ValueError(f"invalid or duplicate asset path: {path}")
        seen.add(path)
        role = str(row.get("role") or "")
        if role not in {"positive_candidate", "hard_negative_candidate"}:
            raise ValueError(f"unsupported asset role: {role}")
        if role == "positive_candidate":
            if row.get("target") != "GLASS_SHATTER" or "glass_breaking" not in path:
                raise ValueError(f"positive candidate is not an explicit glass-breaking row: {path}")
        else:
            if list(row.get("confuses") or []) != ["GLASS_SHATTER"]:
                raise ValueError(f"hard-negative mapping must target GLASS_SHATTER only: {path}")
        if not str(row.get("recording_family") or ""):
            raise ValueError(f"recording_family missing: {path}")


def raw_transport_url(config: Mapping[str, Any], filename: str) -> str:
    transport = config["acquisition_transport"]
    repository = str(transport["repository"])
    commit = str(transport["commit"])
    directory = str(transport["directory"]).strip("/")
    return (
        "https://raw.githubusercontent.com/"
        f"{repository}/{commit}/{quote(directory)}/{quote(filename)}"
    )


def materialize_asset(config: Mapping[str, Any], row: Mapping[str, Any]) -> dict[str, Any]:
    filename = str(row["path"])
    url = raw_transport_url(config, filename)
    media_bytes, content_type, resolved_url = fetch(url)
    path = OUTPUT_ROOT / filename
    path.write_bytes(media_bytes)

    probe = probe_audio(path)
    if not probe.ok:
        raise RuntimeError(f"audio probe failed for {filename}: {probe.reason}")
    fingerprint = canonical_audio_fingerprint(path)
    return {
        "source_asset_id": filename,
        "source_dataset_candidate": config["source_id"],
        "underlying_source_family_candidate": config["underlying_source_family_candidate"],
        "role": row["role"],
        "target": row.get("target"),
        "confuses": list(row.get("confuses") or []),
        "semantic": row["semantic"],
        "recording_family": row["recording_family"],
        "license_id": "CC0",
        "canonical_source_page": config["canonical_source_page"],
        "transport_url": url,
        "resolved_transport_url": resolved_url,
        "transport_commit": config["acquisition_transport"]["commit"],
        "content_type": content_type,
        "media_sha256": hashlib.sha256(media_bytes).hexdigest(),
        "size_bytes": len(media_bytes),
        "audio_probe": probe.to_dict(),
        "canonical_fingerprint": fingerprint,
        "admission_status": "REAL_BYTES_MATERIALIZED_REVIEW_REQUIRED",
    }


def main() -> int:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    validate_config(config)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    page_bytes, _, resolved_page = fetch(str(config["canonical_source_page"]))
    page_text = page_bytes.decode("utf-8", errors="replace")
    page_ok, missing_markers = canonical_page_evidence_ok(page_text, config)
    if not page_ok:
        raise SystemExit(
            "canonical OpenGameArt rights/provenance evidence failed closed: "
            + ",".join(missing_markers)
        )

    rows: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    for asset in config["assets"]:
        try:
            rows.append(materialize_asset(config, asset))
        except Exception as exc:
            failures.append({
                "source_asset_id": str(asset.get("path") or ""),
                "error": f"{type(exc).__name__}:{exc}",
            })

    positives = [row for row in rows if row["role"] == "positive_candidate"]
    negatives = [row for row in rows if row["role"] == "hard_negative_candidate"]
    negative_groups = sorted({str(row["recording_family"]) for row in negatives})
    positive_groups = sorted({str(row["recording_family"]) for row in positives})

    payload = {
        "schema_version": "echo.opengameart-rubberduck-materialization.v1",
        "source_id": config["source_id"],
        "source_family_candidate": config["underlying_source_family_candidate"],
        "status": "PASS" if not failures and len(rows) == len(config["assets"]) else "PARTIAL",
        "canonical_source_evidence": {
            "url": config["canonical_source_page"],
            "resolved_url": resolved_page,
            "page_sha256": hashlib.sha256(page_bytes).hexdigest(),
            "creator": config["creator"],
            "license_id": config["declared_license"],
            "markers_pass": page_ok,
        },
        "transport_evidence": {
            "repository": config["acquisition_transport"]["repository"],
            "commit": config["acquisition_transport"]["commit"],
            "directory": config["acquisition_transport"]["directory"],
            "source_credit": false,
        },
        "materialized_count": len(rows),
        "fingerprinted_count": sum(1 for row in rows if (row.get("canonical_fingerprint") or {}).get("vector_sha256")),
        "positive_candidate_count": len(positives),
        "positive_candidate_group_count": len(positive_groups),
        "hard_negative_candidate_count": len(negatives),
        "hard_negative_candidate_group_count": len(negative_groups),
        "positive_candidate_groups": positive_groups,
        "hard_negative_candidate_groups": negative_groups,
        "assets": sorted(rows, key=lambda row: str(row["source_asset_id"])),
        "failures": failures,
        "certification_stop_line": (
            "PASS means real bytes/probe/fingerprint/provenance acquisition succeeded. "
            "It does not grant corpus admission, source-family certification, coverage credit, "
            "split membership or CERT-MK1-DF-CORPUS-001."
        ),
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "materialized": payload["materialized_count"],
        "fingerprinted": payload["fingerprinted_count"],
        "positive_candidates": payload["positive_candidate_count"],
        "hard_negative_candidates": payload["hard_negative_candidate_count"],
        "hard_negative_groups": payload["hard_negative_candidate_group_count"],
        "failures": len(failures),
    }, sort_keys=True))
    return 0 if payload["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())

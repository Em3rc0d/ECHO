"""Dataset materialization helpers for ECHO MK1.

The module intentionally separates discovery/materialization from corpus
admission. Downloaded bytes never become training data until the existing
Foundry admission, rights, semantic-review, dedup and coverage gates pass.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tarfile
from typing import Any, Iterable, Mapping
from urllib.request import Request, urlopen
import zipfile


@dataclass(frozen=True)
class MaterializedFile:
    source_id: str
    name: str
    path: str
    size_bytes: int
    md5_expected: str | None
    md5_actual: str
    verified: bool

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


def load_json_object(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"JSON object required: {path}")
    return payload


def validate_materialization_plan(plan: Mapping[str, Any]) -> None:
    if plan.get("schema_version") != "echo.materialization-plan.v1":
        raise ValueError("unsupported materialization plan schema")
    if not plan.get("plan_id"):
        raise ValueError("materialization plan requires plan_id")
    sources = plan.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("materialization plan requires sources")


def plan_summary(plan: Mapping[str, Any]) -> dict[str, Any]:
    validate_materialization_plan(plan)
    states: dict[str, int] = {}
    for row in plan["sources"].values():
        status = str(row.get("status") or "UNKNOWN")
        states[status] = states.get(status, 0) + 1
    return {
        "plan_id": plan["plan_id"],
        "source_count": len(plan["sources"]),
        "statuses": dict(sorted(states.items())),
        "completion_rule": plan.get("completion_rule"),
    }


def _md5(path: Path) -> str:
    digest = hashlib.md5()  # nosec B303 - publisher compatibility checksum only
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def zenodo_file_url(record_url: str, filename: str) -> str:
    base = record_url.rstrip("/")
    return f"{base}/files/{filename}?download=1"


def _download(url: str, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_suffix(target.suffix + ".part")
    existing = partial.stat().st_size if partial.exists() else 0
    headers = {"User-Agent": "ECHO-Data-Foundry/1.0"}
    if existing:
        headers["Range"] = f"bytes={existing}-"
    request = Request(url, headers=headers)
    mode = "ab" if existing else "wb"
    with urlopen(request, timeout=120) as response, partial.open(mode) as output:  # nosec B310 - URLs come from versioned source registry
        shutil.copyfileobj(response, output, length=1024 * 1024)
    partial.replace(target)


def files_for_stage(source: Mapping[str, Any], stage: str) -> list[Mapping[str, Any]]:
    if stage not in {"metadata", "full"}:
        raise ValueError("stage must be metadata or full")
    result = []
    for row in source.get("files", []):
        if stage in (row.get("required_for") or []):
            result.append(row)
    return result


def materialize_registered_source(
    *,
    source_id: str,
    acquisition_registry: Mapping[str, Any],
    root: str | Path,
    stage: str,
    allow_large_download: bool = False,
) -> list[MaterializedFile]:
    sources = acquisition_registry.get("sources", {})
    source = sources.get(source_id)
    if not isinstance(source, Mapping):
        raise KeyError(source_id)
    rows = files_for_stage(source, stage)
    if stage == "full" and not allow_large_download:
        raise ValueError("full materialization requires explicit allow_large_download=True")
    if source.get("manual_download_required"):
        raise RuntimeError(f"{source_id} requires authorized/manual acquisition")
    record_url = str(source.get("record_url") or "")
    if "zenodo.org/records/" not in record_url:
        raise RuntimeError(f"automatic materialization is not implemented for {source_id}")

    source_root = Path(root) / "raw" / source_id
    results: list[MaterializedFile] = []
    for row in rows:
        name = str(row["name"])
        target = source_root / name
        if not target.exists():
            _download(zenodo_file_url(record_url, name), target)
        actual = _md5(target)
        expected = str(row.get("md5") or "") or None
        verified = expected is None or actual.casefold() == expected.casefold()
        if not verified:
            raise ValueError(f"publisher checksum mismatch: {source_id}/{name}")
        results.append(
            MaterializedFile(
                source_id=source_id,
                name=name,
                path=str(target),
                size_bytes=target.stat().st_size,
                md5_expected=expected,
                md5_actual=actual,
                verified=verified,
            )
        )
    return results


def ensure_free_space(root: str | Path, minimum_free_bytes: int) -> None:
    Path(root).mkdir(parents=True, exist_ok=True)
    free = shutil.disk_usage(root).free
    if free < minimum_free_bytes:
        raise RuntimeError(
            f"insufficient persistent storage: free={free} required={minimum_free_bytes}"
        )


def extract_source_archives(source_root: str | Path, output_root: str | Path) -> list[str]:
    """Extract complete source archives after checksum verification.

    Multipart ZIP sets require 7z/7zz. Ordinary ZIP and tar.gz use stdlib.
    Extraction is deliberately explicit and never deletes publisher archives.
    """
    source_root = Path(source_root)
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    extracted: list[str] = []

    multipart_terminals = []
    for archive in sorted(source_root.glob("*.zip")):
        stem = archive.with_suffix("")
        if any(source_root.glob(stem.name + ".z[0-9][0-9]")):
            multipart_terminals.append(archive)
        else:
            with zipfile.ZipFile(archive) as zf:
                zf.extractall(output_root)
            extracted.append(str(archive))

    seven_zip = shutil.which("7zz") or shutil.which("7z")
    for archive in multipart_terminals:
        if not seven_zip:
            raise RuntimeError("multipart ZIP extraction requires 7z or 7zz")
        subprocess.run(
            [seven_zip, "x", "-y", f"-o{output_root}", str(archive)],
            check=True,
        )
        extracted.append(str(archive))

    for archive in sorted(source_root.glob("*.tar.gz")):
        with tarfile.open(archive, "r:gz") as tf:
            tf.extractall(output_root, filter="data")
        extracted.append(str(archive))
    return extracted


def write_materialization_report(path: str | Path, rows: Iterable[MaterializedFile]) -> str:
    payload = {
        "schema_version": "echo.materialization-report.v1",
        "files": [row.to_dict() for row in rows],
    }
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

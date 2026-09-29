"""Pinned auxiliary assets required by panns-inference 0.1.1."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import tempfile
from urllib.request import Request, urlopen

PANNS_LABELS_COMMIT = "b28b633fa531467e99811d3da6b27f6b505f9b69"
PANNS_LABELS_GIT_BLOB_SHA1 = "3a2767e81114adecde59992cf6607f31c1862f4c"
PANNS_LABELS_URL = (
    "https://raw.githubusercontent.com/qiuqiangkong/"
    "audioset_tagging_cnn/"
    f"{PANNS_LABELS_COMMIT}/metadata/class_labels_indices.csv"
)


def _git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()  # nosec B324 - Git identity


def _validate_labels_bytes(data: bytes) -> None:
    actual = _git_blob_sha1(data)
    if actual != PANNS_LABELS_GIT_BLOB_SHA1:
        raise RuntimeError(
            "PANNs AudioSet labels identity mismatch: "
            f"{actual} != {PANNS_LABELS_GIT_BLOB_SHA1}"
        )

    text = data.decode("utf-8")
    lines = [line for line in text.splitlines() if line]
    if not lines or lines[0] != "index,mid,display_name":
        raise RuntimeError("PANNs AudioSet labels header mismatch")
    if len(lines) != 528:
        raise RuntimeError(
            f"PANNs AudioSet labels row-count mismatch: {len(lines) - 1} != 527"
        )


def ensure_panns_labels(path: Path | None = None) -> Path:
    """Ensure panns-inference's implicit AudioSet label file exists exactly.

    panns-inference 0.1.1 shells out to wget at import time when this file is
    absent, which is not portable to a default Windows environment. ECHO
    materializes the same upstream file with Python and verifies the pinned Git
    blob identity before import.
    """
    target = path or (Path.home() / "panns_data" / "class_labels_indices.csv")

    if target.is_file():
        data = target.read_bytes()
        try:
            _validate_labels_bytes(data)
            return target
        except RuntimeError:
            # Replace stale/partial upstream side-effect output atomically.
            pass

    target.parent.mkdir(parents=True, exist_ok=True)
    request = Request(
        PANNS_LABELS_URL,
        headers={"User-Agent": "ECHO-MVP-001/panns-label-bootstrap"},
    )
    with urlopen(request, timeout=60) as response:  # nosec B310 - pinned HTTPS URL
        data = response.read()

    _validate_labels_bytes(data)

    with tempfile.NamedTemporaryFile(
        mode="wb",
        dir=target.parent,
        prefix=target.name + ".",
        suffix=".part",
        delete=False,
    ) as handle:
        handle.write(data)
        temp_path = Path(handle.name)

    try:
        os.replace(temp_path, target)
    finally:
        if temp_path.exists():
            temp_path.unlink()

    return target

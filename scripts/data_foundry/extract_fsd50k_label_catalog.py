#!/usr/bin/env python3
"""Extract the full released FSD50K label/count catalog from pinned ground truth."""

from __future__ import annotations

from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import shutil
import time
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "configs/data_foundry/acquisition_registry.v1.json"
SOURCE_ID = "fsd50k-1.0"
UA = "ECHO-Data-Foundry/1.0 (+https://github.com/Em3rc0d/ECHO)"


def digest(path: Path, algo: str) -> str:
    h = hashlib.new(algo)
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def url(record_url: str, filename: str) -> str:
    record_id = urlparse(record_url).path.rstrip("/").split("/")[-1]
    return f"https://zenodo.org/api/records/{record_id}/files/{quote(filename, safe='')}/content"


def download(source_url: str, target: Path) -> None:
    last = None
    for attempt in range(5):
        try:
            req = Request(source_url, headers={"User-Agent": UA})
            with urlopen(req, timeout=180) as r, target.open("wb") as out:  # nosec B310
                shutil.copyfileobj(r, out, length=1024 * 1024)
            return
        except Exception as exc:
            last = exc
            target.unlink(missing_ok=True)
            if attempt < 4:
                time.sleep(min(16, 2 ** attempt))
    raise RuntimeError(last)


def main() -> int:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--work-root", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    reg = json.loads(REGISTRY.read_text())
    source = reg["sources"][SOURCE_ID]
    entry = next(row for row in source["files"] if row["name"] == "FSD50K.ground_truth.zip")
    work = Path(a.work_root); work.mkdir(parents=True, exist_ok=True)
    archive = work / entry["name"]
    download(url(source["record_url"], entry["name"]), archive)
    if digest(archive, "md5").casefold() != str(entry["md5"]).casefold():
        raise SystemExit("publisher checksum mismatch")

    counts = Counter()
    split_counts: dict[str, Counter[str]] = defaultdict(Counter)
    with zipfile.ZipFile(archive) as zf:
        for member in ("FSD50K.ground_truth/dev.csv", "FSD50K.ground_truth/eval.csv"):
            reader = csv.DictReader(io.StringIO(zf.read(member).decode("utf-8-sig")))
            for row in reader:
                split = str(row.get("split") or ("eval" if member.endswith("eval.csv") else "unknown"))
                for label in (x.strip() for x in str(row.get("labels") or "").split(",")):
                    if label:
                        counts[label] += 1
                        split_counts[label][split] += 1
    payload = {
        "schema_version": "echo.fsd50k-label-catalog.v1",
        "status": "PASS",
        "source_id": SOURCE_ID,
        "source_release": "1.0",
        "ground_truth_sha256": digest(archive, "sha256"),
        "label_count": len(counts),
        "labels": [
            {"label": label, "count": counts[label], "split_counts": dict(sorted(split_counts[label].items()))}
            for label in sorted(counts)
        ],
    }
    out = Path(a.output); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"labels": len(counts), "status": "PASS"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

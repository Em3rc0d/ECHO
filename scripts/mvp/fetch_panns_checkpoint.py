#!/usr/bin/env python3
"""Fetch the pinned PANNs Cnn14 AudioSet checkpoint for ECHO Benchmark B."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

URL = "https://zenodo.org/records/3987831/files/Cnn14_mAP%3D0.431.pth?download=1"
SHA256 = "0dc499e40e9761ef5ea061ffc77697697f277f6a960894903df3ada000e34b31"
SIZE_BYTES = 327_428_481
USER_AGENT = "ECHO-MVP/1.0 (+https://github.com/Em3rc0d/ECHO)"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/models/panns/Cnn14_mAP=0.431.pth"),
    )
    args = parser.parse_args()

    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    if output.is_file():
        digest = sha256_file(output)
        if digest == SHA256 and output.stat().st_size == SIZE_BYTES:
            print(f"PANNs checkpoint already verified: {output}")
            return 0
        output.unlink()

    part = output.with_suffix(output.suffix + ".part")
    last = None
    for attempt in range(1, 6):
        h = hashlib.sha256()
        size = 0
        try:
            request = Request(
                URL,
                headers={"User-Agent": USER_AGENT, "Accept": "application/octet-stream"},
            )
            with urlopen(request, timeout=180) as response, part.open("wb") as out:  # nosec B310
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    h.update(chunk)
                    size += len(chunk)
                    out.write(chunk)
            digest = h.hexdigest()
            if digest != SHA256:
                raise RuntimeError(f"SHA-256 mismatch: {digest} != {SHA256}")
            if size != SIZE_BYTES:
                raise RuntimeError(f"size mismatch: {size} != {SIZE_BYTES}")
            part.replace(output)
            print(f"PANNs checkpoint verified: {output}")
            print(f"sha256={digest} bytes={size}")
            return 0
        except (HTTPError, URLError, TimeoutError, OSError, RuntimeError) as exc:
            last = exc
            part.unlink(missing_ok=True)
            if attempt < 5:
                time.sleep(min(20, 2 ** (attempt - 1)))

    raise SystemExit(f"PANNs checkpoint download failed: {last}")


if __name__ == "__main__":
    raise SystemExit(main())

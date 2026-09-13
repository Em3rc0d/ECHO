from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from echo.data_foundry.acquisition import (
    files_for_stage,
    load_acquisition_registry,
    verification_summary,
    verify_source_release,
)


class AcquisitionTests(unittest.TestCase):
    def test_stage_filters_files(self) -> None:
        source = {
            "files": [
                {"name": "meta.csv", "required_for": ["metadata", "full"]},
                {"name": "audio.zip", "required_for": ["full"]},
            ]
        }
        self.assertEqual([row["name"] for row in files_for_stage(source, "metadata")], ["meta.csv"])
        self.assertEqual(
            [row["name"] for row in files_for_stage(source, "full")],
            ["meta.csv", "audio.zip"],
        )

    def test_verify_publisher_md5(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = b"publisher-bundle-bytes"
            (root / "meta.csv").write_bytes(payload)
            expected = hashlib.md5(payload, usedforsecurity=False).hexdigest()
            registry = {
                "schema_version": "echo.acquisition-registry.v1",
                "sources": {
                    "source": {
                        "files": [
                            {
                                "name": "meta.csv",
                                "md5": expected,
                                "required_for": ["metadata", "full"],
                            }
                        ]
                    }
                },
            }
            result = verify_source_release(
                registry=registry,
                source_id="source",
                root=root,
                stage="metadata",
            )
            self.assertTrue(result[0].checksum_ok)
            self.assertEqual(verification_summary(result)["status"], "PASS")

    def test_missing_file_fails_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            registry = {
                "schema_version": "echo.acquisition-registry.v1",
                "sources": {
                    "source": {
                        "files": [
                            {
                                "name": "missing.csv",
                                "md5": "0" * 32,
                                "required_for": ["metadata"],
                            }
                        ]
                    }
                },
            }
            result = verify_source_release(
                registry=registry,
                source_id="source",
                root=tmp,
                stage="metadata",
            )
            summary = verification_summary(result)
            self.assertEqual(summary["status"], "FAIL")
            self.assertEqual(summary["missing_files"], ["missing.csv"])

    def test_real_registry_loads(self) -> None:
        path = Path("configs/data_foundry/acquisition_registry.v1.json")
        if path.exists():
            registry = load_acquisition_registry(path)
            self.assertIn("fsd50k-1.0", registry["sources"])
            self.assertIn("sonyc-ust-v2", registry["sources"])
            self.assertIn("singapura-v1.0a", registry["sources"])


if __name__ == "__main__":
    unittest.main()

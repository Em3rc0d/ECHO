from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from echo.data_foundry.acquisition import load_acquisition_registry
from echo.data_foundry.publisher_snapshot import load_snapshot, verify_snapshot
from echo.data_foundry.source_policy import load_dataset_certification


class PublisherSnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.acquisition = load_acquisition_registry("configs/data_foundry/acquisition_registry.v1.json")
        cls.certification = load_dataset_certification("configs/data_foundry/dataset_certification.v1.json")
        cls.source_registry = json.loads(Path("configs/data_foundry/source_registry.v1.json").read_text(encoding="utf-8"))

    def _snapshot(self, source_id: str) -> dict:
        return load_snapshot(f"configs/data_foundry/publisher_snapshots/{source_id}.json")

    def test_all_pinned_snapshots_match_registries(self) -> None:
        for source_id in ("fsd50k-1.0", "sonyc-ust-v2", "singapura-v1.0a"):
            with self.subTest(source_id=source_id):
                result = verify_snapshot(
                    source_id=source_id,
                    snapshot=self._snapshot(source_id),
                    acquisition_registry=self.acquisition,
                    certification_policy=self.certification,
                    source_registry=self.source_registry,
                )
                self.assertEqual(result["status"], "PASS")
                self.assertGreater(result["file_count"], 0)

    def test_checksum_drift_fails_closed(self) -> None:
        snapshot = copy.deepcopy(self._snapshot("fsd50k-1.0"))
        snapshot["files"][0]["md5"] = "0" * 32
        with self.assertRaises(ValueError):
            verify_snapshot(
                source_id="fsd50k-1.0",
                snapshot=snapshot,
                acquisition_registry=self.acquisition,
                certification_policy=self.certification,
                source_registry=self.source_registry,
            )

    def test_missing_publisher_file_fails_closed(self) -> None:
        snapshot = copy.deepcopy(self._snapshot("sonyc-ust-v2"))
        snapshot["files"] = snapshot["files"][:-1]
        with self.assertRaises(ValueError):
            verify_snapshot(
                source_id="sonyc-ust-v2",
                snapshot=snapshot,
                acquisition_registry=self.acquisition,
                certification_policy=self.certification,
                source_registry=self.source_registry,
            )


if __name__ == "__main__":
    unittest.main()

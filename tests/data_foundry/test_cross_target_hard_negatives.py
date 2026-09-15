from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from scripts.data_foundry.enrich_canonical_asset_ledger import (
    CROSS_TARGET_SEMANTIC_STATUS,
    HARD_NEGATIVE_MAPPING,
    apply_cross_target_hard_negatives,
    load_cross_target_confusers,
)


class CrossTargetHardNegativeTests(unittest.TestCase):
    def base_row(self, label: str) -> dict:
        return {
            "ledger_asset_id": f"test:{label.lower()}",
            "rights_status": "ALLOW_RELEASE_SAFE",
            "echo_labels": [label],
            "hard_negative_for": [],
            "candidate_targets": [label],
            "semantic_status_by_target": {label: "EXACT"},
            "label_provenance": ["TEST_EXACT_POSITIVE"],
            "canonical_fingerprint": {"vector_sha256": "a" * 64},
        }

    def test_frozen_mapping_is_narrow_and_directional(self) -> None:
        mapping = load_cross_target_confusers(HARD_NEGATIVE_MAPPING)
        self.assertEqual(mapping["SIREN"], ("FIRE_ALARM", "VEHICLE_HORN"))
        self.assertEqual(mapping["VEHICLE_HORN"], ("SIREN",))
        self.assertEqual(set(mapping), {"SIREN", "VEHICLE_HORN"})

    def test_siren_positive_is_preserved_while_confuser_roles_are_added(self) -> None:
        row = self.base_row("SIREN")
        attached = apply_cross_target_hard_negatives(row, load_cross_target_confusers())
        self.assertEqual(attached, 2)
        self.assertEqual(row["echo_labels"], ["SIREN"])
        self.assertEqual(row["hard_negative_for"], ["FIRE_ALARM", "VEHICLE_HORN"])
        self.assertEqual(row["semantic_status_by_target"]["FIRE_ALARM"], CROSS_TARGET_SEMANTIC_STATUS)
        self.assertEqual(row["semantic_status_by_target"]["VEHICLE_HORN"], CROSS_TARGET_SEMANTIC_STATUS)

    def test_vehicle_horn_positive_is_preserved_as_siren_confuser(self) -> None:
        row = self.base_row("VEHICLE_HORN")
        attached = apply_cross_target_hard_negatives(row, load_cross_target_confusers())
        self.assertEqual(attached, 1)
        self.assertEqual(row["echo_labels"], ["VEHICLE_HORN"])
        self.assertEqual(row["hard_negative_for"], ["SIREN"])

    def test_non_release_safe_row_gets_no_cross_target_credit(self) -> None:
        row = self.base_row("SIREN")
        row["rights_status"] = "REVIEW_REQUIRED"
        original = copy.deepcopy(row)
        self.assertEqual(apply_cross_target_hard_negatives(row, load_cross_target_confusers()), 0)
        self.assertEqual(row, original)

    def test_missing_fingerprint_gets_no_cross_target_credit(self) -> None:
        row = self.base_row("SIREN")
        row["canonical_fingerprint"] = None
        original = copy.deepcopy(row)
        self.assertEqual(apply_cross_target_hard_negatives(row, load_cross_target_confusers()), 0)
        self.assertEqual(row, original)

    def test_same_target_mapping_fails_closed(self) -> None:
        payload = json.loads(Path(HARD_NEGATIVE_MAPPING).read_text(encoding="utf-8"))
        payload["cross_target_exact_positive_confusers"]["SIREN"].append("SIREN")
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "mapping.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "same-target"):
                load_cross_target_confusers(path)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import unittest
from pathlib import Path

from echo.data_foundry.coverage_policy import evaluate_coverage, load_coverage_policy
from echo.data_foundry.contracts import TARGET_LABELS


class CoveragePolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = load_coverage_policy("configs/data_foundry/coverage_policy.v1.json")

    def _solid_rows(self) -> list[dict]:
        rows: list[dict] = []
        splits = [("train", 10), ("validation", 5), ("test", 10)]
        for label in TARGET_LABELS:
            group_index = 0
            for split, groups in splits:
                for _ in range(groups):
                    source = "source-a" if group_index % 2 == 0 else "source-b"
                    group = f"{label}:group:{group_index}"
                    for asset_index in range(2):
                        rows.append({
                            "asset_id": f"{label}:{group_index}:{asset_index}",
                            "source_dataset": source,
                            "source_release": "1",
                            "recording_group_id": group,
                            "echo_labels": [label],
                            "echo_split": split,
                            "duration_seconds": 4.0,
                            "field_holdout": False,
                        })
                    group_index += 1

        for group_index in range(100):
            source = f"neg-source-{group_index % 4}"
            group = f"negative:group:{group_index}"
            split = ("train", "validation", "test")[group_index % 3]
            for asset_index in range(2):
                rows.append({
                    "asset_id": f"negative:{group_index}:{asset_index}",
                    "source_dataset": source,
                    "source_release": "1",
                    "recording_group_id": group,
                    "echo_labels": [],
                    "echo_split": split,
                    "duration_seconds": 4.0,
                    "field_holdout": False,
                })
        return rows

    def test_release_safe_floor_passes_only_with_diverse_complete_corpus(self) -> None:
        result = evaluate_coverage(self._solid_rows(), policy=self.policy, profile="release_safe")
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["gap_codes"], [])
        for label in TARGET_LABELS:
            self.assertGreaterEqual(result["classes"][label]["source_count"], 2)
            self.assertGreaterEqual(result["classes"][label]["independent_group_count"], 25)

    def test_one_missing_target_fails_closed(self) -> None:
        rows = [row for row in self._solid_rows() if "FIRE_ALARM" not in row.get("echo_labels", [])]
        result = evaluate_coverage(rows, policy=self.policy, profile="release_safe")
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("FIRE_ALARM_ASSETS_BELOW_MIN", result["gap_codes"])
        self.assertIn("FIRE_ALARM_SOURCES_BELOW_MIN", result["gap_codes"])

    def test_field_holdout_cannot_hide_development_gap(self) -> None:
        rows = [row for row in self._solid_rows() if "TIRE_SQUEAL" not in row.get("echo_labels", [])]
        for index in range(60):
            rows.append({
                "asset_id": f"holdout:tire:{index}",
                "source_dataset": "echo-field-v1",
                "source_release": "future-v1",
                "recording_group_id": f"field:{index}",
                "echo_labels": ["TIRE_SQUEAL"],
                "echo_split": "field_holdout",
                "duration_seconds": 5.0,
                "field_holdout": True,
            })
        result = evaluate_coverage(rows, policy=self.policy, profile="release_safe")
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("TIRE_SQUEAL_ASSETS_BELOW_MIN", result["gap_codes"])
        self.assertEqual(result["field_holdout_excluded_count"], 60)

    def test_policy_file_is_versioned_json(self) -> None:
        payload = json.loads(Path("configs/data_foundry/coverage_policy.v1.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["schema_version"], "echo.coverage-policy.v1")
        self.assertEqual(payload["policy_id"], "MK1-CORPUS-SOLIDITY-001")


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from echo.data_foundry.coverage_policy import evaluate_coverage, load_coverage_policy
from echo.data_foundry.contracts import TARGET_LABELS


class CoveragePolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = load_coverage_policy("configs/data_foundry/coverage_policy.v1.json")

    def _quality_fields(self, asset_id: str, *, confuses: list[str] | None = None) -> dict:
        extra: dict = {"audio_probe": {"ok": True}}
        if confuses is not None:
            extra["confuses"] = confuses
        return {
            "sha256": hashlib.sha256(asset_id.encode("utf-8")).hexdigest(),
            "license_id": "CC-BY-4.0",
            "label_provenance": "synthetic_test_fixture",
            "extra": extra,
        }

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
                        asset_id = f"{label}:{group_index}:{asset_index}"
                        rows.append({
                            "asset_id": asset_id,
                            "source_dataset": source,
                            "source_release": "1",
                            "recording_group_id": group,
                            "echo_labels": [label],
                            "echo_split": split,
                            "duration_seconds": 4.0,
                            "field_holdout": False,
                            **self._quality_fields(asset_id),
                        })
                    group_index += 1

        for group_index in range(100):
            source = f"neg-source-{group_index % 4}"
            group = f"negative:group:{group_index}"
            split = ("train", "validation", "test")[group_index % 3]
            for asset_index in range(2):
                asset_id = f"negative:{group_index}:{asset_index}"
                rows.append({
                    "asset_id": asset_id,
                    "source_dataset": source,
                    "source_release": "1",
                    "recording_group_id": group,
                    "echo_labels": [],
                    "echo_split": split,
                    "duration_seconds": 4.0,
                    "field_holdout": False,
                    **self._quality_fields(asset_id, confuses=list(TARGET_LABELS)),
                })
        return rows

    def test_release_safe_floor_passes_only_with_diverse_complete_corpus(self) -> None:
        result = evaluate_coverage(self._solid_rows(), policy=self.policy, profile="release_safe")
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["gap_codes"], [])
        self.assertEqual(result["asset_quality"]["exact_duplicate_groups"], 0)
        self.assertEqual(result["asset_quality"]["near_duplicate_groups"], 0)
        for label in TARGET_LABELS:
            self.assertGreaterEqual(result["classes"][label]["source_count"], 2)
            self.assertGreaterEqual(result["classes"][label]["independent_group_count"], 25)
            self.assertGreaterEqual(result["classes"][label]["hard_negatives"]["source_count"], 2)

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

    def test_generic_background_cannot_replace_explicit_hard_negatives(self) -> None:
        rows = self._solid_rows()
        for row in rows:
            if not row.get("echo_labels"):
                row["extra"]["confuses"] = [
                    label for label in TARGET_LABELS if label != "FIRE_ALARM"
                ]
        result = evaluate_coverage(rows, policy=self.policy, profile="release_safe")
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("FIRE_ALARM_HARD_NEGATIVE_ASSETS_BELOW_MIN", result["gap_codes"])

    def test_positive_for_one_target_can_be_hard_negative_for_another(self) -> None:
        rows = self._solid_rows()

        # Remove VEHICLE_HORN confuser credit from all target-free negatives so
        # the horn HN floor can only be closed by exact SIREN positives.
        for row in rows:
            if not row.get("echo_labels"):
                row["extra"]["confuses"] = [
                    label for label in row["extra"]["confuses"]
                    if label != "VEHICLE_HORN"
                ]

        # Ten SIREN recording groups x two assets, alternating two sources,
        # satisfy the existing horn HN floor without changing SIREN positives.
        siren_rows = [row for row in rows if row.get("echo_labels") == ["SIREN"]][:20]
        self.assertEqual(len({row["recording_group_id"] for row in siren_rows}), 10)
        self.assertEqual(len({row["source_dataset"] for row in siren_rows}), 2)
        for row in siren_rows:
            row["extra"]["confuses"] = ["VEHICLE_HORN"]

        result = evaluate_coverage(rows, policy=self.policy, profile="release_safe")
        self.assertEqual(result["status"], "PASS")
        horn_hn = result["classes"]["VEHICLE_HORN"]["hard_negatives"]
        self.assertEqual(horn_hn["asset_count"], 20)
        self.assertEqual(horn_hn["independent_group_count"], 10)
        self.assertEqual(horn_hn["source_count"], 2)
        # Positive-bearing cross-target confusers are not generic background.
        self.assertEqual(result["background"]["asset_count"], 200)
        self.assertEqual(result["background"]["independent_group_count"], 100)

    def test_same_target_positive_cannot_receive_hard_negative_credit(self) -> None:
        rows = self._solid_rows()

        # Remove pure-negative SIREN credit, then try to replace it by marking
        # SIREN positives as SIREN confusers. Same-target credit must be ignored.
        for row in rows:
            if not row.get("echo_labels"):
                row["extra"]["confuses"] = [
                    label for label in row["extra"]["confuses"]
                    if label != "SIREN"
                ]
        for row in [row for row in rows if row.get("echo_labels") == ["SIREN"]][:20]:
            row["extra"]["confuses"] = ["SIREN"]

        result = evaluate_coverage(rows, policy=self.policy, profile="release_safe")
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("SIREN_HARD_NEGATIVE_ASSETS_BELOW_MIN", result["gap_codes"])
        self.assertEqual(result["classes"]["SIREN"]["hard_negatives"]["asset_count"], 0)

    def test_exact_duplicates_fail_solidity_gate(self) -> None:
        rows = self._solid_rows()
        rows[1]["sha256"] = rows[0]["sha256"]
        result = evaluate_coverage(rows, policy=self.policy, profile="release_safe")
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("EXACT_DUPLICATE_GROUPS_ABOVE_MAX", result["gap_codes"])

    def test_missing_technical_provenance_fails_gate(self) -> None:
        rows = self._solid_rows()
        rows[0]["extra"].pop("audio_probe")
        rows[1]["label_provenance"] = None
        result = evaluate_coverage(rows, policy=self.policy, profile="release_safe")
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("ASSETS_WITHOUT_VALID_AUDIO_PROBE", result["gap_codes"])
        self.assertIn("ASSETS_WITHOUT_LABEL_PROVENANCE", result["gap_codes"])

    def test_policy_file_is_versioned_json(self) -> None:
        payload = json.loads(Path("configs/data_foundry/coverage_policy.v1.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["schema_version"], "echo.coverage-policy.v1")
        self.assertEqual(payload["policy_id"], "MK1-CORPUS-SOLIDITY-001")


if __name__ == "__main__":
    unittest.main()

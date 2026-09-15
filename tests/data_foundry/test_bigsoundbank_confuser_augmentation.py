from __future__ import annotations

import unittest

from scripts.data_foundry.augment_canonical_ledger_with_bigsoundbank_confusers import governed_roles


MAPPING = {
    "targets": {
        "TIRE_SQUEAL": {
            "source_labels": [
                "Squeak",
                "Accelerating_and_revving_and_vroom",
                "Car_passing_by",
                "Car",
            ]
        }
    }
}


class BigSoundBankConfuserAugmentationTests(unittest.TestCase):
    def test_accepts_exact_governed_tire_confuser(self) -> None:
        config = {
            "semantic": "Car_passing_by",
            "hard_negative_for": ["TIRE_SQUEAL"],
        }
        report = {
            "semantic": "Car_passing_by",
            "hard_negative_for": ["TIRE_SQUEAL"],
        }
        ledger = {"echo_labels": []}

        self.assertEqual(
            governed_roles(config, report, ledger, MAPPING),
            ["TIRE_SQUEAL"],
        )

    def test_rejects_config_report_role_mismatch(self) -> None:
        config = {
            "semantic": "Car",
            "hard_negative_for": ["TIRE_SQUEAL"],
        }
        report = {
            "semantic": "Car",
            "hard_negative_for": [],
        }
        ledger = {"echo_labels": []}

        with self.assertRaisesRegex(ValueError, "role mismatch"):
            governed_roles(config, report, ledger, MAPPING)

    def test_rejects_semantic_outside_frozen_mapping(self) -> None:
        config = {
            "semantic": "Road_noise",
            "hard_negative_for": ["TIRE_SQUEAL"],
        }
        report = {
            "semantic": "Road_noise",
            "hard_negative_for": ["TIRE_SQUEAL"],
        }
        ledger = {"echo_labels": []}

        with self.assertRaisesRegex(ValueError, "not frozen"):
            governed_roles(config, report, ledger, MAPPING)

    def test_rejects_same_target_positive_overlap(self) -> None:
        config = {
            "semantic": "Car",
            "hard_negative_for": ["TIRE_SQUEAL"],
        }
        report = {
            "semantic": "Car",
            "hard_negative_for": ["TIRE_SQUEAL"],
        }
        ledger = {"echo_labels": ["TIRE_SQUEAL"]}

        with self.assertRaisesRegex(ValueError, "positive target"):
            governed_roles(config, report, ledger, MAPPING)

    def test_rejects_config_report_semantic_mismatch(self) -> None:
        config = {
            "semantic": "Car",
            "hard_negative_for": ["TIRE_SQUEAL"],
        }
        report = {
            "semantic": "Car_passing_by",
            "hard_negative_for": ["TIRE_SQUEAL"],
        }
        ledger = {"echo_labels": []}

        with self.assertRaisesRegex(ValueError, "semantic mismatch"):
            governed_roles(config, report, ledger, MAPPING)


if __name__ == "__main__":
    unittest.main()

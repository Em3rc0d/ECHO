from __future__ import annotations

import unittest

from scripts.data_foundry.build_canonical_asset_ledger import confuser_targets_for_asset


class CanonicalAssetLedgerBuilderTests(unittest.TestCase):
    def test_positive_label_cannot_be_reused_as_hard_negative_for_same_asset(self) -> None:
        entries = {
            "sonyc-ust-v2:clip.wav": {
                "echo_labels": ["SIREN"],
            }
        }
        result = confuser_targets_for_asset(
            entries,
            source_dataset="sonyc-ust-v2",
            source_asset_id="clip.wav",
            confuses=["FIRE_ALARM", "SIREN"],
        )
        self.assertEqual(result, ["FIRE_ALARM"])

    def test_confuser_roles_are_kept_when_target_is_not_positive(self) -> None:
        entries = {
            "sonyc-ust-v2:clip.wav": {
                "echo_labels": ["VEHICLE_HORN"],
            }
        }
        result = confuser_targets_for_asset(
            entries,
            source_dataset="sonyc-ust-v2",
            source_asset_id="clip.wav",
            confuses=["FIRE_ALARM", "SIREN"],
        )
        self.assertEqual(result, ["FIRE_ALARM", "SIREN"])

    def test_unknown_targets_never_enter_hard_negative_roles(self) -> None:
        result = confuser_targets_for_asset(
            {},
            source_dataset="sonyc-ust-v2",
            source_asset_id="clip.wav",
            confuses=["SIREN", "NOT_AN_ECHO_TARGET"],
        )
        self.assertEqual(result, ["SIREN"])


if __name__ == "__main__":
    unittest.main()

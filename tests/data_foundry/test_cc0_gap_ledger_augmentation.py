from __future__ import annotations

import unittest

from scripts.data_foundry.augment_canonical_ledger_with_cc0_gaps import (
    CANONICAL_SOURCE_ID,
    semantic_decision,
)


class CC0GapLedgerAugmentationTests(unittest.TestCase):
    def test_cc0_gap_path_reuses_existing_freesound_canonical_source(self) -> None:
        self.assertEqual(CANONICAL_SOURCE_ID, "echo-freesound-release-safe-v1")

    def test_explicit_fire_alarm_is_exact(self) -> None:
        semantic, exact, family, blockers = semantic_decision(
            sound_id=82797,
            report_target="FIRE_ALARM",
            report_semantic="exact_taxonomy_candidate_review_required",
            supplemental={
                82797: {
                    "target": "FIRE_ALARM",
                    "semantic": "fire_alarm",
                    "recording_family": "payattention-fire-alarm-building-announcement",
                }
            },
        )
        self.assertEqual(semantic, "fire_alarm")
        self.assertTrue(exact)
        self.assertEqual(family, "payattention-fire-alarm-building-announcement")
        self.assertEqual(blockers, [])

    def test_explicit_tire_squeal_is_exact(self) -> None:
        semantic, exact, family, blockers = semantic_decision(
            sound_id=350677,
            report_target="TIRE_SQUEAL",
            report_semantic="exact_taxonomy_candidate_review_required",
            supplemental={
                350677: {
                    "target": "TIRE_SQUEAL",
                    "semantic": "tire_squeal",
                    "recording_family": "Nordschleife-tyre-squeal-02",
                }
            },
        )
        self.assertTrue(exact)
        self.assertEqual(semantic, "tire_squeal")
        self.assertEqual(family, "Nordschleife-tyre-squeal-02")
        self.assertEqual(blockers, [])

    def test_temporal_review_candidate_does_not_become_positive(self) -> None:
        semantic, exact, _, blockers = semantic_decision(
            sound_id=233557,
            report_target="TIRE_SQUEAL",
            report_semantic="exact_taxonomy_candidate_review_required",
            supplemental={
                233557: {
                    "target": "TIRE_SQUEAL",
                    "semantic": "contains_tire_squeal_temporal_review_required",
                    "recording_family": "car-screech-233557",
                }
            },
        )
        self.assertEqual(semantic, "contains_tire_squeal_temporal_review_required")
        self.assertFalse(exact)
        self.assertEqual(blockers, [])

    def test_license_text_conflict_fails_closed(self) -> None:
        semantic, exact, _, blockers = semantic_decision(
            sound_id=834335,
            report_target="FIRE_ALARM",
            report_semantic="fire_alarm",
            supplemental={
                834335: {
                    "target": "FIRE_ALARM",
                    "semantic": "license_text_conflict_review_required",
                    "recording_family": "bangcorrupt-fire-alarm",
                }
            },
        )
        self.assertEqual(semantic, "license_text_conflict_review_required")
        self.assertFalse(exact)
        self.assertIn("RIGHTS_TEXT_CONFLICT_REVIEW_REQUIRED", blockers)

    def test_augmentation_only_never_receives_real_positive_credit(self) -> None:
        semantic, exact, _, blockers = semantic_decision(
            sound_id=536769,
            report_target="TIRE_SQUEAL",
            report_semantic="derived_cc0_tire_squeal_augmentation_only",
            supplemental={},
        )
        self.assertFalse(exact)
        self.assertIn("AUGMENTATION_ONLY_NO_REAL_SOURCE_CREDIT", blockers)

    def test_curated_target_conflict_fails_closed(self) -> None:
        _, exact, _, blockers = semantic_decision(
            sound_id=999,
            report_target="FIRE_ALARM",
            report_semantic="fire_alarm",
            supplemental={
                999: {
                    "target": "TIRE_SQUEAL",
                    "semantic": "tire_squeal",
                    "recording_family": "wrong-target-family",
                }
            },
        )
        self.assertFalse(exact)
        self.assertIn("CURATED_TARGET_CONFLICT", blockers)


if __name__ == "__main__":
    unittest.main()

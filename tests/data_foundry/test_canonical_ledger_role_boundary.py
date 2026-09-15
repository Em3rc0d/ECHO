from __future__ import annotations

import unittest

from scripts.data_foundry.enforce_canonical_ledger_role_boundary import (
    apply_role_boundary,
    corpus_admission_rejection,
    has_governed_corpus_role,
    unresolved_admission_blockers,
)


class CanonicalLedgerRoleBoundaryTests(unittest.TestCase):
    def test_review_only_materialization_is_not_a_corpus_role(self) -> None:
        row = {
            "source_dataset": "echo-freesound-release-safe-v1",
            "echo_labels": [],
            "hard_negative_for": [],
            "rights_status": "ALLOW_RELEASE_SAFE",
            "blocking_reasons": ["NO_EXACT_SEMANTIC_ROLE", "GROUPING_GLOBAL_AUDIT_REQUIRED"],
        }
        self.assertFalse(has_governed_corpus_role(row))
        self.assertEqual(corpus_admission_rejection(row), "REVIEW_ONLY_NO_GOVERNED_ROLE")
        kept, audit = apply_role_boundary([row])
        self.assertEqual(kept, [])
        self.assertEqual(audit["removed_review_only_rows"], 1)
        self.assertTrue(audit["source_evidence_retained_elsewhere"])

    def test_exact_release_safe_positive_is_retained(self) -> None:
        row = {
            "source_dataset": "echo-freesound-release-safe-v1",
            "echo_labels": ["FIRE_ALARM"],
            "hard_negative_for": [],
            "rights_status": "ALLOW_RELEASE_SAFE",
            "blocking_reasons": [],
        }
        self.assertTrue(has_governed_corpus_role(row))
        self.assertIsNone(corpus_admission_rejection(row))
        kept, audit = apply_role_boundary([row])
        self.assertEqual(len(kept), 1)
        self.assertEqual(audit["removed_rows"], 0)

    def test_governed_release_safe_hard_negative_is_retained(self) -> None:
        row = {
            "source_dataset": "echo-freesound-release-safe-v1",
            "echo_labels": [],
            "hard_negative_for": ["TIRE_SQUEAL"],
            "rights_status": "ALLOW_RELEASE_SAFE",
            "blocking_reasons": [],
        }
        self.assertTrue(has_governed_corpus_role(row))
        self.assertIsNone(corpus_admission_rejection(row))
        kept, _ = apply_role_boundary([row])
        self.assertEqual(len(kept), 1)

    def test_pre_grouping_marker_is_deferred_not_quarantined(self) -> None:
        row = {
            "source_dataset": "echo-freesound-release-safe-v1",
            "source_asset_id": "98054",
            "echo_labels": ["GLASS_SHATTER"],
            "hard_negative_for": [],
            "rights_status": "ALLOW_RELEASE_SAFE",
            "blocking_reasons": ["GROUPING_GLOBAL_AUDIT_REQUIRED"],
        }
        self.assertEqual(unresolved_admission_blockers(row), set())
        self.assertIsNone(corpus_admission_rejection(row))
        kept, audit = apply_role_boundary([row])
        self.assertEqual(len(kept), 1)
        self.assertEqual(
            audit["retained_deferred_blocker_counts"],
            {"GROUPING_GLOBAL_AUDIT_REQUIRED": 1},
        )

    def test_grouping_marker_does_not_hide_a_real_conflict(self) -> None:
        row = {
            "source_dataset": "echo-freesound-release-safe-v1",
            "echo_labels": ["SIREN"],
            "hard_negative_for": [],
            "rights_status": "ALLOW_RELEASE_SAFE",
            "blocking_reasons": [
                "GROUPING_GLOBAL_AUDIT_REQUIRED",
                "SEMANTIC_STATUS_CONFLICT_FIRE_ALARM",
            ],
        }
        self.assertEqual(
            unresolved_admission_blockers(row),
            {"SEMANTIC_STATUS_CONFLICT_FIRE_ALARM"},
        )
        self.assertEqual(corpus_admission_rejection(row), "UNRESOLVED_ADMISSION_BLOCKER")
        kept, audit = apply_role_boundary([row])
        self.assertEqual(kept, [])
        self.assertEqual(audit["removed_unresolved_blocker_rows"], 1)

    def test_research_only_positive_is_quarantined(self) -> None:
        row = {
            "source_dataset": "echo-wikimedia-fire-alarm-v1",
            "echo_labels": ["FIRE_ALARM"],
            "hard_negative_for": [],
            "rights_status": "RESEARCH_ONLY",
            "license_id": "CC-BY-SA-3.0-AU",
            "blocking_reasons": ["LICENSE_NOT_RELEASE_SAFE"],
        }
        self.assertTrue(has_governed_corpus_role(row))
        self.assertEqual(corpus_admission_rejection(row), "NOT_RELEASE_SAFE")
        kept, audit = apply_role_boundary([row])
        self.assertEqual(kept, [])
        self.assertEqual(audit["removed_non_release_safe_rows"], 1)
        self.assertEqual(audit["removed_blocking_reason_counts"], {"LICENSE_NOT_RELEASE_SAFE": 1})
        self.assertEqual(audit["removed_rights_status_counts"], {"RESEARCH_ONLY": 1})

    def test_exact_siren_with_disputed_supplemental_target_is_quarantined(self) -> None:
        row = {
            "source_dataset": "echo-freesound-release-safe-v1",
            "source_asset_id": "53448",
            "echo_labels": ["SIREN"],
            "hard_negative_for": [],
            "rights_status": "ALLOW_RELEASE_SAFE",
            "semantic_status_by_target": {
                "SIREN": "EXACT_FSD50K_GROUND_TRUTH",
                "FIRE_ALARM": "CONFLICT:EXACT_CATEGORY_REVIEW_REQUIRED|REVIEW_REQUIRED",
            },
            "blocking_reasons": ["SEMANTIC_STATUS_CONFLICT_FIRE_ALARM"],
        }
        self.assertTrue(has_governed_corpus_role(row))
        self.assertEqual(corpus_admission_rejection(row), "UNRESOLVED_ADMISSION_BLOCKER")
        kept, audit = apply_role_boundary([row])
        self.assertEqual(kept, [])
        self.assertEqual(audit["removed_unresolved_blocker_rows"], 1)
        self.assertEqual(
            audit["removed_blocking_reason_counts"],
            {"SEMANTIC_STATUS_CONFLICT_FIRE_ALARM": 1},
        )

    def test_second_semantic_conflict_is_not_silently_promoted(self) -> None:
        row = {
            "source_dataset": "echo-freesound-release-safe-v1",
            "source_asset_id": "238228",
            "echo_labels": ["SIREN"],
            "hard_negative_for": [],
            "rights_status": "ALLOW_RELEASE_SAFE",
            "semantic_status_by_target": {
                "SIREN": "EXACT_FSD50K_GROUND_TRUTH",
                "TIRE_SQUEAL": "CONFLICT:EXACT_CATEGORY_REVIEW_REQUIRED|REVIEW_REQUIRED",
            },
            "blocking_reasons": ["SEMANTIC_STATUS_CONFLICT_TIRE_SQUEAL"],
        }
        kept, audit = apply_role_boundary([row])
        self.assertEqual(kept, [])
        self.assertEqual(audit["removed_unresolved_blocker_rows"], 1)
        self.assertEqual(
            audit["removed_blocking_reason_counts"],
            {"SEMANTIC_STATUS_CONFLICT_TIRE_SQUEAL": 1},
        )

    def test_missing_rights_status_fails_closed(self) -> None:
        row = {
            "source_dataset": "echo-freesound-release-safe-v1",
            "echo_labels": ["SIREN"],
            "hard_negative_for": [],
            "blocking_reasons": [],
        }
        self.assertEqual(corpus_admission_rejection(row), "NOT_RELEASE_SAFE")
        kept, audit = apply_role_boundary([row])
        self.assertEqual(kept, [])
        self.assertEqual(audit["removed_non_release_safe_rows"], 1)
        self.assertEqual(audit["removed_rights_status_counts"], {"MISSING": 1})

    def test_unknown_candidate_label_cannot_create_role(self) -> None:
        row = {
            "source_dataset": "echo-freesound-release-safe-v1",
            "echo_labels": ["NOT_AN_ECHO_TARGET"],
            "hard_negative_for": [],
            "rights_status": "ALLOW_RELEASE_SAFE",
            "blocking_reasons": [],
        }
        self.assertFalse(has_governed_corpus_role(row))
        self.assertEqual(corpus_admission_rejection(row), "REVIEW_ONLY_NO_GOVERNED_ROLE")


if __name__ == "__main__":
    unittest.main()

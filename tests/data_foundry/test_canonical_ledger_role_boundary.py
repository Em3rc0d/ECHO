from __future__ import annotations

import unittest

from scripts.data_foundry.enforce_canonical_ledger_role_boundary import (
    apply_role_boundary,
    has_governed_corpus_role,
)


class CanonicalLedgerRoleBoundaryTests(unittest.TestCase):
    def test_review_only_materialization_is_not_a_corpus_role(self) -> None:
        row = {
            "source_dataset": "echo-freesound-release-safe-v1",
            "echo_labels": [],
            "hard_negative_for": [],
            "blocking_reasons": ["NO_EXACT_SEMANTIC_ROLE", "GROUPING_GLOBAL_AUDIT_REQUIRED"],
        }
        self.assertFalse(has_governed_corpus_role(row))
        kept, audit = apply_role_boundary([row])
        self.assertEqual(kept, [])
        self.assertEqual(audit["removed_review_only_rows"], 1)
        self.assertTrue(audit["source_evidence_retained_elsewhere"])

    def test_exact_positive_is_retained(self) -> None:
        row = {
            "source_dataset": "echo-freesound-release-safe-v1",
            "echo_labels": ["FIRE_ALARM"],
            "hard_negative_for": [],
            "blocking_reasons": [],
        }
        self.assertTrue(has_governed_corpus_role(row))
        kept, audit = apply_role_boundary([row])
        self.assertEqual(len(kept), 1)
        self.assertEqual(audit["removed_review_only_rows"], 0)

    def test_governed_hard_negative_is_retained(self) -> None:
        row = {
            "source_dataset": "echo-freesound-release-safe-v1",
            "echo_labels": [],
            "hard_negative_for": ["TIRE_SQUEAL"],
            "blocking_reasons": [],
        }
        self.assertTrue(has_governed_corpus_role(row))
        kept, _ = apply_role_boundary([row])
        self.assertEqual(len(kept), 1)

    def test_unknown_candidate_label_cannot_create_role(self) -> None:
        row = {
            "source_dataset": "echo-freesound-release-safe-v1",
            "echo_labels": ["NOT_AN_ECHO_TARGET"],
            "hard_negative_for": [],
            "blocking_reasons": [],
        }
        self.assertFalse(has_governed_corpus_role(row))


if __name__ == "__main__":
    unittest.main()

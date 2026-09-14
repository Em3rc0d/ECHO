from __future__ import annotations

import unittest

from scripts.data_foundry.build_corpus_closure_evidence import (
    build_group_audit,
    build_split_audit,
)


class CorpusClosureEvidenceTests(unittest.TestCase):
    def _row(self, asset: str, group: str = "g1") -> dict:
        return {
            "ledger_asset_id": asset,
            "rights_status": "ALLOW_RELEASE_SAFE",
            "stage_status": "READY_FOR_GLOBAL_DEDUP",
            "blocking_reasons": [],
            "media_sha256": (asset[0] * 64)[:64],
            "byte_size": 100,
            "audio_probe": {"ok": True, "duration_seconds": 2.0},
            "recording_group_id": group,
            "grouping_status": "CURATED_RECORDING_FAMILY",
            "echo_labels": ["SIREN"],
            "hard_negative_for": [],
            "candidate_targets": ["SIREN"],
            "field_holdout": False,
            "original_split": None,
        }

    def test_group_audit_fails_when_global_group_review_pending(self) -> None:
        row = self._row("a")
        row["blocking_reasons"] = ["GROUPING_GLOBAL_AUDIT_REQUIRED"]
        row["stage_status"] = "REVIEW_REQUIRED"
        dedup = {
            "exact_cross_recording_group_conflict_count": 0,
            "near_duplicate_unresolved_cross_group_count": 0,
        }
        result = build_group_audit([row], dedup)
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("RECORDING_FAMILY_GLOBAL_AUDIT_PENDING", result["gap_codes"])

    def test_split_audit_inherits_upstream_failures(self) -> None:
        row = self._row("b")
        policy = {
            "seed": "test",
            "original_split_map": {"train": "train"},
            "fallback_group_hash_ratios": {
                "train": 0.7,
                "validation": 0.15,
                "test": 0.15,
            },
        }
        result, assignments = build_split_audit(
            [row],
            policy,
            {"status": "FAIL"},
            {"status": "FAIL"},
        )
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("UPSTREAM_GLOBAL_DEDUP_NOT_PASS", result["gap_codes"])
        self.assertIn("UPSTREAM_RECORDING_FAMILY_AUDIT_NOT_PASS", result["gap_codes"])
        self.assertIn("g1", assignments)

    def test_original_split_conflict_is_explicit(self) -> None:
        left = self._row("c", "shared")
        right = self._row("d", "shared")
        left["original_split"] = "train"
        right["original_split"] = "test"
        policy = {
            "seed": "test",
            "original_split_map": {"train": "train", "test": "test"},
            "fallback_group_hash_ratios": {
                "train": 0.7,
                "validation": 0.15,
                "test": 0.15,
            },
        }
        result, _ = build_split_audit(
            [left, right],
            policy,
            {"status": "PASS"},
            {"status": "PASS"},
        )
        self.assertIn("ORIGINAL_SPLIT_CONFLICT_WITHIN_RECORDING_FAMILY", result["gap_codes"])


if __name__ == "__main__":
    unittest.main()

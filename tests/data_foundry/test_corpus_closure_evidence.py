from __future__ import annotations

import unittest

from scripts.data_foundry.build_corpus_closure_evidence import (
    build_dedup,
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

    def _fingerprint(self, *, pcm: str, vector: list[int], samples: int = 32000) -> dict:
        return {
            "schema_version": "echo.canonical-audio-fingerprint.v1",
            "algorithm": "normalized-rms-envelope-v1",
            "canonical_decode": {
                "channels": 1,
                "sample_rate_hz": 16000,
                "sample_format": "s16le",
            },
            "bins": len(vector),
            "levels": 255,
            "decoded_sample_count": samples,
            "canonical_pcm_sha256": pcm,
            "vector_sha256": pcm,
            "vector": vector,
        }

    def test_screen_only_candidate_does_not_block_dedup_or_group_audit(self) -> None:
        left = self._row("a", "left")
        right = self._row("b", "right")
        left["canonical_fingerprint"] = self._fingerprint(pcm="1" * 64, vector=[100, 100])
        right["canonical_fingerprint"] = self._fingerprint(pcm="2" * 64, vector=[103, 100])
        policy = {
            "comparison": {
                "candidate_max_distance": 0.02,
                "confirmed_group_max_distance": 0.002,
                "confirmed_group_max_relative_sample_count_delta": 0.01,
            }
        }

        dedup = build_dedup([left, right], policy)
        groups = build_group_audit([left, right], dedup)

        self.assertEqual(dedup["status"], "PASS")
        self.assertEqual(dedup["near_duplicate_candidate_cross_group_count"], 1)
        self.assertEqual(dedup["confirmed_near_duplicate_cross_group_count"], 0)
        self.assertEqual(dedup["review_only_near_duplicate_count"], 1)
        self.assertEqual(groups["status"], "PASS")
        self.assertEqual(groups["screening_candidate_cross_group_count"], 1)

    def test_confirmed_candidate_crossing_groups_blocks_closure(self) -> None:
        left = self._row("c", "left")
        right = self._row("d", "right")
        left["canonical_fingerprint"] = self._fingerprint(pcm="3" * 64, vector=[100, 100])
        right["canonical_fingerprint"] = self._fingerprint(pcm="4" * 64, vector=[100, 100])
        policy = {
            "comparison": {
                "candidate_max_distance": 0.02,
                "confirmed_group_max_distance": 0.002,
                "confirmed_group_max_relative_sample_count_delta": 0.01,
            }
        }

        dedup = build_dedup([left, right], policy)
        groups = build_group_audit([left, right], dedup)

        self.assertEqual(dedup["status"], "FAIL")
        self.assertEqual(dedup["confirmed_near_duplicate_cross_group_count"], 1)
        self.assertIn("CONFIRMED_NEAR_DUPLICATE_RECORDING_GROUP_CONFLICTS", dedup["gap_codes"])
        self.assertEqual(groups["status"], "FAIL")
        self.assertIn("CONFIRMED_NEAR_DUPLICATES_CROSS_RECORDING_FAMILIES", groups["gap_codes"])

    def test_group_audit_fails_when_global_group_review_pending(self) -> None:
        row = self._row("e")
        row["blocking_reasons"] = ["GROUPING_GLOBAL_AUDIT_REQUIRED"]
        row["stage_status"] = "REVIEW_REQUIRED"
        dedup = {
            "exact_cross_recording_group_conflict_count": 0,
            "confirmed_near_duplicate_cross_group_count": 0,
            "near_duplicate_candidate_cross_group_count": 0,
        }
        result = build_group_audit([row], dedup)
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("RECORDING_FAMILY_GLOBAL_AUDIT_PENDING", result["gap_codes"])

    def test_split_audit_inherits_upstream_failures(self) -> None:
        row = self._row("f")
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
        left = self._row("g", "shared")
        right = self._row("h", "shared")
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

from __future__ import annotations

import unittest

from scripts.data_foundry.apply_split_conflict_quarantine import (
    QUARANTINE,
    _coverage_rows,
    build_quarantined_split_audit,
    split_plan_with_quarantine,
)


class SplitConflictQuarantineTests(unittest.TestCase):
    def _row(self, asset: str, *, group: str = "shared", original_split: str | None = None) -> dict:
        return {
            "ledger_asset_id": asset,
            "rights_status": "ALLOW_RELEASE_SAFE",
            "stage_status": "READY_FOR_GLOBAL_DEDUP",
            "blocking_reasons": [],
            "media_sha256": (asset[0] * 64)[:64],
            "byte_size": 100,
            "audio_probe": {"ok": True, "duration_seconds": 2.0},
            "recording_group_id": group,
            "grouping_status": "GLOBAL_ACOUSTIC_COMPONENT",
            "echo_labels": ["SIREN"],
            "hard_negative_for": [],
            "candidate_targets": ["SIREN"],
            "field_holdout": False,
            "original_split": original_split,
            "license_id": "CC0",
            "label_provenance": ["test"],
            "underlying_source_family": "TEST_SOURCE",
        }

    def _policy(self) -> dict:
        return {
            "policy_id": "TEST-SPLIT-002",
            "seed": "test-seed",
            "protected_original_split_conflict_strategy": "quarantine_entire_recording_group",
            "original_split_map": {
                "train": "train",
                "validation": "validation",
                "test": "test",
            },
            "fallback_group_hash_ratios": {
                "train": 0.7,
                "validation": 0.15,
                "test": 0.15,
            },
        }

    def test_conflicting_original_splits_quarantine_whole_group(self) -> None:
        rows = [
            self._row("a", original_split="train"),
            self._row("b", original_split="test"),
        ]
        assignments, conflicts = split_plan_with_quarantine(rows, self._policy())
        self.assertEqual(assignments["shared"], QUARANTINE)
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]["asset_count"], 2)
        self.assertEqual(conflicts[0]["recognized_original_splits"], ["test", "train"])

    def test_quarantined_conflict_is_not_split_failure_when_upstream_passes(self) -> None:
        rows = [
            self._row("a", original_split="train"),
            self._row("b", original_split="test"),
            self._row("c", group="clean", original_split="train"),
        ]
        audit, assignments = build_quarantined_split_audit(
            rows,
            self._policy(),
            {"status": "PASS"},
            {"status": "PASS"},
        )
        self.assertEqual(audit["status"], "PASS")
        self.assertEqual(audit["gap_codes"], [])
        self.assertEqual(audit["original_split_conflict_count"], 1)
        self.assertEqual(audit["original_split_conflicts_quarantined"], 1)
        self.assertEqual(audit["quarantined_asset_count"], 2)
        self.assertEqual(audit["eligible_asset_count"], 1)
        self.assertEqual(assignments["shared"], QUARANTINE)
        self.assertEqual(assignments["clean"], "train")

    def test_quarantine_never_enters_coverage_rows(self) -> None:
        rows = [
            self._row("a", original_split="train"),
            self._row("b", original_split="test"),
            self._row("c", group="clean", original_split="train"),
        ]
        assignments, _ = split_plan_with_quarantine(rows, self._policy())
        translated = _coverage_rows(rows, assignments)
        self.assertEqual([row["asset_id"] for row in translated], ["c"])
        self.assertTrue(all(row["echo_split"] != QUARANTINE for row in translated))

    def test_strategy_must_be_explicit(self) -> None:
        policy = self._policy()
        policy.pop("protected_original_split_conflict_strategy")
        with self.assertRaises(ValueError):
            split_plan_with_quarantine([self._row("a")], policy)

    def test_upstream_failures_still_fail_closed(self) -> None:
        row = self._row("a", group="clean", original_split="train")
        audit, _ = build_quarantined_split_audit(
            [row],
            self._policy(),
            {"status": "FAIL"},
            {"status": "PASS"},
        )
        self.assertEqual(audit["status"], "FAIL")
        self.assertIn("UPSTREAM_GLOBAL_DEDUP_NOT_PASS", audit["gap_codes"])


if __name__ == "__main__":
    unittest.main()

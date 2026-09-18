from __future__ import annotations

import unittest

from scripts.data_foundry.balance_release_safe_corpus_sources import (
    max_allowed_dominant,
    remove_target_role,
    select_dominant_asset_ids,
)


def row(asset: str, group: str, labels=None, hard_negatives=None):
    return {
        "ledger_asset_id": asset,
        "recording_group_id": group,
        "echo_labels": list(labels or ["GLASS_SHATTER"]),
        "candidate_targets": list(labels or ["GLASS_SHATTER"]),
        "hard_negative_for": list(hard_negatives or []),
        "semantic_status_by_target": {
            label: "EXACT" for label in (labels or ["GLASS_SHATTER"])
        },
    }


class SourceBalancePolicyTests(unittest.TestCase):
    def test_max_allowed_dominant_matches_fraction_boundary(self) -> None:
        self.assertEqual(max_allowed_dominant(2, 0.80), 8)
        self.assertEqual(max_allowed_dominant(23, 0.80), 92)

    def test_group_first_selection_uses_distinct_groups_before_second_members(self) -> None:
        rows = [
            row("a1", "g1"), row("a2", "g1"),
            row("b1", "g2"), row("b2", "g2"),
            row("c1", "g3"),
        ]
        selected = select_dominant_asset_ids(
            rows,
            keep_count=3,
            policy_id="P",
            target="GLASS_SHATTER",
            family="FREESOUND",
        )
        groups = {
            next(item["recording_group_id"] for item in rows if item["ledger_asset_id"] == asset)
            for asset in selected
        }
        self.assertEqual(len(selected), 3)
        self.assertEqual(groups, {"g1", "g2", "g3"})

    def test_selection_is_deterministic(self) -> None:
        rows = [row(f"a{i}", f"g{i % 4}") for i in range(12)]
        left = select_dominant_asset_ids(rows, keep_count=7, policy_id="P", target="GLASS_SHATTER", family="FREESOUND")
        right = select_dominant_asset_ids(list(reversed(rows)), keep_count=7, policy_id="P", target="GLASS_SHATTER", family="FREESOUND")
        self.assertEqual(left, right)

    def test_remove_target_drops_role_only_row(self) -> None:
        self.assertIsNone(remove_target_role(row("a", "g"), "GLASS_SHATTER"))

    def test_remove_target_preserves_other_governed_role(self) -> None:
        source = row("a", "g", labels=["GLASS_SHATTER", "SIREN"])
        changed = remove_target_role(source, "GLASS_SHATTER")
        self.assertIsNotNone(changed)
        self.assertEqual(changed["echo_labels"], ["SIREN"])
        self.assertNotIn("GLASS_SHATTER", changed["semantic_status_by_target"])

    def test_remove_target_preserves_hard_negative_row(self) -> None:
        source = row("a", "g", labels=["GLASS_SHATTER"], hard_negatives=["SIREN"])
        changed = remove_target_role(source, "GLASS_SHATTER")
        self.assertIsNotNone(changed)
        self.assertEqual(changed["echo_labels"], [])
        self.assertEqual(changed["hard_negative_for"], ["SIREN"])


if __name__ == "__main__":
    unittest.main()

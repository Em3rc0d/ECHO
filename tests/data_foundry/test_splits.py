from __future__ import annotations

import unittest

from echo.data_foundry.splits import SplitRatios, assign_group, assert_no_cross_split_hashes, plan_groups


class SplitTests(unittest.TestCase):
    def test_ratios_must_sum_to_one(self) -> None:
        with self.assertRaises(ValueError):
            SplitRatios(0.7, 0.2, 0.2)

    def test_assignment_is_deterministic(self) -> None:
        ratios = SplitRatios(0.7, 0.15, 0.15)
        first = assign_group("sensor-A:session-01", seed="echo-v1", ratios=ratios)
        second = assign_group("sensor-A:session-01", seed="echo-v1", ratios=ratios)
        self.assertEqual(first, second)
        self.assertIn(first, {"train", "validation", "test"})

    def test_plan_is_order_independent(self) -> None:
        ratios = SplitRatios(0.8, 0.1, 0.1)
        a = plan_groups(["c", "a", "b"], seed="s", ratios=ratios)
        b = plan_groups(["b", "c", "a"], seed="s", ratios=ratios)
        self.assertEqual(a, b)

    def test_exact_hash_cannot_cross_splits(self) -> None:
        rows = [
            {"asset_id": "a", "sha256": "a" * 64, "echo_split": "train"},
            {"asset_id": "b", "sha256": "a" * 64, "echo_split": "test"},
        ]
        with self.assertRaises(ValueError):
            assert_no_cross_split_hashes(rows)


if __name__ == "__main__":
    unittest.main()

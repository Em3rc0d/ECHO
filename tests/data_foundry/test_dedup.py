from __future__ import annotations

import unittest

from echo.data_foundry.dedup import audit_duplicate_leakage, find_exact_duplicates, find_near_duplicate_fingerprints


class DedupTests(unittest.TestCase):
    def test_exact_duplicates_reported(self) -> None:
        rows = [
            {"asset_id": "a", "sha256": "1" * 64, "echo_split": "train", "recording_group_id": "g"},
            {"asset_id": "b", "sha256": "1" * 64, "echo_split": "train", "recording_group_id": "g"},
        ]
        findings = find_exact_duplicates(rows)
        self.assertEqual(len(findings), 1)
        self.assertFalse(findings[0].crosses_splits)

    def test_exact_duplicate_cross_split_stops_line(self) -> None:
        rows = [
            {"asset_id": "a", "sha256": "1" * 64, "echo_split": "train", "recording_group_id": "ga"},
            {"asset_id": "b", "sha256": "1" * 64, "echo_split": "test", "recording_group_id": "gb"},
        ]
        with self.assertRaises(ValueError):
            audit_duplicate_leakage(rows)

    def test_near_duplicate_fingerprint_cross_split_stops_line(self) -> None:
        rows = [
            {"asset_id": "a", "sha256": "1" * 64, "echo_split": "train", "recording_group_id": "ga", "extra": {"near_duplicate_fingerprint": "fp1"}},
            {"asset_id": "b", "sha256": "2" * 64, "echo_split": "validation", "recording_group_id": "gb", "extra": {"near_duplicate_fingerprint": "fp1"}},
        ]
        self.assertEqual(len(find_near_duplicate_fingerprints(rows)), 1)
        with self.assertRaises(ValueError):
            audit_duplicate_leakage(rows)

    def test_group_cross_split_stops_line(self) -> None:
        rows = [
            {"asset_id": "a", "sha256": "1" * 64, "echo_split": "train", "recording_group_id": "same"},
            {"asset_id": "b", "sha256": "2" * 64, "echo_split": "test", "recording_group_id": "same"},
        ]
        with self.assertRaises(ValueError):
            audit_duplicate_leakage(rows)


if __name__ == "__main__":
    unittest.main()

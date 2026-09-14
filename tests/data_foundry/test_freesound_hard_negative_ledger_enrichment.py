from __future__ import annotations

import unittest

from scripts.data_foundry.enrich_ledger_with_freesound_hard_negatives import (
    valid_hard_negative_roles,
)


class FreesoundHardNegativeLedgerEnrichmentTests(unittest.TestCase):
    def test_preserves_governed_hard_negative_roles(self) -> None:
        source = {
            "hard_negative_for": ["TIRE_SQUEAL", "VEHICLE_HORN"],
        }
        ledger = {"echo_labels": ["SIREN"]}
        self.assertEqual(
            valid_hard_negative_roles(source, ledger),
            ["TIRE_SQUEAL", "VEHICLE_HORN"],
        )

    def test_positive_label_has_precedence(self) -> None:
        source = {
            "hard_negative_for": ["SIREN", "TIRE_SQUEAL"],
        }
        ledger = {"echo_labels": ["SIREN"]}
        self.assertEqual(
            valid_hard_negative_roles(source, ledger),
            ["TIRE_SQUEAL"],
        )

    def test_unknown_roles_are_never_admitted(self) -> None:
        source = {
            "hard_negative_for": ["TIRE_SQUEAL", "NOT_AN_ECHO_TARGET"],
        }
        ledger = {"echo_labels": []}
        self.assertEqual(
            valid_hard_negative_roles(source, ledger),
            ["TIRE_SQUEAL"],
        )


if __name__ == "__main__":
    unittest.main()

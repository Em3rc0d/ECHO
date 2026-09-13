from __future__ import annotations

import unittest

from echo.data_foundry.contracts import MappingStatus
from echo.data_foundry.mapping import LabelMapper


PAYLOAD = {
    "schema_version": "echo.label-mapping.v1",
    "sources": {
        "fsd50k-1.0": {
            "Siren": {"status": "EXACT", "echo_labels": ["SIREN"], "review_required": False, "use": "positive"},
            "Shatter": {"status": "BROADER", "echo_labels": ["GLASS_SHATTER"], "review_required": True, "use": "positive_after_review"},
        },
        "singapura-v1.0a": {
            "12-1": {"status": "AMBIGUOUS", "echo_labels": [], "review_required": False, "use": "hard_negative", "confuses": ["TIRE_SQUEAL"]},
        },
    },
}


class MappingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mapper = LabelMapper(PAYLOAD)

    def test_exact_siren(self) -> None:
        result = self.mapper.map_labels("fsd50k-1.0", ["Siren"])
        self.assertEqual(result.echo_labels, ("SIREN",))
        self.assertEqual(result.status, MappingStatus.EXACT)
        self.assertFalse(result.review_required)

    def test_broad_shatter_requires_review(self) -> None:
        result = self.mapper.map_labels("fsd50k-1.0", ["Shatter"])
        self.assertEqual(result.echo_labels, ("GLASS_SHATTER",))
        self.assertEqual(result.status, MappingStatus.BROADER)
        self.assertTrue(result.review_required)

    def test_friction_brake_is_not_tire_squeal_positive(self) -> None:
        result = self.mapper.map_labels("singapura-v1.0a", ["12-1"])
        self.assertEqual(result.echo_labels, ())
        self.assertEqual(result.confuses, ("TIRE_SQUEAL",))

    def test_unknown_label_is_unmapped_not_guessed(self) -> None:
        result = self.mapper.map_labels("fsd50k-1.0", ["Unknown semantic label"])
        self.assertEqual(result.echo_labels, ())
        self.assertEqual(result.unmapped_source_labels, ("Unknown semantic label",))


if __name__ == "__main__":
    unittest.main()

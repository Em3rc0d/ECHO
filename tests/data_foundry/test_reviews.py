from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from echo.data_foundry.reviews import load_review_decisions


class ReviewDecisionTests(unittest.TestCase):
    def test_valid_review_loads(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "reviews.json"
            path.write_text(json.dumps({
                "schema_version": "echo.review-decisions.v1",
                "decisions": [{
                    "asset_id": "fsd50k-1.0:123",
                    "approved": True,
                    "echo_labels": ["GLASS_SHATTER"],
                    "reviewer": "reviewer-a",
                    "reviewed_at_utc": "2026-09-13T00:00:00Z",
                    "rationale": "audible glass break confirmed",
                    "evidence_ref": "review://123"
                }]
            }), encoding="utf-8")
            decisions = load_review_decisions(path)
            self.assertTrue(decisions["fsd50k-1.0:123"].approved)
            self.assertEqual(decisions["fsd50k-1.0:123"].echo_labels, ("GLASS_SHATTER",))

    def test_unknown_target_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "reviews.json"
            path.write_text(json.dumps({
                "schema_version": "echo.review-decisions.v1",
                "decisions": [{
                    "asset_id": "x:1",
                    "approved": True,
                    "echo_labels": ["ROBBERY"],
                    "reviewer": "r",
                    "reviewed_at_utc": "2026-09-13T00:00:00Z",
                    "rationale": "invalid semantic target"
                }]
            }), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_review_decisions(path)

    def test_duplicate_decision_rejected(self) -> None:
        row = {
            "asset_id": "x:1", "approved": False, "echo_labels": [],
            "reviewer": "r", "reviewed_at_utc": "2026-09-13T00:00:00Z", "rationale": "no"
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "reviews.json"
            path.write_text(json.dumps({"schema_version": "echo.review-decisions.v1", "decisions": [row, row]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_review_decisions(path)


if __name__ == "__main__":
    unittest.main()

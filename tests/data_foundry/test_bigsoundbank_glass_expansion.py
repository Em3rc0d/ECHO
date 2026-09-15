from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
EXPANSION = ROOT / "configs/data_foundry/bigsoundbank_glass_expansion.v1.json"
BASE = ROOT / "configs/data_foundry/gap_source_candidates.v1.json"
CONFUSERS = ROOT / "configs/data_foundry/bigsoundbank_confusers.v1.json"


class BigSoundBankGlassExpansionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.expansion = json.loads(EXPANSION.read_text(encoding="utf-8"))
        self.base = json.loads(BASE.read_text(encoding="utf-8"))
        self.confusers = json.loads(CONFUSERS.read_text(encoding="utf-8"))

    def test_schema_source_and_target_are_exact(self) -> None:
        self.assertEqual(self.expansion["schema_version"], "echo.bigsoundbank-glass-expansion.v1")
        self.assertEqual(self.expansion["source_dataset"], "echo-bigsoundbank-cc0-gap-v1")
        self.assertEqual(self.expansion["target"], "GLASS_SHATTER")

    def test_exact_nine_assets_only(self) -> None:
        expected = {
            "bigsoundbank-387",
            "bigsoundbank-1121",
            "bigsoundbank-1122",
            "bigsoundbank-1123",
            "bigsoundbank-2041",
            "bigsoundbank-2042",
            "bigsoundbank-2043",
            "bigsoundbank-2044",
            "bigsoundbank-2045",
        }
        rows = self.expansion["assets"]
        self.assertEqual(len(rows), 9)
        self.assertEqual({row["asset_key"] for row in rows}, expected)
        self.assertTrue(all(row["semantic"] == "glass_shatter" for row in rows))

    def test_grouping_is_conservative_three_families(self) -> None:
        groups = {row["recording_family"] for row in self.expansion["assets"]}
        self.assertEqual(
            groups,
            {
                "mirror_break_387",
                "broken_christmas_ball_family",
                "bulb_bursting_family",
            },
        )
        christmas = [row for row in self.expansion["assets"] if row["asset_key"] in {
            "bigsoundbank-1121", "bigsoundbank-1122", "bigsoundbank-1123"
        }]
        bulbs = [row for row in self.expansion["assets"] if row["asset_key"] in {
            "bigsoundbank-2041", "bigsoundbank-2042", "bigsoundbank-2043", "bigsoundbank-2044", "bigsoundbank-2045"
        }]
        self.assertEqual({row["recording_family"] for row in christmas}, {"broken_christmas_ball_family"})
        self.assertEqual({row["recording_family"] for row in bulbs}, {"bulb_bursting_family"})

    def test_expansion_does_not_duplicate_existing_governed_assets(self) -> None:
        existing = {
            row["asset_key"]
            for rows in self.base["sources"]["echo-bigsoundbank-cc0-gap-v1"]["targets"].values()
            for row in rows
        }
        confusers = {row["asset_key"] for row in self.confusers["assets"]}
        expanded = {row["asset_key"] for row in self.expansion["assets"]}
        self.assertTrue(expanded.isdisjoint(existing))
        self.assertTrue(expanded.isdisjoint(confusers))

    def test_pages_and_media_are_pinned_to_bigsoundbank_https(self) -> None:
        for row in self.expansion["assets"]:
            self.assertTrue(row["url"].startswith("https://bigsoundbank.com/"))
            self.assertTrue(row["media_url"].startswith("https://bigsoundbank.com/UPLOAD/mp3/"))
            self.assertTrue(row["media_url"].endswith(".mp3"))


if __name__ == "__main__":
    unittest.main()

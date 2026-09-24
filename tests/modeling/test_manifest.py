import json
from pathlib import Path
import tempfile
import unittest

from echo.modeling.manifest import MVP_TARGETS, load_benchmark_manifest


class ManifestTest(unittest.TestCase):
    def test_partial_supervision_round_trip(self):
        row = {
            "asset_id": "source:1",
            "split": "train",
            "source_dataset": "source",
            "recording_group_id": "group:1",
            "media_sha256": "a" * 64,
            "duration_seconds": 1.0,
            "positive_labels": ["SIREN"],
            "explicit_negative_labels": ["VEHICLE_HORN"],
            "supervision": {
                "GLASS_SHATTER": None,
                "SIREN": 1,
                "VEHICLE_HORN": 0,
            },
            "origin_uri": "https://example.invalid/1",
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.jsonl"
            path.write_text(json.dumps(row) + "\n", encoding="utf-8")
            loaded = load_benchmark_manifest(path)
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].supervision["SIREN"], 1)
        self.assertEqual(loaded[0].supervision["VEHICLE_HORN"], 0)
        self.assertIsNone(loaded[0].supervision["GLASS_SHATTER"])
        self.assertEqual(tuple(MVP_TARGETS), ("GLASS_SHATTER", "SIREN", "VEHICLE_HORN"))


if __name__ == "__main__":
    unittest.main()

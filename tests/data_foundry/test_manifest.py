from __future__ import annotations

import unittest

from echo.data_foundry.manifest import asset_manifest_sha256, asset_manifest_text, build_dataset_manifest


class ManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.a = {
            "asset_id": "source:b",
            "source_dataset": "source",
            "source_release": "1",
            "sha256": "b" * 64,
        }
        self.b = {
            "asset_id": "source:a",
            "source_dataset": "source",
            "source_release": "1",
            "sha256": "a" * 64,
        }

    def test_asset_manifest_digest_is_input_order_independent(self) -> None:
        self.assertEqual(
            asset_manifest_sha256([self.a, self.b]),
            asset_manifest_sha256([self.b, self.a]),
        )
        text = asset_manifest_text([self.a, self.b])
        self.assertLess(text.index("source:a"), text.index("source:b"))

    def test_dataset_manifest_derives_counts_and_sources(self) -> None:
        manifest = build_dataset_manifest(
            manifest_id="echo-data-test",
            profile="release_safe",
            taxonomy_version="echo.taxonomy.v1",
            records=[self.a, self.b],
            source_registry_sha256="1" * 64,
            license_policy_sha256="2" * 64,
            label_mapping_sha256="3" * 64,
            split_policy_sha256="4" * 64,
            known_gaps=["FIRE_ALARM"],
            created_at_utc="2026-09-13T00:00:00Z",
        )
        self.assertEqual(manifest["asset_count"], 2)
        self.assertEqual(manifest["source_releases"], ["source@1"])
        self.assertEqual(manifest["known_gaps"], ["FIRE_ALARM"])


if __name__ == "__main__":
    unittest.main()

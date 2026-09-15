from __future__ import annotations

import unittest

from scripts.data_foundry.resolve_global_recording_groups import resolve_groups


def row(asset: str, group: str, media: str) -> dict:
    return {
        "ledger_asset_id": f"echo-freesound-release-safe-v1:{asset}",
        "source_dataset": "echo-freesound-release-safe-v1",
        "source_asset_id": asset,
        "license_id": "CC-BY-4.0",
        "rights_status": "ALLOW_RELEASE_SAFE",
        "media_sha256": media,
        "byte_size": 100,
        "audio_probe": {"ok": True, "duration_seconds": 1.0, "sample_rate_hz": 44100, "channels": 1},
        "recording_group_id": group,
        "grouping_status": "FALLBACK_CLIP_ID",
        "echo_labels": ["SIREN"],
        "hard_negative_for": [],
        "candidate_targets": ["SIREN"],
        "blocking_reasons": ["GROUPING_GLOBAL_AUDIT_REQUIRED"],
        "field_holdout": False,
    }


class GlobalRecordingGroupResolutionTests(unittest.TestCase):
    def test_fallback_singleton_becomes_explicitly_screened(self) -> None:
        rows, audit = resolve_groups([row("1", "freesound:sound:1", "a" * 64)], threshold=0.02)
        self.assertEqual(rows[0]["recording_group_id"], "freesound:sound:1")
        self.assertEqual(rows[0]["grouping_status"], "GLOBAL_ACOUSTIC_SCREENED_SOURCE_GROUP")
        self.assertNotIn("GROUPING_GLOBAL_AUDIT_REQUIRED", rows[0]["blocking_reasons"])
        self.assertEqual(rows[0]["stage_status"], "READY_FOR_GLOBAL_DEDUP")
        self.assertEqual(audit["fallback_asset_count_after"], 0)
        self.assertFalse(audit["content_merge_performed"])

    def test_exact_identity_across_fallback_groups_forces_shared_protection_group(self) -> None:
        same_media = "b" * 64
        rows, audit = resolve_groups([
            row("1", "freesound:sound:1", same_media),
            row("2", "freesound:sound:2", same_media),
        ], threshold=0.02)
        self.assertEqual(rows[0]["recording_group_id"], rows[1]["recording_group_id"])
        self.assertTrue(rows[0]["recording_group_id"].startswith("global-acoustic:"))
        self.assertEqual(rows[0]["grouping_status"], "GLOBAL_ACOUSTIC_COMPONENT")
        self.assertEqual(rows[1]["grouping_status"], "GLOBAL_ACOUSTIC_COMPONENT")
        self.assertEqual(audit["global_acoustic_component_count"], 1)
        self.assertFalse(audit["content_deleted"])


if __name__ == "__main__":
    unittest.main()

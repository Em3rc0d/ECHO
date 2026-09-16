from __future__ import annotations

import unittest

from scripts.data_foundry.resolve_global_recording_groups import resolve_groups


def fingerprint(*, value: int, samples: int, pcm: str) -> dict:
    return {
        "schema_version": "echo.canonical-audio-fingerprint.v1",
        "algorithm": "normalized-rms-envelope-v1",
        "canonical_decode": {
            "channels": 1,
            "sample_rate_hz": 16000,
            "sample_format": "s16le",
        },
        "bins": 128,
        "levels": 255,
        "decoded_sample_count": samples,
        "canonical_pcm_sha256": pcm,
        "vector_sha256": f"vector-{value}-{samples}-{pcm}",
        "vector": [value] * 128,
    }


def row(asset: str, group: str, media: str, *, fp: dict | None = None) -> dict:
    value = {
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
    if fp is not None:
        value["canonical_fingerprint"] = fp
    return value


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

    def test_screening_only_near_edge_does_not_union_groups(self) -> None:
        # Distance = 2/255 ~= 0.00784: inside broad 0.02 screening, outside
        # strict 0.002 confirmation. It must remain review evidence only.
        rows, audit = resolve_groups([
            row("1", "freesound:sound:1", "a" * 64, fp=fingerprint(value=0, samples=32000, pcm="1" * 64)),
            row("2", "freesound:sound:2", "b" * 64, fp=fingerprint(value=2, samples=32000, pcm="2" * 64)),
        ], threshold=0.02, confirmed_threshold=0.002, max_relative_sample_count_delta=0.01)
        self.assertNotEqual(rows[0]["recording_group_id"], rows[1]["recording_group_id"])
        self.assertEqual(audit["near_duplicate_candidate_edge_count"], 1)
        self.assertEqual(audit["confirmed_near_duplicate_grouping_edge_count"], 0)
        self.assertEqual(audit["review_only_near_duplicate_edge_count"], 1)
        self.assertEqual(audit["global_acoustic_component_count"], 0)

    def test_confirmed_near_duplicate_edge_unions_groups_for_split_protection(self) -> None:
        rows, audit = resolve_groups([
            row("1", "freesound:sound:1", "a" * 64, fp=fingerprint(value=100, samples=32000, pcm="1" * 64)),
            row("2", "freesound:sound:2", "b" * 64, fp=fingerprint(value=100, samples=32100, pcm="2" * 64)),
        ], threshold=0.02, confirmed_threshold=0.002, max_relative_sample_count_delta=0.01)
        self.assertEqual(rows[0]["recording_group_id"], rows[1]["recording_group_id"])
        self.assertTrue(rows[0]["recording_group_id"].startswith("global-acoustic:"))
        self.assertEqual(audit["confirmed_near_duplicate_grouping_edge_count"], 1)
        self.assertEqual(audit["review_only_near_duplicate_edge_count"], 0)

    def test_shape_match_with_incompatible_length_never_unions(self) -> None:
        rows, audit = resolve_groups([
            row("1", "freesound:sound:1", "a" * 64, fp=fingerprint(value=100, samples=32000, pcm="1" * 64)),
            row("2", "freesound:sound:2", "b" * 64, fp=fingerprint(value=100, samples=64000, pcm="2" * 64)),
        ], threshold=0.02, confirmed_threshold=0.002, max_relative_sample_count_delta=0.01)
        self.assertNotEqual(rows[0]["recording_group_id"], rows[1]["recording_group_id"])
        self.assertEqual(audit["near_duplicate_candidate_edge_count"], 1)
        self.assertEqual(audit["confirmed_near_duplicate_grouping_edge_count"], 0)
        self.assertEqual(audit["candidate_edges_rejected_by_length_count"], 1)
        self.assertEqual(audit["review_only_near_duplicate_edge_count"], 1)


if __name__ == "__main__":
    unittest.main()

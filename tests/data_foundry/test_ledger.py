from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
import json
from echo.data_foundry.ledger import load_underlying_source_policy, underlying_source_family, summarize_ledger, validate_ledger


def row(asset_id: str, source: str, family: str, *, label: str | None = None, hard_negative: str | None = None, stage: str = "READY_FOR_GLOBAL_DEDUP") -> dict:
    return {
        "schema_version": "echo.canonical-asset-ledger-entry.v1",
        "ledger_asset_id": asset_id,
        "source_dataset": source,
        "source_release": "v1",
        "source_asset_id": asset_id.split(":", 1)[-1],
        "underlying_source_family": family,
        "origin_uri": None,
        "media_sha256": ("a" if asset_id.endswith("1") else "b") * 64,
        "byte_size": 100,
        "audio_probe": {"ok": True, "duration_seconds": 1.0, "sample_rate_hz": 16000, "channels": 1},
        "license_id": "CC-BY-4.0",
        "rights_status": "ALLOW_RELEASE_SAFE",
        "candidate_targets": ([label] if label else []),
        "echo_labels": ([label] if label else []),
        "hard_negative_for": ([hard_negative] if hard_negative else []),
        "semantic_status_by_target": {},
        "label_provenance": ["fixture"],
        "recording_group_id": f"g:{asset_id}",
        "grouping_status": "SOURCE_EXPLICIT",
        "original_split": None,
        "field_holdout": False,
        "canonical_fingerprint": None,
        "materialization_evidence": ["fixture"],
        "stage_status": stage,
        "blocking_reasons": [],
    }


class LedgerTests(unittest.TestCase):
    def test_summary_counts_underlying_family_not_wrapper(self) -> None:
        rows = [
            row("fsd:1", "fsd50k-1.0", "FREESOUND", label="SIREN"),
            row("direct:2", "echo-freesound-release-safe-v1", "FREESOUND", label="SIREN"),
            row("sonyc:3", "sonyc-ust-v2", "SONYC_UST", label="SIREN"),
        ]
        rows[2]["media_sha256"] = "c" * 64
        summary = summarize_ledger(rows)
        self.assertEqual(summary["positive_counts"]["SIREN"], 3)
        self.assertEqual(summary["positive_underlying_source_family_counts"]["SIREN"], 2)

    def test_ready_row_cannot_hide_missing_probe(self) -> None:
        value = row("x:1", "sonyc-ust-v2", "SONYC_UST", label="SIREN")
        value["audio_probe"] = None
        with self.assertRaises(ValueError):
            validate_ledger([value])

    def test_positive_and_hard_negative_same_target_is_rejected(self) -> None:
        value = row("x:1", "sonyc-ust-v2", "SONYC_UST", label="SIREN", hard_negative="SIREN")
        with self.assertRaises(ValueError):
            validate_ledger([value])

    def test_underlying_source_policy_requires_registered_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "policy.json"
            path.write_text(json.dumps({
                "schema_version": "echo.underlying-source-families.v1",
                "sources": {"a": {"family": "F"}},
            }), encoding="utf-8")
            policy = load_underlying_source_policy(path)
            self.assertEqual(underlying_source_family(policy, "a"), "F")
            with self.assertRaises(ValueError):
                underlying_source_family(policy, "missing")

if __name__ == '__main__': unittest.main()

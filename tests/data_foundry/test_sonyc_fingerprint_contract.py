from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.data_foundry.validate_sonyc_fingerprint_contract import (
    CONFUSER_FILE,
    SUMMARY_FILE,
    TARGET_FILE,
    validate_fingerprint,
    validate_materialization,
)


class SonycFingerprintContractTests(unittest.TestCase):
    def valid_fingerprint(self, seed: int = 1) -> dict:
        vector = [(seed + index) % 256 for index in range(128)]
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
            "decoded_sample_count": 160000,
            "canonical_pcm_sha256": "a" * 64,
            "vector_sha256": hashlib.sha256(bytes(vector)).hexdigest(),
            "vector": vector,
        }

    def candidate(self, asset_id: str, fingerprint: dict, *, labels: bool) -> dict:
        row = {
            "source_dataset": "sonyc-ust-v2",
            "source_release": "2.3",
            "source_asset_id": asset_id,
            "sha256": hashlib.sha256(asset_id.encode("utf-8")).hexdigest(),
            "byte_size": 320044,
            "audio_probe": {
                "ok": True,
                "sample_rate_hz": 16000,
                "channels": 1,
                "duration_seconds": 10.0,
            },
            "canonical_fingerprint": fingerprint,
            "fingerprint_error": None,
            "license_id": "CC-BY-4.0",
            "split": "train",
            "recording_group_candidate": "sonyc:test",
            "archive": "audio-0.tar.gz",
            "archive_member": f"audio/{asset_id}.wav",
        }
        if labels:
            row["echo_labels"] = ["SIREN"]
        else:
            row["confuses"] = ["SIREN"]
            row["source_confusers"] = ["car-alarm"]
        return row

    def write_fixture(self, root: Path, targets: list[dict], confusers: list[dict]) -> None:
        unique = {
            (row["source_dataset"], row["source_asset_id"], row["sha256"])
            for row in [*targets, *confusers]
        }
        summary = {
            "schema_version": "echo.sonyc-full-materialization-summary.v2",
            "fingerprint_failures": 0,
            "fingerprinted_ledger_relevant_assets": len(unique),
            "target_candidate_count": len(targets),
            "confuser_candidate_count": len(confusers),
        }
        (root / SUMMARY_FILE).write_text(json.dumps(summary), encoding="utf-8")
        for filename, rows in ((TARGET_FILE, targets), (CONFUSER_FILE, confusers)):
            with (root / filename).open("w", encoding="utf-8") as handle:
                for row in rows:
                    handle.write(json.dumps(row) + "\n")

    def test_real_contract_uses_vector_sha256_not_generic_digest(self) -> None:
        fingerprint = self.valid_fingerprint()
        self.assertNotIn("digest", fingerprint)
        self.assertEqual(validate_fingerprint(fingerprint), [])

    def test_missing_vector_sha256_fails_closed(self) -> None:
        fingerprint = self.valid_fingerprint()
        fingerprint.pop("vector_sha256")
        errors = validate_fingerprint(fingerprint)
        self.assertTrue(any("vector_sha256" in error for error in errors))

    def test_semantic_overlap_counts_one_unique_ledger_asset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fingerprint = self.valid_fingerprint()
            target = self.candidate("clip-1", fingerprint, labels=True)
            confuser = self.candidate("clip-1", fingerprint, labels=False)
            self.write_fixture(root, [target], [confuser])

            report = validate_materialization(root)

            self.assertEqual(report["candidate_rows_checked"], 2)
            self.assertEqual(report["unique_ledger_relevant_assets"], 1)

    def test_conflicting_fingerprint_for_same_asset_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = self.candidate("clip-1", self.valid_fingerprint(1), labels=True)
            confuser = self.candidate("clip-1", self.valid_fingerprint(2), labels=False)
            self.write_fixture(root, [target], [confuser])

            with self.assertRaisesRegex(ValueError, "conflicting fingerprint"):
                validate_materialization(root)


if __name__ == "__main__":
    unittest.main()

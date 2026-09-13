from __future__ import annotations

import json
import struct
import tempfile
import unittest
import wave
from pathlib import Path

from echo.data_foundry.contracts import AdmissionStatus, RawAssetCandidate
from echo.data_foundry.dataset import load_benchmark_split, validate_frozen_bundle
from echo.data_foundry.intake import read_candidate_manifest, write_candidate_manifest
from echo.data_foundry.pipeline import admit_from_files, freeze_corpus, load_split_policy, read_record_manifest


class FoundryPipelineTests(unittest.TestCase):
    def _write_wav(self, path: Path, envelope: list[int]) -> None:
        samples: list[int] = []
        for i, amplitude in enumerate(envelope):
            samples.append(amplitude if i % 40 < 20 else -amplitude)
        with wave.open(str(path), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes(b"".join(struct.pack("<h", sample) for sample in samples))

    def test_candidate_manifest_round_trip_is_deterministic(self) -> None:
        candidates = [
            RawAssetCandidate(source_dataset="sonyc-ust-v2", source_release="2.3", source_asset_id="b.wav", local_relpath="b.wav", license_id="CC-BY-4.0", original_labels=("car-horn",), recording_group_id="g2"),
            RawAssetCandidate(source_dataset="sonyc-ust-v2", source_release="2.3", source_asset_id="a.wav", local_relpath="a.wav", license_id="CC-BY-4.0", original_labels=("siren",), recording_group_id="g1"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            p1 = Path(tmp) / "c1.jsonl"
            p2 = Path(tmp) / "c2.jsonl"
            h1 = write_candidate_manifest(p1, candidates)
            h2 = write_candidate_manifest(p2, list(reversed(candidates)))
            self.assertEqual(h1, h2)
            loaded = read_candidate_manifest(p1)
            self.assertEqual([item.source_asset_id for item in loaded], ["a.wav", "b.wav"])

    def test_release_safe_admit_freeze_and_benchmark_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Different temporal envelopes ensure the near-duplicate screen does not
            # intentionally collapse the two fixtures merely because gain differs.
            self._write_wav(root / "a.wav", [1000] * 800 + [200] * 800)
            self._write_wav(root / "b.wav", [200] * 400 + [1500] * 800 + [200] * 400)
            candidates = [
                RawAssetCandidate(source_dataset="sonyc-ust-v2", source_release="2.3", source_asset_id="a.wav", local_relpath="a.wav", license_id="CC-BY-4.0", original_labels=("siren",), recording_group_id="g1", original_split="train"),
                RawAssetCandidate(source_dataset="sonyc-ust-v2", source_release="2.3", source_asset_id="b.wav", local_relpath="b.wav", license_id="CC-BY-4.0", original_labels=("car-horn",), recording_group_id="g2", original_split="test"),
            ]
            candidate_path = root / "candidates.jsonl"
            records_path = root / "records.jsonl"
            write_candidate_manifest(candidate_path, candidates)
            admit_from_files(
                candidate_manifest=candidate_path,
                mapping_path="configs/data_foundry/label_mapping.v1.json",
                license_policy_path="configs/data_foundry/license_policy.v1.json",
                profile="release_safe",
                output_path=records_path,
                audio_root=root,
            )
            records = read_record_manifest(records_path)
            self.assertEqual(len(records), 2)
            self.assertTrue(all(record.admission_status is AdmissionStatus.ADMITTED_RELEASE_SAFE for record in records))
            self.assertTrue(all(record.sample_rate_hz == 16000 for record in records))
            self.assertTrue(all(record.channels == 1 for record in records))
            self.assertTrue(all(record.extra.get("audio_probe", {}).get("ok") for record in records))
            self.assertNotEqual(records[0].extra.get("near_duplicate_fingerprint"), records[1].extra.get("near_duplicate_fingerprint"))

            source_registry = json.loads(Path("configs/data_foundry/source_registry.v1.json").read_text(encoding="utf-8"))
            license_policy = json.loads(Path("configs/data_foundry/license_policy.v1.json").read_text(encoding="utf-8"))
            mapping = json.loads(Path("configs/data_foundry/label_mapping.v1.json").read_text(encoding="utf-8"))
            split_policy = load_split_policy("configs/data_foundry/split_policy.v1.json")
            bundle = root / "frozen"
            result = freeze_corpus(
                records=records,
                output_dir=bundle,
                manifest_id="test-manifest",
                profile="release_safe",
                taxonomy_version="echo.taxonomy.v1",
                source_registry=source_registry,
                license_policy=license_policy,
                label_mapping=mapping,
                split_policy=split_policy,
            )
            self.assertTrue(result["status"].startswith("PASS"))
            self.assertEqual(result["admitted_assets"], 2)
            identity = validate_frozen_bundle(bundle)
            self.assertEqual(identity["asset_count"], 2)
            train = load_benchmark_split(bundle, "train")
            test = load_benchmark_split(bundle, "test")
            self.assertEqual([row["asset_id"] for row in train], ["sonyc-ust-v2:a.wav"])
            self.assertEqual([row["asset_id"] for row in test], ["sonyc-ust-v2:b.wav"])

    def test_corrupt_audio_is_quarantined(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "bad.wav").write_bytes(b"not-a-wave")
            candidates = [RawAssetCandidate(
                source_dataset="sonyc-ust-v2", source_release="2.3", source_asset_id="bad.wav",
                local_relpath="bad.wav", license_id="CC-BY-4.0", original_labels=("siren",),
                recording_group_id="g-bad",
            )]
            candidate_path = root / "candidates.jsonl"
            records_path = root / "records.jsonl"
            write_candidate_manifest(candidate_path, candidates)
            admit_from_files(
                candidate_manifest=candidate_path,
                mapping_path="configs/data_foundry/label_mapping.v1.json",
                license_policy_path="configs/data_foundry/license_policy.v1.json",
                profile="release_safe",
                output_path=records_path,
                audio_root=root,
            )
            record = read_record_manifest(records_path)[0]
            self.assertEqual(record.admission_status, AdmissionStatus.QUARANTINED)
            self.assertIn("AUDIO_PROBE_FAILED", record.reason_codes)


if __name__ == "__main__":
    unittest.main()

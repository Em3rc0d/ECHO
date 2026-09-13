from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from echo.data_foundry.contracts import AdmissionStatus, RawAssetCandidate
from echo.data_foundry.intake import read_candidate_manifest, write_candidate_manifest
from echo.data_foundry.pipeline import admit_from_files, freeze_corpus, load_split_policy, read_record_manifest


class FoundryPipelineTests(unittest.TestCase):
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

    def test_release_safe_admit_and_freeze(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.wav").write_bytes(b"audio-a")
            (root / "b.wav").write_bytes(b"audio-b")
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

            source_registry = json.loads(Path("configs/data_foundry/source_registry.v1.json").read_text(encoding="utf-8"))
            license_policy = json.loads(Path("configs/data_foundry/license_policy.v1.json").read_text(encoding="utf-8"))
            mapping = json.loads(Path("configs/data_foundry/label_mapping.v1.json").read_text(encoding="utf-8"))
            split_policy = load_split_policy("configs/data_foundry/split_policy.v1.json")
            result = freeze_corpus(
                records=records,
                output_dir=root / "frozen",
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
            self.assertTrue((root / "frozen" / "dataset-manifest.json").exists())
            split_manifest = json.loads((root / "frozen" / "split-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(split_manifest["assignments"]["sonyc-ust-v2:a.wav"], "train")
            self.assertEqual(split_manifest["assignments"]["sonyc-ust-v2:b.wav"], "test")


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from echo.data_foundry.admission import materialize_asset_record
from echo.data_foundry.contracts import AdmissionStatus, RawAssetCandidate
from echo.data_foundry.mapping import LabelMapper


class AdmissionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mapper = LabelMapper(
            {
                "schema_version": "echo.label-mapping.v1",
                "sources": {
                    "source": {
                        "Siren": {
                            "status": "EXACT",
                            "echo_labels": ["SIREN"],
                            "review_required": False,
                            "use": "positive",
                        },
                        "Shatter": {
                            "status": "BROADER",
                            "echo_labels": ["GLASS_SHATTER"],
                            "review_required": True,
                            "use": "positive_after_review",
                        },
                    }
                },
            }
        )

    def test_permissive_exact_asset_is_admitted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            audio = Path(tmp) / "a.wav"
            audio.write_bytes(b"deterministic-placeholder-bytes")
            candidate = RawAssetCandidate(
                source_dataset="source",
                source_release="1",
                source_asset_id="a",
                local_relpath=str(audio),
                license_id="CC-BY-4.0",
                original_labels=("Siren",),
                recording_group_id="group-a",
            )
            record = materialize_asset_record(
                candidate,
                mapper=self.mapper,
                profile="release_safe",
            )
            self.assertEqual(record.admission_status, AdmissionStatus.ADMITTED_RELEASE_SAFE)
            self.assertEqual(record.echo_labels, ("SIREN",))
            self.assertEqual(len(record.sha256), 64)

    def test_broad_positive_is_quarantined_without_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            audio = Path(tmp) / "a.wav"
            audio.write_bytes(b"data")
            candidate = RawAssetCandidate(
                source_dataset="source",
                source_release="1",
                source_asset_id="a",
                local_relpath=str(audio),
                license_id="CC-BY-4.0",
                original_labels=("Shatter",),
                recording_group_id="group-a",
            )
            record = materialize_asset_record(candidate, mapper=self.mapper, profile="release_safe")
            self.assertEqual(record.admission_status, AdmissionStatus.QUARANTINED)
            self.assertIn("LABEL_REVIEW_REQUIRED", record.reason_codes)

    def test_noncommercial_asset_cannot_enter_release_safe_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            audio = Path(tmp) / "a.wav"
            audio.write_bytes(b"data")
            candidate = RawAssetCandidate(
                source_dataset="source",
                source_release="1",
                source_asset_id="a",
                local_relpath=str(audio),
                license_id="CC-BY-NC-3.0",
                original_labels=("Siren",),
                recording_group_id="group-a",
            )
            record = materialize_asset_record(candidate, mapper=self.mapper, profile="release_safe")
            self.assertEqual(record.admission_status, AdmissionStatus.QUARANTINED)
            self.assertIn("LICENSE_RESEARCH_ONLY_FOR_REQUESTED_PROFILE", record.reason_codes)


if __name__ == "__main__":
    unittest.main()

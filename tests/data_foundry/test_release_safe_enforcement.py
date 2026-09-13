from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from echo.data_foundry.contracts import AdmissionStatus, AssetRecord, MappingStatus, UseDecision
from echo.data_foundry.coverage_policy import load_coverage_policy
from echo.data_foundry.dataset import validate_frozen_bundle
from echo.data_foundry.pipeline import freeze_corpus, load_split_policy
from echo.data_foundry.source_policy import load_dataset_certification


class ReleaseSafeEnforcementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source_registry = json.loads(Path("configs/data_foundry/source_registry.v1.json").read_text(encoding="utf-8"))
        cls.license_policy = json.loads(Path("configs/data_foundry/license_policy.v1.json").read_text(encoding="utf-8"))
        cls.mapping = json.loads(Path("configs/data_foundry/label_mapping.v1.json").read_text(encoding="utf-8"))
        cls.split_policy = load_split_policy("configs/data_foundry/split_policy.v1.json")
        cls.source_certification = load_dataset_certification("configs/data_foundry/dataset_certification.v1.json")
        cls.coverage_policy = load_coverage_policy("configs/data_foundry/coverage_policy.v1.json")

    def _record(
        self,
        *,
        admission_status: AdmissionStatus = AdmissionStatus.ADMITTED_RELEASE_SAFE,
        use_decision: UseDecision = UseDecision.ALLOW_RELEASE_SAFE,
    ) -> AssetRecord:
        return AssetRecord(
            asset_id="sonyc-ust-v2:fixture.wav",
            source_dataset="sonyc-ust-v2",
            source_release="2.3",
            source_asset_id="fixture.wav",
            sha256="a" * 64,
            license_id="CC-BY-4.0",
            use_decision=use_decision,
            original_labels=("siren",),
            echo_labels=("SIREN",),
            mapping_status=MappingStatus.EXACT,
            recording_group_id="fixture-group",
            admission_status=admission_status,
            duration_seconds=10.0,
            label_provenance="test_fixture",
            extra={"audio_probe": {"ok": True}},
        )

    def _freeze(self, root: Path, **overrides):
        kwargs = dict(
            records=[self._record()],
            output_dir=root / "bundle",
            manifest_id="release-safe-enforcement-fixture",
            profile="release_safe",
            taxonomy_version="echo.taxonomy.v1",
            source_registry=self.source_registry,
            license_policy=self.license_policy,
            label_mapping=self.mapping,
            split_policy=self.split_policy,
            source_certification=self.source_certification,
            coverage_policy=self.coverage_policy,
        )
        kwargs.update(overrides)
        return freeze_corpus(**kwargs)

    def test_release_safe_direct_api_cannot_omit_source_certification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "source certification"):
                self._freeze(Path(tmp), source_certification=None)

    def test_release_safe_direct_api_cannot_omit_coverage_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "coverage policy"):
                self._freeze(Path(tmp), coverage_policy=None)

    def test_release_safe_rejects_research_only_admission_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "incompatible with release_safe"):
                self._freeze(
                    Path(tmp),
                    records=[
                        self._record(
                            admission_status=AdmissionStatus.ADMITTED_RESEARCH_ONLY,
                            use_decision=UseDecision.ALLOW_RESEARCH_ONLY,
                        )
                    ],
                )

    def test_release_safe_rejects_asset_without_release_safe_rights(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "release-safe asset rights"):
                self._freeze(
                    Path(tmp),
                    records=[self._record(use_decision=UseDecision.ALLOW_RESEARCH_ONLY)],
                )

    def test_production_policy_fails_tiny_incomplete_release_safe_corpus(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = self._freeze(root)
            self.assertEqual(result["status"], "FAIL_COVERAGE_GATE")
            self.assertTrue(result["coverage_gaps"])
            with self.assertRaisesRegex(ValueError, "unresolved corpus coverage"):
                validate_frozen_bundle(root / "bundle")


if __name__ == "__main__":
    unittest.main()

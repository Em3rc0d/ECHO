from __future__ import annotations

import unittest

from echo.data_foundry.certification import (
    CERTIFICATE_ONLY_GAP,
    CORPUS_CERTIFICATE_ID,
    DATASET_EMPIRICAL_ID,
    DATA_QUALITY_EMPIRICAL_ID,
    apply_corpus_certificate,
    build_corpus_certificate,
    certificate_sha256,
    validate_corpus_certificate,
    validate_pre_certificate_readiness,
)
from echo.data_foundry.readiness import REQUIRED_EVIDENCE_NODES


class CorpusCertificationTests(unittest.TestCase):
    def _readiness(self) -> dict:
        return {
            "readiness_id": "EMP-MK1-CORPUS-READINESS-001",
            "status": "BLOCKED",
            "modeling_allowed": False,
            "eligible_for_certificate_review": True,
            "evidence_identity_sha256": "1" * 64,
            "gap_codes": [CERTIFICATE_ONLY_GAP],
            "corpus_certificate": {
                "id": CORPUS_CERTIFICATE_ID,
                "status": "OPEN",
            },
            "inputs": {
                "canonical_ledger_summary": {
                    "sha256": "2" * 64,
                    "baseline_commit": "abc1234",
                    "ledger_sha256": "3" * 64,
                    "entry_count": 500,
                },
                "coverage_policy": {
                    "sha256": "4" * 64,
                    "policy_id": "MK1-CORPUS-SOLIDITY-001",
                    "schema_version": "echo.coverage-policy.v1",
                },
            },
            "closure_evidence_nodes": {
                node: {
                    "filename": filename,
                    "present": True,
                    "status": "PASS",
                    "sha256": f"{index + 5:x}" * 64,
                    "pass": True,
                }
                for index, (node, filename) in enumerate(REQUIRED_EVIDENCE_NODES.items())
            },
            "next_authorized_stage": "CORPUS_FOUNDRY_CLOSURE",
        }

    def _certificate(self) -> dict:
        return build_corpus_certificate(
            readiness=self._readiness(),
            git_commit="abc1234",
            generated_at_utc="2026-09-15T00:00:00Z",
            free_tier_policy_sha256="a" * 64,
            toolchain_certificate_sha256="b" * 64,
            documentation_certificate_sha256="c" * 64,
            github_run_id="12345",
        )

    def test_pre_certificate_requires_certificate_as_only_gap(self) -> None:
        readiness = self._readiness()
        self.assertEqual(validate_pre_certificate_readiness(readiness), [])
        readiness["gap_codes"].append("COVERAGE_GATE_NOT_PASS")
        failures = validate_pre_certificate_readiness(readiness)
        self.assertTrue(failures)

    def test_certificate_materializes_required_empirical_outputs(self) -> None:
        certificate = self._certificate()
        self.assertEqual(certificate["artifact_id"], CORPUS_CERTIFICATE_ID)
        self.assertEqual(certificate["status"], "CERTIFIED")
        self.assertEqual(
            certificate["empirical_outputs"][DATASET_EMPIRICAL_ID]["status"], "PASS"
        )
        self.assertEqual(
            certificate["empirical_outputs"][DATA_QUALITY_EMPIRICAL_ID]["status"],
            "PASS",
        )
        self.assertEqual(certificate["certificate_sha256"], certificate_sha256(certificate))

    def test_valid_certificate_unlocks_only_matching_evidence_identity(self) -> None:
        readiness = self._readiness()
        certificate = self._certificate()
        final = apply_corpus_certificate(readiness, certificate)
        self.assertTrue(final["modeling_allowed"])
        self.assertEqual(final["status"], "READY")
        self.assertEqual(final["gap_codes"], [])
        self.assertEqual(final["next_authorized_stage"], "BENCHMARK_A_B_C")

    def test_stale_certificate_fails_closed(self) -> None:
        readiness = self._readiness()
        readiness["evidence_identity_sha256"] = "d" * 64
        final = apply_corpus_certificate(readiness, self._certificate())
        self.assertFalse(final["modeling_allowed"])
        self.assertEqual(final["status"], "BLOCKED")
        self.assertEqual(final["corpus_certificate"]["status"], "INVALIDATED")
        self.assertIn("CORPUS_CERTIFICATE_INVALID", final["gap_codes"])

    def test_tampered_certificate_hash_is_rejected(self) -> None:
        certificate = self._certificate()
        certificate["scope"] = "tampered"
        failures = validate_corpus_certificate(
            certificate, evidence_identity_sha256="1" * 64
        )
        self.assertIn("certificate_sha256 does not match certificate payload", failures)


if __name__ == "__main__":
    unittest.main()

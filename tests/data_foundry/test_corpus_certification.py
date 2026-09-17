from __future__ import annotations

import copy
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
    FREE_TIER_SHA = "a" * 64
    TOOLCHAIN_SHA = "b" * 64
    HANDOFF_SHA = "c" * 64

    def _readiness(self) -> dict:
        closure_hashes = {
            node: f"{index + 5:064x}"
            for index, node in enumerate(sorted(REQUIRED_EVIDENCE_NODES))
        }
        return {
            "schema_version": "echo.corpus-closure-readiness.v2",
            "readiness_id": "EMP-MK1-CORPUS-READINESS-001",
            "profile": "release_safe",
            "status": "BLOCKED",
            "modeling_allowed": False,
            "eligible_for_certificate_review": True,
            "release_law": "certificate required before model entry",
            "evidence_identity_sha256": "1" * 64,
            "evidence_identity_material": {
                "canonical_ledger_semantic_sha256": "3" * 64,
                "coverage_policy_sha256": "4" * 64,
                "closure_evidence_sha256": closure_hashes,
            },
            "gap_codes": [CERTIFICATE_ONLY_GAP],
            "corpus_certificate": {
                "id": CORPUS_CERTIFICATE_ID,
                "status": "OPEN",
            },
            "inputs": {
                "canonical_ledger_summary": {
                    "sha256": "2" * 64,
                    "baseline_commit": "d" * 40,
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
                    "sha256": closure_hashes[node],
                    "pass": True,
                }
                for node, filename in REQUIRED_EVIDENCE_NODES.items()
            },
            "ledger_blocking_reason_counts": {},
            "target_readiness": {},
            "next_authorized_stage": "CORPUS_FOUNDRY_CLOSURE",
        }

    def _certificate(self) -> dict:
        return build_corpus_certificate(
            readiness=self._readiness(),
            git_commit="e" * 40,
            generated_at_utc="2026-09-16T23:00:00Z",
            free_tier_policy_sha256=self.FREE_TIER_SHA,
            toolchain_certificate_sha256=self.TOOLCHAIN_SHA,
            handoff_certificate_sha256=self.HANDOFF_SHA,
            github_run_id="12345",
        )

    def _apply(self, readiness: dict, certificate: dict) -> dict:
        return apply_corpus_certificate(
            readiness,
            certificate,
            free_tier_policy_sha256=self.FREE_TIER_SHA,
            toolchain_certificate_sha256=self.TOOLCHAIN_SHA,
            handoff_certificate_sha256=self.HANDOFF_SHA,
        )

    def test_pre_certificate_requires_certificate_as_only_gap(self) -> None:
        readiness = self._readiness()
        self.assertEqual(validate_pre_certificate_readiness(readiness), [])
        readiness["gap_codes"].append("COVERAGE_GATE_NOT_PASS")
        self.assertTrue(validate_pre_certificate_readiness(readiness))

    def test_pre_certificate_requires_semantic_identity_binding(self) -> None:
        readiness = self._readiness()
        readiness["inputs"]["canonical_ledger_summary"]["ledger_sha256"] = "f" * 64
        failures = validate_pre_certificate_readiness(readiness)
        self.assertIn("canonical ledger input disagrees with semantic identity", failures)

    def test_certificate_materializes_required_empirical_outputs(self) -> None:
        certificate = self._certificate()
        self.assertEqual(certificate["artifact_id"], CORPUS_CERTIFICATE_ID)
        self.assertEqual(certificate["schema_version"], "echo.corpus-certificate.v2")
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
        final = self._apply(self._readiness(), self._certificate())
        self.assertTrue(final["modeling_allowed"])
        self.assertEqual(final["status"], "READY")
        self.assertEqual(final["gap_codes"], [])
        self.assertEqual(final["next_authorized_stage"], "BENCHMARK_A_B_C")
        self.assertEqual(final["corpus_certificate"]["status"], "CERTIFIED")

    def test_provenance_only_rebuild_does_not_invalidate_certificate(self) -> None:
        readiness = self._readiness()
        readiness["inputs"]["canonical_ledger_summary"]["baseline_commit"] = "f" * 40
        readiness["inputs"]["canonical_ledger_summary"]["sha256"] = "0" * 64
        final = self._apply(readiness, self._certificate())
        self.assertTrue(final["modeling_allowed"])
        self.assertEqual(final["status"], "READY")

    def test_stale_semantic_identity_fails_closed(self) -> None:
        readiness = self._readiness()
        readiness["evidence_identity_sha256"] = "9" * 64
        final = self._apply(readiness, self._certificate())
        self.assertFalse(final["modeling_allowed"])
        self.assertEqual(final["status"], "BLOCKED")
        self.assertEqual(final["corpus_certificate"]["status"], "INVALIDATED")
        self.assertIn("CORPUS_CERTIFICATE_INVALID", final["gap_codes"])

    def test_stable_ancestor_drift_fails_closed(self) -> None:
        for kwargs, expected in (
            ({"free_tier_policy_sha256": "9" * 64}, "free-tier policy ancestor hash drifted"),
            ({"toolchain_certificate_sha256": "9" * 64}, "toolchain certificate ancestor hash drifted"),
            ({"handoff_certificate_sha256": "9" * 64}, "handoff certificate ancestor hash drifted"),
        ):
            with self.subTest(expected=expected):
                params = {
                    "free_tier_policy_sha256": self.FREE_TIER_SHA,
                    "toolchain_certificate_sha256": self.TOOLCHAIN_SHA,
                    "handoff_certificate_sha256": self.HANDOFF_SHA,
                }
                params.update(kwargs)
                failures = validate_corpus_certificate(
                    self._certificate(),
                    evidence_identity_sha256="1" * 64,
                    **params,
                )
                self.assertIn(expected, failures)

    def test_tampered_certificate_hash_is_rejected(self) -> None:
        certificate = copy.deepcopy(self._certificate())
        certificate["scope"] = "tampered"
        failures = validate_corpus_certificate(
            certificate,
            evidence_identity_sha256="1" * 64,
            free_tier_policy_sha256=self.FREE_TIER_SHA,
            toolchain_certificate_sha256=self.TOOLCHAIN_SHA,
            handoff_certificate_sha256=self.HANDOFF_SHA,
        )
        self.assertIn("certificate_sha256 does not match certificate payload", failures)


if __name__ == "__main__":
    unittest.main()

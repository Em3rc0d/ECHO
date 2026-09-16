from __future__ import annotations

import unittest

from echo.data_foundry.readiness import REQUIRED_EVIDENCE_NODES, evaluate_readiness


class CorpusClosureReadinessTests(unittest.TestCase):
    def _policy(self) -> dict:
        targets = {}
        hard = {}
        for label in (
            "GLASS_SHATTER",
            "SIREN",
            "FIRE_ALARM",
            "VEHICLE_HORN",
            "TIRE_SQUEAL",
        ):
            targets[label] = {
                "min_assets": 50,
                "min_independent_groups": 25,
                "min_sources": 2,
                "min_clip_duration_seconds": 180.0,
            }
            hard[label] = {
                "min_assets": 20,
                "min_independent_groups": 10,
                "min_sources": 2,
            }
        return {
            "schema_version": "echo.coverage-policy.v1",
            "policy_id": "MK1-CORPUS-SOLIDITY-001",
            "profiles": {
                "release_safe": {
                    "target_labels": targets,
                    "hard_negatives": {"per_target": hard},
                }
            },
        }

    def _ledger(self, *, certified: bool = False) -> dict:
        labels = (
            "GLASS_SHATTER",
            "SIREN",
            "FIRE_ALARM",
            "VEHICLE_HORN",
            "TIRE_SQUEAL",
        )
        return {
            "baseline_commit": "a" * 40,
            "entry_count": 500,
            "ledger_sha256": "d" * 64,
            "corpus_certificate": {
                "id": "CERT-MK1-DF-CORPUS-001",
                "status": "CERTIFIED" if certified else "OPEN",
            },
            "positive_counts": {label: 60 for label in labels},
            "positive_underlying_source_family_counts": {label: 2 for label in labels},
            "hard_negative_counts": {label: 25 for label in labels},
            "hard_negative_underlying_source_family_counts": {label: 2 for label in labels},
            "blocking_reason_counts": {},
            "canonical_fingerprint_missing_count": 0,
        }

    def _evidence(self) -> dict:
        return {
            node: {"status": "PASS", "gap_codes": []}
            for node in REQUIRED_EVIDENCE_NODES
        }

    def _hashes(self) -> dict:
        return {
            "canonical_ledger_summary": "a" * 64,
            "coverage_policy": "b" * 64,
            **{node: "c" * 64 for node in REQUIRED_EVIDENCE_NODES},
        }

    def test_open_certificate_keeps_modeling_locked_even_when_closure_inputs_pass(self) -> None:
        result = evaluate_readiness(
            ledger_summary=self._ledger(certified=False),
            coverage_policy=self._policy(),
            evidence_artifacts=self._evidence(),
            evidence_hashes=self._hashes(),
        )
        self.assertTrue(result["eligible_for_certificate_review"])
        self.assertFalse(result["modeling_allowed"])
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("CORPUS_CERTIFICATE_NOT_CERTIFIED", result["gap_codes"])

    def test_certified_complete_evidence_unlocks_modeling(self) -> None:
        result = evaluate_readiness(
            ledger_summary=self._ledger(certified=True),
            coverage_policy=self._policy(),
            evidence_artifacts=self._evidence(),
            evidence_hashes=self._hashes(),
        )
        self.assertTrue(result["eligible_for_certificate_review"])
        self.assertTrue(result["modeling_allowed"])
        self.assertEqual(result["status"], "READY")
        self.assertEqual(result["gap_codes"], [])
        self.assertEqual(result["next_authorized_stage"], "BENCHMARK_A_B_C")

    def test_missing_fire_alarm_floor_fails_closed(self) -> None:
        ledger = self._ledger(certified=True)
        ledger["positive_counts"]["FIRE_ALARM"] = 5
        result = evaluate_readiness(
            ledger_summary=ledger,
            coverage_policy=self._policy(),
            evidence_artifacts=self._evidence(),
            evidence_hashes=self._hashes(),
        )
        self.assertFalse(result["modeling_allowed"])
        self.assertIn("FIRE_ALARM_ASSETS_5_LT_50", result["gap_codes"])

    def test_missing_hard_negatives_fail_closed(self) -> None:
        ledger = self._ledger(certified=True)
        ledger["hard_negative_counts"]["TIRE_SQUEAL"] = 0
        ledger["hard_negative_underlying_source_family_counts"]["TIRE_SQUEAL"] = 0
        result = evaluate_readiness(
            ledger_summary=ledger,
            coverage_policy=self._policy(),
            evidence_artifacts=self._evidence(),
            evidence_hashes=self._hashes(),
        )
        self.assertIn("TIRE_SQUEAL_HARD_NEGATIVES_0_LT_20", result["gap_codes"])
        self.assertIn("TIRE_SQUEAL_HARD_NEGATIVE_SOURCES_0_LT_2", result["gap_codes"])

    def test_missing_closure_evidence_file_is_explicit_gap(self) -> None:
        evidence = self._evidence()
        evidence["reproducibility"] = None
        result = evaluate_readiness(
            ledger_summary=self._ledger(certified=True),
            coverage_policy=self._policy(),
            evidence_artifacts=evidence,
            evidence_hashes=self._hashes(),
        )
        self.assertIn("REPRODUCIBILITY_NOT_PASS", result["gap_codes"])
        self.assertFalse(result["modeling_allowed"])


if __name__ == "__main__":
    unittest.main()

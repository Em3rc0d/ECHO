from __future__ import annotations

import copy
import unittest

from echo.data_foundry.readiness import REQUIRED_EVIDENCE_NODES, evaluate_readiness


class ReadinessSemanticIdentityTests(unittest.TestCase):
    def _ledger(self) -> dict:
        return {
            "baseline_commit": "1" * 40,
            "ledger_sha256": "a" * 64,
            "entry_count": 10,
            "positive_counts": {},
            "positive_underlying_source_family_counts": {},
            "hard_negative_counts": {},
            "hard_negative_underlying_source_family_counts": {},
            "blocking_reason_counts": {},
            "canonical_fingerprint_missing_count": 0,
            "corpus_certificate": {
                "id": "CERT-MK1-DF-CORPUS-001",
                "status": "OPEN",
            },
        }

    def _policy(self) -> dict:
        targets = {
            name: {"min_assets": 0, "min_sources": 0}
            for name in (
                "GLASS_SHATTER",
                "SIREN",
                "FIRE_ALARM",
                "VEHICLE_HORN",
                "TIRE_SQUEAL",
            )
        }
        hard_negatives = {
            name: {"min_assets": 0, "min_sources": 0} for name in targets
        }
        return {
            "policy_id": "test-policy",
            "schema_version": "test",
            "profiles": {
                "release_safe": {
                    "target_labels": targets,
                    "hard_negatives": {"per_target": hard_negatives},
                }
            },
        }

    def _artifacts(self) -> tuple[dict, dict]:
        artifacts = {
            node: {"status": "PASS", "gap_codes": []}
            for node in REQUIRED_EVIDENCE_NODES
        }
        hashes = {
            node: f"{index + 1:064x}"
            for index, node in enumerate(sorted(REQUIRED_EVIDENCE_NODES))
        }
        hashes["coverage_policy"] = "b" * 64
        hashes["canonical_ledger_summary"] = "c" * 64
        return artifacts, hashes

    def _evaluate(self, ledger: dict, hashes: dict) -> dict:
        artifacts, _ = self._artifacts()
        return evaluate_readiness(
            ledger_summary=ledger,
            coverage_policy=self._policy(),
            evidence_artifacts=artifacts,
            evidence_hashes=hashes,
        )

    def test_execution_provenance_does_not_change_semantic_identity(self) -> None:
        ledger = self._ledger()
        _, hashes = self._artifacts()
        first = self._evaluate(ledger, hashes)

        moved = copy.deepcopy(ledger)
        moved["baseline_commit"] = "2" * 40
        changed_hashes = dict(hashes)
        changed_hashes["canonical_ledger_summary"] = "d" * 64
        second = self._evaluate(moved, changed_hashes)

        self.assertEqual(
            first["evidence_identity_sha256"], second["evidence_identity_sha256"]
        )
        self.assertNotEqual(
            first["inputs"]["canonical_ledger_summary"]["sha256"],
            second["inputs"]["canonical_ledger_summary"]["sha256"],
        )
        self.assertNotEqual(
            first["inputs"]["canonical_ledger_summary"]["baseline_commit"],
            second["inputs"]["canonical_ledger_summary"]["baseline_commit"],
        )

    def test_semantic_ledger_change_changes_readiness_identity(self) -> None:
        ledger = self._ledger()
        _, hashes = self._artifacts()
        first = self._evaluate(ledger, hashes)

        changed = copy.deepcopy(ledger)
        changed["ledger_sha256"] = "e" * 64
        second = self._evaluate(changed, hashes)

        self.assertNotEqual(
            first["evidence_identity_sha256"], second["evidence_identity_sha256"]
        )

    def test_identity_material_exposes_semantic_ledger_hash(self) -> None:
        ledger = self._ledger()
        _, hashes = self._artifacts()
        result = self._evaluate(ledger, hashes)
        self.assertEqual(result["schema_version"], "echo.corpus-closure-readiness.v2")
        self.assertEqual(
            result["evidence_identity_material"]["canonical_ledger_semantic_sha256"],
            ledger["ledger_sha256"],
        )


if __name__ == "__main__":
    unittest.main()

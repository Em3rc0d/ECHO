from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from scripts.data_foundry import augment_canonical_ledger_with_opengameart_cc0 as augmentation
from scripts.data_foundry.augment_canonical_ledger_with_opengameart_cc0 import (
    MANIFEST,
    REPORT,
    SOURCE_FAMILY,
    SOURCE_ID,
    TARGET,
    manifest_index,
    validate_report,
)


class OpenGameArtLedgerAugmentationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = json.loads(Path(MANIFEST).read_text(encoding="utf-8"))
        self.report = json.loads(Path(REPORT).read_text(encoding="utf-8"))
        self.governed = manifest_index(self.manifest)

    def test_durable_report_matches_governed_manifest(self) -> None:
        rows = validate_report(self.report, self.manifest, self.governed)
        self.assertEqual(len(rows), 45)
        self.assertEqual(sum(row["role"] == "positive_candidate" for row in rows), 6)
        self.assertEqual(sum(row["role"] == "hard_negative_candidate" for row in rows), 39)

    def test_source_identity_is_not_the_transport_host(self) -> None:
        self.assertEqual(SOURCE_ID, "echo-opengameart-rubberduck-cc0-v1")
        self.assertEqual(SOURCE_FAMILY, "OPENGAMEART_RUBBERDUCK")
        self.assertTrue(self.manifest["governance"]["mirror_is_not_source_family"])
        self.assertFalse(self.report["transport_evidence"]["source_credit"])

    def test_six_positive_variants_remain_one_recording_group(self) -> None:
        rows = validate_report(self.report, self.manifest, self.governed)
        positives = [row for row in rows if row["role"] == "positive_candidate"]
        self.assertEqual({row["target"] for row in positives}, {TARGET})
        self.assertEqual({row["recording_family"] for row in positives}, {"bfh1:glass_breaking"})

    def test_mirror_credit_inflation_fails_closed(self) -> None:
        mutated = copy.deepcopy(self.report)
        mutated["transport_evidence"]["source_credit"] = True
        with self.assertRaisesRegex(ValueError, "mirror"):
            validate_report(mutated, self.manifest, self.governed)

    def test_missing_fingerprint_fails_closed(self) -> None:
        mutated = copy.deepcopy(self.report)
        mutated["assets"][0]["canonical_fingerprint"] = None
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            validate_report(mutated, self.manifest, self.governed)

    def test_report_cannot_add_ungoverned_asset(self) -> None:
        mutated = copy.deepcopy(self.report)
        extra = copy.deepcopy(mutated["assets"][0])
        extra["source_asset_id"] = "ungoverned.ogg"
        mutated["assets"].append(extra)
        mutated["materialized_count"] += 1
        mutated["fingerprinted_count"] += 1
        with self.assertRaisesRegex(ValueError, "asset set"):
            validate_report(mutated, self.manifest, self.governed)

    def test_positive_semantic_drift_fails_closed(self) -> None:
        mutated_manifest = copy.deepcopy(self.manifest)
        first_positive = next(row for row in mutated_manifest["assets"] if row["role"] == "positive_candidate")
        first_positive["semantic"] = "generic_break_review_required"
        with self.assertRaisesRegex(ValueError, "positive semantic drift"):
            manifest_index(mutated_manifest)

    def test_real_durable_ledger_copy_accepts_exactly_governed_rows(self) -> None:
        baseline_ledger = augmentation.LEDGER
        baseline_summary = augmentation.SUMMARY
        baseline_count = sum(1 for line in baseline_ledger.read_text(encoding="utf-8").splitlines() if line.strip())

        with tempfile.TemporaryDirectory(dir=augmentation.ROOT) as directory:
            work = Path(directory)
            ledger = work / "ledger.jsonl"
            summary = work / "summary.json"
            shutil.copyfile(baseline_ledger, ledger)
            shutil.copyfile(baseline_summary, summary)

            with patch.object(augmentation, "LEDGER", ledger), patch.object(augmentation, "SUMMARY", summary):
                self.assertEqual(augmentation.main(), 0)

            rows = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines() if line.strip()]
            self.assertEqual(len(rows), baseline_count + 45)
            admitted = [row for row in rows if row["source_dataset"] == SOURCE_ID]
            self.assertEqual(len(admitted), 45)
            self.assertEqual(sum(TARGET in row.get("echo_labels", []) for row in admitted), 6)
            self.assertEqual(sum(TARGET in row.get("hard_negative_for", []) for row in admitted), 39)
            self.assertEqual(
                {row["recording_group_id"] for row in admitted if TARGET in row.get("echo_labels", [])},
                {"opengameart:rubberduck:bfh1:glass_breaking"},
            )
            self.assertTrue(all(row["underlying_source_family"] == SOURCE_FAMILY for row in admitted))
            self.assertTrue(all(row["stage_status"] == "READY_FOR_GLOBAL_DEDUP" for row in admitted))
            self.assertTrue(all((row.get("canonical_fingerprint") or {}).get("vector_sha256") for row in admitted))

            summary_payload = json.loads(summary.read_text(encoding="utf-8"))
            evidence = summary_payload["opengameart_rubberduck_cc0_augmentation"]
            self.assertEqual(evidence["status"], "PASS")
            self.assertEqual(evidence["stats"]["rows"], 45)
            self.assertEqual(evidence["stats"]["positive_rows"], 6)
            self.assertEqual(evidence["stats"]["hard_negative_rows"], 39)


if __name__ == "__main__":
    unittest.main()

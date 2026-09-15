from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.data_foundry import augment_canonical_ledger_with_till_behrend_glass as augmentation


class TillBehrendGlassLedgerAugmentationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = augmentation.read_json(augmentation.MANIFEST)
        self.report = augmentation.read_json(augmentation.REPORT)
        self.source = augmentation.governed_source(self.manifest)

    def test_current_durable_evidence_admits_exactly_one_till_positive(self) -> None:
        row = augmentation.validated_asset(self.report, self.source)
        self.assertEqual(row["source_id"], augmentation.SOURCE_ID)
        self.assertEqual(row["source_asset_id"], "glass_breaking.wav")
        self.assertEqual(row["role"], "positive_candidate")
        self.assertEqual(row["semantic_candidate"], "glass_shatter")
        self.assertEqual(row["underlying_source_family_candidate"], "OPENGAMEART_TILL_BEHREND")
        self.assertEqual(row["license_id"], "CC0")
        self.assertTrue(row["audio_probe"]["ok"])
        self.assertTrue(row["canonical_fingerprint"]["canonical_pcm_sha256"])
        self.assertTrue(row["canonical_fingerprint"]["vector_sha256"])

    def test_rubberduck_glass_named_rows_remain_review_only(self) -> None:
        archive_rows = [
            row
            for row in self.report["assets"]
            if row["source_id"] != augmentation.SOURCE_ID
        ]
        self.assertEqual(len(archive_rows), 11)
        self.assertTrue(all(row["role"] == "glass_named_review_candidate" for row in archive_rows))
        self.assertTrue(all(row["semantic_candidate"] == "glass_named_filename_review_required" for row in archive_rows))
        self.assertTrue(all(row["admission_status"] == "DISCOVERY_REVIEW_ONLY_NO_CORPUS_CREDIT" for row in archive_rows))

    def test_missing_fingerprint_fails_closed(self) -> None:
        mutated = json.loads(json.dumps(self.report))
        till = next(row for row in mutated["assets"] if row["source_id"] == augmentation.SOURCE_ID)
        till["canonical_fingerprint"] = None
        with self.assertRaises(ValueError):
            augmentation.validated_asset(mutated, self.source)

    def test_non_till_positive_fails_closed(self) -> None:
        mutated = json.loads(json.dumps(self.report))
        rubberduck = next(row for row in mutated["assets"] if row["source_id"] != augmentation.SOURCE_ID)
        rubberduck["role"] = "positive_candidate"
        with self.assertRaises(ValueError):
            augmentation.validated_asset(mutated, self.source)

    def test_source_family_policy_is_exact_and_distinct(self) -> None:
        family_policy = json.loads(Path(augmentation.FAMILY_POLICY_PATH).read_text(encoding="utf-8"))
        sources = family_policy["sources"]
        till = sources[augmentation.SOURCE_ID]
        rubberduck = sources["echo-opengameart-rubberduck-cc0-v1"]
        self.assertEqual(till["family"], "OPENGAMEART_TILL_BEHREND")
        self.assertTrue(till["diversity_credit"])
        self.assertEqual(rubberduck["family"], "OPENGAMEART_RUBBERDUCK")
        self.assertNotEqual(till["family"], rubberduck["family"])

    def test_source_policy_is_release_safe_allow(self) -> None:
        policy = json.loads(Path(augmentation.SOURCE_POLICY_PATH).read_text(encoding="utf-8"))
        source = policy["sources"][augmentation.SOURCE_ID]
        self.assertEqual(source["profiles"]["release_safe"], "ALLOW")
        self.assertEqual(source["source_release_status"], "CURATED_REAL_BYTE_EVIDENCE_CERTIFIED")
        self.assertEqual(source["evidence_urls"], ["https://opengameart.org/content/glass-break"])

    def test_real_augmentation_adds_exactly_one_ready_glass_row(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            ledger = temp / "ledger.jsonl"
            summary = temp / "summary.json"
            shutil.copy2(augmentation.LEDGER, ledger)
            shutil.copy2(augmentation.SUMMARY, summary)

            before_rows = augmentation.read_jsonl(ledger)
            before_summary = augmentation.read_json(summary)
            old_ledger, old_summary = augmentation.LEDGER, augmentation.SUMMARY
            try:
                augmentation.LEDGER = ledger
                augmentation.SUMMARY = summary
                self.assertEqual(augmentation.main(), 0)
            finally:
                augmentation.LEDGER = old_ledger
                augmentation.SUMMARY = old_summary

            after_rows = augmentation.read_jsonl(ledger)
            after_summary = augmentation.read_json(summary)
            self.assertEqual(len(after_rows), len(before_rows) + 1)
            self.assertEqual(
                after_summary["positive_counts"]["GLASS_SHATTER"],
                before_summary["positive_counts"]["GLASS_SHATTER"] + 1,
            )
            self.assertEqual(after_summary["canonical_fingerprint_missing_count"], 0)

            till_rows = [
                row
                for row in after_rows
                if row["ledger_asset_id"] == f"{augmentation.SOURCE_ID}:{augmentation.ASSET_ID}"
            ]
            self.assertEqual(len(till_rows), 1)
            till = till_rows[0]
            self.assertEqual(till["echo_labels"], ["GLASS_SHATTER"])
            self.assertEqual(till["underlying_source_family"], "OPENGAMEART_TILL_BEHREND")
            self.assertEqual(till["recording_group_id"], "opengameart:till-behrend:glass-breaking")
            self.assertEqual(till["stage_status"], "READY_FOR_GLOBAL_DEDUP")
            self.assertTrue(till["canonical_fingerprint"]["canonical_pcm_sha256"])


if __name__ == "__main__":
    unittest.main()

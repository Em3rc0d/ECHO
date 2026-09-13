from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from echo.data_foundry.materialization import (
    ensure_free_space,
    files_for_stage,
    load_json_object,
    plan_summary,
    validate_materialization_plan,
    zenodo_file_url,
)


class MaterializationTests(unittest.TestCase):
    def test_plan_is_versioned_and_covers_required_profiles(self) -> None:
        plan = load_json_object("configs/data_foundry/materialization_plan.v1.json")
        validate_materialization_plan(plan)
        summary = plan_summary(plan)
        self.assertEqual(summary["plan_id"], "MK1-DATA-MATERIALIZATION-001")
        self.assertIn("release_safe", plan["profiles"])
        self.assertIn("research_extended", plan["profiles"])
        self.assertIn("echo-freesound-exact-gap-v1", plan["sources"])
        self.assertIn("echo-bigsoundbank-cc0-gap-v1", plan["sources"])

    def test_release_safe_plan_keeps_synthetic_data_out_of_independent_source_credit(self) -> None:
        plan = load_json_object("configs/data_foundry/materialization_plan.v1.json")
        synth = plan["sources"]["shantycam-smoke-synth"]
        self.assertFalse(synth["independent_source_credit"])

    def test_gap_candidate_config_keeps_discovery_separate_from_admission(self) -> None:
        payload = json.loads(Path("configs/data_foundry/gap_source_candidates.v1.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["schema_version"], "echo.gap-source-candidates.v1")
        fsd = payload["sources"]["echo-freesound-exact-gap-v1"]
        self.assertEqual(fsd["targets"]["FIRE_ALARM"]["expected_candidate_count"], 87)
        self.assertEqual(fsd["targets"]["TIRE_SQUEAL"]["expected_candidate_count"], 23)
        self.assertIn("Manual review", fsd["admission"])

    def test_zenodo_url_builder_is_deterministic(self) -> None:
        url = zenodo_file_url("https://zenodo.org/records/123/", "x.zip")
        self.assertEqual(url, "https://zenodo.org/records/123/files/x.zip?download=1")

    def test_stage_filter_uses_registry_required_for(self) -> None:
        source = {
            "files": [
                {"name": "meta.csv", "required_for": ["metadata", "full"]},
                {"name": "audio.zip", "required_for": ["full"]},
            ]
        }
        self.assertEqual([r["name"] for r in files_for_stage(source, "metadata")], ["meta.csv"])
        self.assertEqual([r["name"] for r in files_for_stage(source, "full")], ["meta.csv", "audio.zip"])

    def test_free_space_guard_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(RuntimeError):
                ensure_free_space(tmp, 10**18)


if __name__ == "__main__":
    unittest.main()

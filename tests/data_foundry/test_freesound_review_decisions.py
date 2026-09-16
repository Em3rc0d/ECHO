from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
SUPPLEMENTAL = ROOT / "configs/data_foundry/freesound_cc0_supplemental.v1.json"
DECISIONS = ROOT / "configs/data_foundry/review_decisions.v1.json"
EXACT = {"FIRE_ALARM": "fire_alarm", "TIRE_SQUEAL": "tire_squeal"}


class FreesoundReviewDecisionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.supplemental = json.loads(SUPPLEMENTAL.read_text(encoding="utf-8"))
        cls.decisions = json.loads(DECISIONS.read_text(encoding="utf-8"))
        cls.rows = {
            (target, int(row["sound_id"])): row
            for target, rows in cls.supplemental["targets"].items()
            for row in rows
        }

    def test_review_decision_keys_are_unique(self) -> None:
        keys = [
            (str(row["source_dataset"]), str(row["target"]), int(row["sound_id"]))
            for row in self.decisions["decisions"]
        ]
        self.assertEqual(len(keys), len(set(keys)))

    def test_admit_exact_decisions_match_operational_supplemental(self) -> None:
        admits = [row for row in self.decisions["decisions"] if row["decision"] == "ADMIT_EXACT"]
        self.assertGreater(len(admits), 0)
        for decision in admits:
            target = str(decision["target"])
            sound_id = int(decision["sound_id"])
            with self.subTest(target=target, sound_id=sound_id):
                self.assertIn((target, sound_id), self.rows)
                operational = self.rows[(target, sound_id)]
                self.assertEqual(operational["semantic"], EXACT[target])
                self.assertEqual(decision["canonical_semantic"], EXACT[target])
                self.assertTrue(str(operational["recording_family"]).strip())
                self.assertTrue(str(decision.get("page_title") or "").startswith("Freesound - "))
                self.assertEqual(len(str(decision.get("page_sha256") or "")), 64)

    def test_keep_review_required_never_receives_exact_credit(self) -> None:
        for decision in self.decisions["decisions"]:
            if decision["decision"] != "KEEP_REVIEW_REQUIRED":
                continue
            target = str(decision["target"])
            sound_id = int(decision["sound_id"])
            operational = self.rows.get((target, sound_id))
            if operational is None:
                continue
            with self.subTest(target=target, sound_id=sound_id):
                self.assertNotEqual(operational["semantic"], EXACT[target])

    def test_known_same_session_tire_series_are_one_recording_family(self) -> None:
        chrysler = {
            self.rows[("TIRE_SQUEAL", sid)]["recording_family"]
            for sid in (71736, 71737, 71738, 71739)
        }
        nordschleife = {
            self.rows[("TIRE_SQUEAL", sid)]["recording_family"]
            for sid in (350671, 350677)
        }
        self.assertEqual(len(chrysler), 1)
        self.assertEqual(len(nordschleife), 1)


if __name__ == "__main__":
    unittest.main()

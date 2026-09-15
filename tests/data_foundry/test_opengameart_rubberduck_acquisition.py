from __future__ import annotations

import ast
import json
from pathlib import Path
import unittest

from scripts import materialize_opengameart_rubberduck_cc0 as materializer
from scripts.materialize_opengameart_rubberduck_cc0 import (
    CONFIG,
    canonical_page_evidence_ok,
    raw_transport_url,
    validate_config,
)


class OpenGameArtRubberduckAcquisitionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = json.loads(Path(CONFIG).read_text(encoding="utf-8"))

    def test_current_config_is_fail_closed_and_valid(self) -> None:
        validate_config(self.config)
        self.assertEqual(self.config["declared_license"], "CC0")
        self.assertTrue(self.config["governance"]["platform_is_not_source_family"])
        self.assertTrue(self.config["governance"]["mirror_is_not_source_family"])

    def test_only_explicit_glass_breaking_rows_are_positive_candidates(self) -> None:
        positives = [row for row in self.config["assets"] if row["role"] == "positive_candidate"]
        self.assertEqual(len(positives), 6)
        self.assertTrue(all(row["target"] == "GLASS_SHATTER" for row in positives))
        self.assertTrue(all("glass_breaking" in row["path"] for row in positives))
        self.assertEqual({row["recording_family"] for row in positives}, {"bfh1:glass_breaking"})

    def test_confuser_pool_is_large_but_grouping_is_conservative(self) -> None:
        negatives = [row for row in self.config["assets"] if row["role"] == "hard_negative_candidate"]
        groups = {row["recording_family"] for row in negatives}
        self.assertGreaterEqual(len(negatives), 20)
        self.assertGreaterEqual(len(groups), 10)
        self.assertLess(len(groups), len(negatives))
        self.assertTrue(all(row["confuses"] == ["GLASS_SHATTER"] for row in negatives))

    def test_transport_url_is_exact_commit_not_moving_main(self) -> None:
        url = raw_transport_url(self.config, "bfh1_glass_breaking_01.ogg")
        commit = self.config["acquisition_transport"]["commit"]
        self.assertIn(commit, url)
        self.assertNotIn("/main/", url)

    def test_canonical_page_requires_creator_cc0_and_authorship_claim(self) -> None:
        html = """
        <html><body>
        <div>Author: rubberduck</div>
        <div>License(s): CC0</div>
        <p>i made 75 breaking, falling and hit sounds</p>
        </body></html>
        """
        ok, missing = canonical_page_evidence_ok(html, self.config)
        self.assertTrue(ok)
        self.assertEqual(missing, [])

    def test_missing_rights_marker_fails_closed(self) -> None:
        html = "<html><body>rubberduck - i made 75 breaking, falling and hit sounds</body></html>"
        ok, missing = canonical_page_evidence_ok(html, self.config)
        self.assertFalse(ok)
        self.assertIn("CC0_MARKER_MISSING", missing)

    def test_filename_cannot_sneak_non_glass_positive_into_config(self) -> None:
        mutated = json.loads(json.dumps(self.config))
        mutated["assets"][0]["path"] = "bfh1_rock_breaking_01.ogg"
        with self.assertRaises(ValueError):
            validate_config(mutated)

    def test_materializer_contains_no_json_literals_as_python_names(self) -> None:
        source = Path(materializer.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        invalid = sorted(
            {
                node.id
                for node in ast.walk(tree)
                if isinstance(node, ast.Name) and node.id in {"false", "true", "null"}
            }
        )
        self.assertEqual(invalid, [])


if __name__ == "__main__":
    unittest.main()

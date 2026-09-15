from __future__ import annotations

import ast
import io
import json
from pathlib import Path
import unittest
import zipfile

from scripts import materialize_opengameart_glass_expansion as materializer
from scripts.materialize_opengameart_glass_expansion import CONFIG, safe_glass_members, validate_config


class OpenGameArtGlassExpansionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = json.loads(Path(CONFIG).read_text(encoding="utf-8"))

    @staticmethod
    def archive_bytes(glass_count: int = 5, *, unsafe: bool = False) -> bytes:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for index in range(glass_count):
                archive.writestr(f"pack/glass_{index + 1:02d}.wav", b"RIFF-placeholder")
            archive.writestr("pack/metal_01.wav", b"RIFF-placeholder")
            archive.writestr("pack/readme.txt", b"metadata")
            if unsafe:
                archive.writestr("../glass_escape.wav", b"RIFF-placeholder")
        return buffer.getvalue()

    def test_current_config_is_discovery_only(self) -> None:
        validate_config(self.config)
        self.assertEqual(self.config["phase"], "EVIDENCE_DISCOVERY_ONLY")
        self.assertEqual(self.config["target"], "GLASS_SHATTER")
        self.assertEqual(len(self.config["sources"]), 3)

    def test_distinct_creator_does_not_reuse_rubberduck_family(self) -> None:
        sources = {row["source_id"]: row for row in self.config["sources"]}
        till = sources["echo-opengameart-till-behrend-glass-v1"]
        rubberduck = [row for row in self.config["sources"] if row["creator"] == "rubberduck"]
        self.assertEqual(till["underlying_source_family_candidate"], "OPENGAMEART_TILL_BEHREND")
        self.assertTrue(all(row["underlying_source_family_candidate"] == "OPENGAMEART_RUBBERDUCK" for row in rubberduck))
        self.assertNotEqual(till["underlying_source_family_candidate"], rubberduck[0]["underlying_source_family_candidate"])

    def test_only_till_direct_row_is_explicit_positive_candidate(self) -> None:
        direct = [row for row in self.config["sources"] if row["kind"] == "direct_audio"]
        archives = [row for row in self.config["sources"] if row["kind"] == "zip_glass_discovery"]
        self.assertEqual(len(direct), 1)
        self.assertEqual(direct[0]["semantic_candidate"], "glass_shatter")
        self.assertEqual(direct[0]["expected_filename"], "glass_breaking.wav")
        self.assertEqual(len(archives), 2)
        for row in archives:
            governance = row["governance"]
            self.assertTrue(governance["glass_named_files_are_review_candidates_only"])
            self.assertTrue(governance["filename_glass_alone_does_not_prove_break_or_shatter"])
            self.assertTrue(governance["recording_group_credit_forbidden_in_discovery"])

    def test_safe_archive_selects_only_glass_named_audio(self) -> None:
        selected, audio_count, uncompressed = safe_glass_members(self.archive_bytes(5), 5)
        self.assertEqual(len(selected), 5)
        self.assertEqual(audio_count, 6)
        self.assertGreater(uncompressed, 0)
        self.assertTrue(all("glass" in info.filename.casefold() for info in selected))

    def test_archive_floor_and_path_traversal_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            safe_glass_members(self.archive_bytes(4), 5)
        with self.assertRaises(ValueError):
            safe_glass_members(self.archive_bytes(5, unsafe=True), 5)

    def test_rubberduck_archives_cannot_claim_separate_source_families(self) -> None:
        mutated = json.loads(json.dumps(self.config))
        rubberduck = [row for row in mutated["sources"] if row["creator"] == "rubberduck"]
        rubberduck[1]["underlying_source_family_candidate"] = "OPENGAMEART_RUBBERDUCK_SECOND_PACK"
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

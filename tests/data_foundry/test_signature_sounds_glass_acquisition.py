from __future__ import annotations

import ast
import io
import json
from pathlib import Path
import unittest
import zipfile

from scripts import materialize_signature_sounds_glass_cc0 as materializer
from scripts.materialize_signature_sounds_glass_cc0 import (
    CONFIG,
    canonical_page_evidence_ok,
    direct_mediafire_download_url,
    safe_audio_members,
    validate_config,
)


class SignatureSoundsGlassAcquisitionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = json.loads(Path(CONFIG).read_text(encoding="utf-8"))

    @staticmethod
    def archive_bytes(count: int = 40, *, unsafe: bool = False) -> bytes:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for index in range(count):
                name = f"Glass Smash One Shots/glass_{index + 1:02d}.wav"
                archive.writestr(name, b"RIFF-test-wav-placeholder")
            archive.writestr("Glass Smash One Shots/readme.txt", b"metadata")
            if unsafe:
                archive.writestr("../escape.wav", b"RIFF-unsafe")
        return buffer.getvalue()

    def test_current_config_is_discovery_only_and_fail_closed(self) -> None:
        validate_config(self.config)
        self.assertEqual(self.config["declared_license"], "CC0")
        self.assertEqual(self.config["target"], "GLASS_SHATTER")
        self.assertEqual(self.config["underlying_source_family_candidate"], "SIGNATURE_SOUNDS")
        self.assertEqual(self.config["governance"]["phase"], "EVIDENCE_DISCOVERY_ONLY")
        self.assertIsNone(self.config["acquisition_transport"]["expected_archive_sha256"])
        self.assertFalse(self.config["acquisition_transport"]["source_credit"])
        self.assertTrue(self.config["governance"]["corpus_admission_forbidden_until_archive_sha256_is_pinned"])

    def test_source_page_requires_pack_cc0_count_recorded_and_wav_markers(self) -> None:
        html = """
        <html><body>
        <h1>Smashed Glass One-Shots Sample Pack (CC0)</h1>
        <p>Royalty-Free (CC0)</p>
        <p>40+ smashed glass one-shots</p>
        <p>Recorded with high-quality equipment</p>
        <p>High-quality WAV format</p>
        </body></html>
        """
        ok, missing = canonical_page_evidence_ok(html)
        self.assertTrue(ok)
        self.assertEqual(missing, [])

    def test_missing_cc0_marker_fails_closed(self) -> None:
        html = "40+ smashed glass one-shots recorded with high-quality equipment in high-quality WAV format"
        ok, missing = canonical_page_evidence_ok(html)
        self.assertFalse(ok)
        self.assertIn("CC0_MARKER_MISSING", missing)

    def test_mediafire_transport_parser_requires_direct_zip(self) -> None:
        html = '<a href="https://download123.mediafire.com/token/file/Glass%2BSmash%2BOne%2BShots.zip">Download</a>'
        url = direct_mediafire_download_url(html)
        self.assertIn("download123.mediafire.com", url)
        self.assertIn(".zip", url)
        with self.assertRaises(ValueError):
            direct_mediafire_download_url('<a href="https://www.mediafire.com/file/x/file">landing only</a>')

    def test_archive_floor_and_conservative_pack_shape(self) -> None:
        audio, ignored, total = safe_audio_members(self.archive_bytes(40), 40)
        self.assertEqual(len(audio), 40)
        self.assertEqual(len(ignored), 1)
        self.assertGreater(total, 0)
        with self.assertRaises(ValueError):
            safe_audio_members(self.archive_bytes(39), 40)

    def test_archive_path_traversal_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            safe_audio_members(self.archive_bytes(40, unsafe=True), 40)

    def test_transport_cannot_receive_source_credit(self) -> None:
        mutated = json.loads(json.dumps(self.config))
        mutated["acquisition_transport"]["source_credit"] = True
        with self.assertRaises(ValueError):
            validate_config(mutated)

    def test_audio_floor_cannot_be_weakened(self) -> None:
        mutated = json.loads(json.dumps(self.config))
        mutated["governance"]["minimum_audio_entries"] = 39
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

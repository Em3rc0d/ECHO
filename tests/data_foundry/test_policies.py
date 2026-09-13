from __future__ import annotations

import unittest

from echo.data_foundry.contracts import UseDecision
from echo.data_foundry.policies import classify_license, normalize_license_id


class LicensePolicyTests(unittest.TestCase):
    def test_permissive_by_is_release_safe(self) -> None:
        self.assertEqual(classify_license("CC BY 4.0"), UseDecision.ALLOW_RELEASE_SAFE)

    def test_noncommercial_is_not_release_safe(self) -> None:
        self.assertEqual(classify_license("CC-BY-NC-3.0"), UseDecision.RESEARCH_ONLY)
        self.assertEqual(
            classify_license("CC-BY-NC-3.0", profile="research_extended"),
            UseDecision.ALLOW_RESEARCH_ONLY,
        )

    def test_sharealike_requires_release_review(self) -> None:
        self.assertEqual(classify_license("CC BY-SA 4.0"), UseDecision.REVIEW_REQUIRED)

    def test_unknown_fails_closed(self) -> None:
        self.assertEqual(classify_license("mystery-license"), UseDecision.QUARANTINE)
        self.assertEqual(classify_license(None), UseDecision.QUARANTINE)

    def test_alias_normalization(self) -> None:
        self.assertEqual(normalize_license_id("cc by 4.0"), "CC-BY-4.0")


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

from pathlib import Path
import unittest


WORKFLOW = Path(".github/workflows/mk1-freesound-cc0-free-materialization.yml")


class FreesoundCc0PersistenceContractTests(unittest.TestCase):
    def test_writer_is_bound_to_trigger_sha_and_never_rebases(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("ref: ${{ github.sha }}", text)
        self.assertIn('RUN_SHA="${GITHUB_SHA}"', text)
        self.assertIn('git reset --hard "$RUN_SHA"', text)
        self.assertNotIn("git pull --rebase", text)

    def test_descendant_persistence_requires_identical_inputs(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("git fetch origin main --depth=50", text)
        self.assertIn('git merge-base --is-ancestor "$RUN_SHA" "$REMOTE_MAIN_SHA"', text)
        self.assertIn("Freesound CC0 materialization inputs changed", text)
        self.assertIn("INPUT_PATHS=(", text)
        for path in (
            "scripts/materialize_freesound_cc0_gap_assets.py",
            "scripts/data_foundry/enrich_freesound_cc0_fingerprints.py",
            "src/echo/data_foundry/canonical_fingerprints.py",
            "MK1/mining-site/materialization/freesound-gap-discovery.json",
            "configs/data_foundry/freesound_cc0_supplemental.v1.json",
            "configs/data_foundry/free_tier_boundary.v1.json",
            ".github/workflows/mk1-freesound-cc0-free-materialization.yml",
        ):
            self.assertIn(path, text)
        self.assertIn('git checkout --detach "$REMOTE_MAIN_SHA"', text)


if __name__ == "__main__":
    unittest.main()

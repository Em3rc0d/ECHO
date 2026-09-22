from __future__ import annotations

from pathlib import Path
import unittest


WORKFLOWS = (
    Path('.github/workflows/mk1-freesound-cc0-free-materialization.yml'),
    Path('.github/workflows/mk1-freesound-release-safe-materialization.yml'),
)

EXPECTED_INPUTS = {
    'mk1-freesound-cc0-free-materialization.yml': (
        'scripts/materialize_freesound_cc0_gap_assets.py',
        'scripts/data_foundry/enrich_freesound_cc0_fingerprints.py',
        'src/echo/data_foundry/canonical_fingerprints.py',
        'MK1/mining-site/materialization/freesound-gap-discovery.json',
        'configs/data_foundry/freesound_cc0_supplemental.v1.json',
        'configs/data_foundry/free_tier_boundary.v1.json',
        '.github/workflows/mk1-freesound-cc0-free-materialization.yml',
    ),
    'mk1-freesound-release-safe-materialization.yml': (
        'scripts/data_foundry/materialize_freesound_release_safe.py',
        'MK1/mining-site/materialization/fsd50k-exact-freesound-candidates.json',
        'MK1/mining-site/materialization/freesound-gap-discovery.json',
        'configs/data_foundry/freesound_cc0_supplemental.v1.json',
        'configs/data_foundry/free_tier_boundary.v1.json',
    ),
}


class FreesoundWorkflowPersistenceContractTests(unittest.TestCase):
    def test_both_workflows_are_bound_to_trigger_sha(self) -> None:
        for workflow in WORKFLOWS:
            with self.subTest(workflow=workflow.name):
                text = workflow.read_text(encoding='utf-8')
                self.assertIn('ref: ${{ github.sha }}', text)
                self.assertIn('RUN_SHA="${GITHUB_SHA}"', text)
                self.assertIn('git reset --hard "$RUN_SHA"', text)

    def test_generated_evidence_is_never_rebased(self) -> None:
        for workflow in WORKFLOWS:
            with self.subTest(workflow=workflow.name):
                text = workflow.read_text(encoding='utf-8')
                self.assertNotIn('git pull --rebase', text)
                self.assertNotIn('git pull --rebase --autostash', text)

    def test_descendant_safe_persistence_fails_closed_on_input_drift(self) -> None:
        for workflow in WORKFLOWS:
            with self.subTest(workflow=workflow.name):
                text = workflow.read_text(encoding='utf-8')
                self.assertIn('git fetch origin main --depth=50', text)
                self.assertIn('REMOTE_MAIN_SHA="$(git rev-parse origin/main)"', text)
                self.assertIn('if [[ "$RUN_SHA" != "$REMOTE_MAIN_SHA" ]]; then', text)
                self.assertIn('git merge-base --is-ancestor "$RUN_SHA" "$REMOTE_MAIN_SHA"', text)
                self.assertIn('INPUT_PATHS=(', text)
                self.assertIn('git diff --quiet "$RUN_SHA" "$REMOTE_MAIN_SHA"', text)
                self.assertIn('refusing stale evidence', text)
                self.assertIn('git checkout --detach "$REMOTE_MAIN_SHA"', text)
                for path in EXPECTED_INPUTS[workflow.name]:
                    self.assertIn(path, text)

    def test_descendant_safe_mode_never_creates_second_source_authority(self) -> None:
        for workflow in WORKFLOWS:
            with self.subTest(workflow=workflow.name):
                text = workflow.read_text(encoding='utf-8')
                self.assertIn('git push origin HEAD:main', text)
                self.assertNotIn('git merge origin/main', text)
                self.assertNotIn('git cherry-pick', text)


if __name__ == '__main__':
    unittest.main()

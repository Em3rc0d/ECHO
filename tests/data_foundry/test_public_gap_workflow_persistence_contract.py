from __future__ import annotations

from pathlib import Path
import unittest

from scripts.materialize_public_gap_assets import license_marker_ok


WORKFLOW = Path('.github/workflows/mk1-public-gap-materialization.yml')


class PublicGapWorkflowPersistenceContractTests(unittest.TestCase):
    def test_materialization_is_bound_to_trigger_sha(self) -> None:
        text = WORKFLOW.read_text(encoding='utf-8')
        self.assertIn('ref: ${{ github.sha }}', text)
        self.assertIn('git reset --hard "${GITHUB_SHA}"', text)

    def test_generated_evidence_is_never_rebased_before_commit(self) -> None:
        text = WORKFLOW.read_text(encoding='utf-8')
        self.assertNotIn('git pull --rebase', text)
        self.assertNotIn('git pull --rebase --autostash', text)

    def test_persistence_fails_closed_if_main_moved(self) -> None:
        text = WORKFLOW.read_text(encoding='utf-8')
        self.assertIn('git fetch origin main', text)
        self.assertIn('RUN_SHA="$(git rev-parse HEAD)"', text)
        self.assertIn('REMOTE_MAIN_SHA="$(git rev-parse origin/main)"', text)
        self.assertIn('if [[ "$RUN_SHA" != "$REMOTE_MAIN_SHA" ]]; then', text)
        self.assertIn('refusing to persist stale evidence', text)

    def test_wikimedia_cc_by_4_license_marker_is_release_safe(self) -> None:
        page = 'This file is licensed under the Creative Commons Attribution 4.0 International license. CC BY 4.0.'
        self.assertTrue(license_marker_ok('echo-wikimedia-fire-alarm-v1', 'CC-BY-4.0', page))

    def test_sharealike_does_not_pass_as_attribution_only(self) -> None:
        page = 'Creative Commons Attribution-ShareAlike 4.0 International'
        self.assertFalse(license_marker_ok('echo-wikimedia-fire-alarm-v1', 'CC-BY-4.0', page))


if __name__ == '__main__':
    unittest.main()

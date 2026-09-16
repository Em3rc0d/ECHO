from __future__ import annotations

from pathlib import Path
import unittest


WORKFLOWS = (
    Path('.github/workflows/mk1-freesound-cc0-free-materialization.yml'),
    Path('.github/workflows/mk1-freesound-release-safe-materialization.yml'),
)


class FreesoundWorkflowPersistenceContractTests(unittest.TestCase):
    def test_both_workflows_are_bound_to_trigger_sha(self) -> None:
        for workflow in WORKFLOWS:
            with self.subTest(workflow=workflow.name):
                text = workflow.read_text(encoding='utf-8')
                self.assertIn('ref: ${{ github.sha }}', text)
                self.assertIn('git reset --hard "${GITHUB_SHA}"', text)

    def test_generated_evidence_is_never_rebased(self) -> None:
        for workflow in WORKFLOWS:
            with self.subTest(workflow=workflow.name):
                text = workflow.read_text(encoding='utf-8')
                self.assertNotIn('git pull --rebase', text)
                self.assertNotIn('git pull --rebase --autostash', text)

    def test_both_workflows_fail_closed_when_main_moves(self) -> None:
        for workflow in WORKFLOWS:
            with self.subTest(workflow=workflow.name):
                text = workflow.read_text(encoding='utf-8')
                self.assertIn('git fetch origin main', text)
                self.assertIn('RUN_SHA="$(git rev-parse HEAD)"', text)
                self.assertIn('REMOTE_MAIN_SHA="$(git rev-parse origin/main)"', text)
                self.assertIn('if [[ "$RUN_SHA" != "$REMOTE_MAIN_SHA" ]]; then', text)
                self.assertIn('refusing to persist stale evidence', text)


if __name__ == '__main__':
    unittest.main()

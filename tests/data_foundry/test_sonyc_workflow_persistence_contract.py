from __future__ import annotations

from pathlib import Path
import unittest


WORKFLOW = Path('.github/workflows/mk1-sonyc-free-materialization.yml')


class SonycWorkflowPersistenceContractTests(unittest.TestCase):
    def test_materialization_and_merge_are_bound_to_trigger_sha(self) -> None:
        text = WORKFLOW.read_text(encoding='utf-8')
        self.assertGreaterEqual(text.count('ref: ${{ github.sha }}'), 2)

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


if __name__ == '__main__':
    unittest.main()

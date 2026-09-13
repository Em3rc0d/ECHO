from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from echo.data_foundry.source_policy import (
    assert_sources_allowed,
    load_dataset_certification,
    source_profile_state,
)


class DatasetSourcePolicyTests(unittest.TestCase):
    def test_real_policy_loads(self) -> None:
        policy = load_dataset_certification("configs/data_foundry/dataset_certification.v1.json")
        self.assertEqual(
            source_profile_state(policy, source_id="sonyc-ust-v2", profile="release_safe"),
            "ALLOW",
        )
        self.assertEqual(
            source_profile_state(policy, source_id="fsd50k-1.0", profile="release_safe"),
            "CONDITIONAL",
        )
        self.assertEqual(
            source_profile_state(policy, source_id="esc50", profile="research_extended"),
            "ALLOW",
        )

    def test_unknown_source_fails_closed(self) -> None:
        policy = {
            "schema_version": "echo.dataset-certification.v1",
            "sources": {"known": {"profiles": {"release_safe": "ALLOW"}}},
        }
        self.assertEqual(
            source_profile_state(policy, source_id="unknown", profile="release_safe"),
            "DENY",
        )

    def test_conditional_source_stops_release_safe_freeze(self) -> None:
        policy = load_dataset_certification("configs/data_foundry/dataset_certification.v1.json")
        with self.assertRaises(ValueError):
            assert_sources_allowed(
                ["sonyc-ust-v2", "fsd50k-1.0"],
                profile="release_safe",
                policy=policy,
            )

    def test_research_extended_allows_declared_research_sources(self) -> None:
        policy = load_dataset_certification("configs/data_foundry/dataset_certification.v1.json")
        assert_sources_allowed(
            ["sonyc-ust-v2", "fsd50k-1.0", "singapura-v1.0a", "esc50", "urbansound8k-1.0"],
            profile="research_extended",
            policy=policy,
        )


if __name__ == "__main__":
    unittest.main()

"""Contract tests for the v2-candidate external demo decision layer.

No weights, camera, MQTT, or assets are required. Importing the actual demo
module also checks that its public policy symbols remain importable.
"""
import unittest

from demo.server import external_abstention_decision, summarize_score_trace
from echo.runtime.event_engine import ThresholdConfig


class DemoSignalAwareDecisionTests(unittest.TestCase):
    def decide(self, quality, events=None, labels=None):
        return external_abstention_decision(
            candidate_events=events or [],
            candidate_labels=labels or [],
            score_diagnostics=None,
            signal_quality_state=quality,
        )

    def assert_abstains(self, decision):
        self.assertEqual(decision["version"], "ECHO-DEMO-ABSTENTION-v2-candidate")
        self.assertFalse(decision["publish_target_event"])
        self.assertIsNone(decision["accepted_target"])

    def test_no_signal_is_not_no_target(self):
        result = self.decide("NO_SIGNAL")
        self.assertEqual(result["state"], "NO_SIGNAL")
        self.assertEqual(result["ood_status"], "SIGNAL_NOT_ANALYZABLE")
        self.assert_abstains(result)

    def test_invalid_signal_is_not_no_target(self):
        result = self.decide("INVALID_SIGNAL")
        self.assertEqual(result["state"], "INVALID_SIGNAL")
        self.assert_abstains(result)

    def test_partial_signal_without_candidate_never_claims_complete_no_target(self):
        result = self.decide("PARTIAL_SIGNAL")
        self.assertEqual(result["state"], "INCOMPLETE_SIGNAL")
        self.assertEqual(result["candidate_event_count"], 0)
        self.assert_abstains(result)

    def test_partial_signal_with_candidate_remains_unknown(self):
        events = [{
            "event_type": "SIREN",
            "confidence_peak": 0.9,
            "confidence_mean": 0.8,
        }]
        result = self.decide("PARTIAL_SIGNAL", events, ["SIREN"])
        self.assertEqual(result["state"], "UNKNOWN")
        self.assertEqual(result["candidate_labels"], ["SIREN"])
        self.assert_abstains(result)

    def test_nonzero_with_no_candidate_preserves_no_target(self):
        result = self.decide("UNASSESSED_NONZERO")
        self.assertEqual(result["state"], "NO_TARGET")
        self.assert_abstains(result)

    def test_nonzero_with_candidate_preserves_unknown(self):
        events = [{
            "event_type": "GLASS_SHATTER",
            "confidence_peak": 0.562,
            "confidence_mean": 0.562,
        }]
        result = self.decide("UNASSESSED_NONZERO", events, ["GLASS_SHATTER"])
        self.assertEqual(result["state"], "UNKNOWN")
        self.assertEqual(result["top_candidate"]["event_type"], "GLASS_SHATTER")
        self.assert_abstains(result)

    def test_zero_scored_windows_do_not_fabricate_zero_probability_scores(self):
        thresholds = {
            "GLASS_SHATTER": ThresholdConfig(0.35, 0.15, 3, 1),
        }
        trace = summarize_score_trace([], thresholds)
        self.assertEqual(trace["window_count"], 0)
        self.assertEqual(trace["labels"], {})
        self.assertEqual(trace["ranked_labels"], [])
        self.assertEqual(trace["diagnostic_kind"], "NO_INFERENCE")
        self.assertFalse(trace["raw_audio_retained"])


if __name__ == "__main__":
    unittest.main()

from datetime import datetime, timedelta, timezone
import unittest

from echo.runtime.event_engine import RawInference, TemporalEventEngine, ThresholdConfig


BASE = datetime(2026, 9, 24, 12, 0, tzinfo=timezone.utc)


def inference(i, score, *, source="cam-1", session="s1"):
    start = BASE + timedelta(seconds=i)
    return RawInference(
        source_id=source,
        site_id="site-1",
        stream_session_id=session,
        window_start_utc=start,
        window_end_utc=start + timedelta(seconds=1),
        scores={"SIREN": score},
        model_version="mvp-test",
    )


class EventEngineTest(unittest.TestCase):
    def engine(self, cooldown=2.0):
        return TemporalEventEngine(
            thresholds={
                "SIREN": ThresholdConfig(
                    on_threshold=0.8,
                    off_threshold=0.4,
                    confirm_windows=2,
                    release_windows=2,
                    cooldown_seconds=cooldown,
                )
            },
            threshold_version="test-v1",
        )

    def test_confirms_closes_and_preserves_event_id(self):
        engine = self.engine()
        self.assertEqual(engine.ingest(inference(0, 0.9)), [])
        opened = engine.ingest(inference(1, 0.85))
        self.assertEqual(len(opened), 1)
        self.assertEqual(opened[0].lifecycle, "CONFIRMED")
        self.assertIsNone(opened[0].end_utc)

        self.assertEqual(engine.ingest(inference(2, 0.5)), [])
        self.assertEqual(engine.ingest(inference(3, 0.2)), [])
        closed = engine.ingest(inference(4, 0.1))
        self.assertEqual(len(closed), 1)
        self.assertEqual(closed[0].lifecycle, "CLOSED")
        self.assertEqual(closed[0].event_id, opened[0].event_id)
        self.assertIsNotNone(closed[0].end_utc)

    def test_cooldown_blocks_immediate_retrigger(self):
        engine = self.engine(cooldown=3)
        engine.ingest(inference(0, 0.9))
        engine.ingest(inference(1, 0.9))
        engine.ingest(inference(2, 0.1))
        engine.ingest(inference(3, 0.1))
        self.assertEqual(engine.ingest(inference(4, 0.99)), [])
        self.assertEqual(engine.ingest(inference(5, 0.99)), [])
        self.assertEqual(engine.ingest(inference(6, 0.99)), [])
        self.assertEqual(engine.ingest(inference(7, 0.99)), [])
        opened = engine.ingest(inference(8, 0.99))
        self.assertEqual(len(opened), 1)

    def test_sources_are_isolated(self):
        engine = self.engine()
        self.assertEqual(engine.ingest(inference(0, 0.9, source="a")), [])
        self.assertEqual(engine.ingest(inference(0, 0.9, source="b")), [])
        a = engine.ingest(inference(1, 0.9, source="a"))
        b = engine.ingest(inference(1, 0.9, source="b"))
        self.assertEqual(len(a), 1)
        self.assertEqual(len(b), 1)
        self.assertNotEqual(a[0].event_id, b[0].event_id)

    def test_sessions_are_isolated(self):
        engine = self.engine()
        self.assertEqual(engine.ingest(inference(0, 0.9, session="old")), [])
        self.assertEqual(engine.ingest(inference(1, 0.9, session="new")), [])
        opened = engine.ingest(inference(2, 0.9, session="new"))
        self.assertEqual(len(opened), 1)

    def test_close_session_flushes_active_event(self):
        engine = self.engine()
        engine.ingest(inference(0, 0.9))
        opened = engine.ingest(inference(1, 0.9))[0]

        closed = engine.close_session(
            source_id="cam-1",
            site_id="site-1",
            stream_session_id="s1",
            end_utc=BASE + timedelta(seconds=2),
            model_version="mvp-test",
        )
        self.assertEqual(len(closed), 1)
        self.assertEqual(closed[0].lifecycle, "CLOSED")
        self.assertEqual(closed[0].event_id, opened.event_id)
        self.assertEqual(
            engine.close_session(
                source_id="cam-1",
                site_id="site-1",
                stream_session_id="s1",
                end_utc=BASE + timedelta(seconds=3),
                model_version="mvp-test",
            ),
            [],
        )

    def test_event_serialization_matches_event_schema_shape(self):
        engine = self.engine()
        engine.ingest(inference(0, 0.9))
        event = engine.ingest(inference(1, 0.9))[0].to_dict()
        self.assertEqual(event["schema_version"], "echo.event.v1")
        self.assertEqual(event["event_type"], "SIREN")
        self.assertEqual(event["source_id"], "cam-1")
        self.assertEqual(event["confidence"]["peak"], 0.9)
        self.assertGreater(event["confidence"]["mean"], 0)


if __name__ == "__main__":
    unittest.main()

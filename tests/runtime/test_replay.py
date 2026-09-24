import unittest

from echo.runtime.replay import iter_replay_windows


class ReplayWindowTest(unittest.TestCase):
    def test_overlapping_windows(self):
        windows = list(
            iter_replay_windows(
                list(range(10)),
                sample_rate_hz=2,
                window_seconds=2.0,
                hop_seconds=1.0,
                pad_final=False,
            )
        )
        self.assertEqual(len(windows), 4)
        self.assertEqual(windows[0].waveform, (0.0, 1.0, 2.0, 3.0))
        self.assertEqual(windows[1].waveform, (2.0, 3.0, 4.0, 5.0))
        self.assertEqual(windows[-1].waveform, (6.0, 7.0, 8.0, 9.0))

    def test_optional_final_padding(self):
        windows = list(
            iter_replay_windows(
                [1.0, 2.0, 3.0],
                sample_rate_hz=2,
                window_seconds=2.0,
                hop_seconds=1.0,
                pad_final=True,
            )
        )
        self.assertEqual(windows[0].waveform, (1.0, 2.0, 3.0, 0.0))
        self.assertEqual(windows[1].waveform, (3.0, 0.0, 0.0, 0.0))


if __name__ == "__main__":
    unittest.main()

import unittest

from echo.modeling.metrics import evaluate_binary, tune_threshold


class MetricsTest(unittest.TestCase):
    def test_binary_metrics(self):
        row = evaluate_binary(
            [0.9, 0.8, 0.2, 0.1],
            [1, 0, 0, 1],
            threshold=0.5,
        )
        self.assertEqual((row.tp, row.fp, row.tn, row.fn), (1, 1, 1, 1))
        self.assertEqual(row.precision, 0.5)
        self.assertEqual(row.recall, 0.5)
        self.assertEqual(row.f1, 0.5)

    def test_threshold_tuning_is_deterministic(self):
        row = tune_threshold(
            [0.95, 0.8, 0.7, 0.2, 0.1],
            [1, 1, 0, 0, 0],
            candidates=[0.5, 0.75, 0.9],
        )
        self.assertEqual(row.threshold, 0.75)
        self.assertEqual(row.f1, 1.0)


if __name__ == "__main__":
    unittest.main()

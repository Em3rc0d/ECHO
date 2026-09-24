import unittest

try:
    import torch
except ImportError:
    torch = None

from echo.modeling.compact_cnn import build_compact_cnn


@unittest.skipIf(torch is None, "torch optional dependency not installed")
class CompactCnnTest(unittest.TestCase):
    def test_forward_shape_and_finite_output(self):
        model = build_compact_cnn(num_targets=3)
        waveform = torch.randn(2, 16000)
        logits = model(waveform)
        self.assertEqual(tuple(logits.shape), (2, 3))
        self.assertTrue(bool(torch.isfinite(logits).all()))


if __name__ == "__main__":
    unittest.main()

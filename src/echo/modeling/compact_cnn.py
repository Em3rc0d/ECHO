"""Compact ECHO log-mel CNN baseline for Benchmark C."""

from __future__ import annotations

import math


def _require_torch():
    try:
        import torch
        import torch.nn as nn
    except ImportError as exc:
        raise RuntimeError(
            "Compact CNN requires torch; install the 'mvp' optional dependencies"
        ) from exc
    return torch, nn


def _hz_to_mel(value: float) -> float:
    return 2595.0 * math.log10(1.0 + value / 700.0)


def _mel_to_hz(value: float) -> float:
    return 700.0 * (10.0 ** (value / 2595.0) - 1.0)


def mel_filterbank(
    *,
    sample_rate_hz: int,
    n_fft: int,
    n_mels: int,
    f_min: float,
    f_max: float,
):
    torch, _nn = _require_torch()
    if not 0.0 <= f_min < f_max <= sample_rate_hz / 2:
        raise ValueError("invalid mel frequency bounds")

    mel_min = _hz_to_mel(f_min)
    mel_max = _hz_to_mel(f_max)
    mel_points = [
        mel_min + (mel_max - mel_min) * i / (n_mels + 1)
        for i in range(n_mels + 2)
    ]
    hz_points = [_mel_to_hz(value) for value in mel_points]
    bins = [
        int(math.floor((n_fft + 1) * hz / sample_rate_hz))
        for hz in hz_points
    ]

    freq_bins = n_fft // 2 + 1
    fb = torch.zeros((n_mels, freq_bins), dtype=torch.float32)
    for m in range(1, n_mels + 1):
        left = max(0, min(freq_bins - 1, bins[m - 1]))
        center = max(left + 1, min(freq_bins - 1, bins[m]))
        right = max(center + 1, min(freq_bins, bins[m + 1]))

        for k in range(left, center):
            fb[m - 1, k] = (k - left) / max(1, center - left)
        for k in range(center, right):
            fb[m - 1, k] = (right - k) / max(1, right - center)
    return fb


def build_compact_cnn(
    *,
    num_targets: int,
    sample_rate_hz: int = 16000,
    n_fft: int = 512,
    win_length: int = 400,
    hop_length: int = 160,
    n_mels: int = 64,
    f_min: float = 50.0,
    f_max: float = 8000.0,
):
    torch, nn = _require_torch()

    class LogMelFrontend(nn.Module):
        def __init__(self):
            super().__init__()
            self.n_fft = n_fft
            self.win_length = win_length
            self.hop_length = hop_length
            self.register_buffer(
                "window",
                torch.hann_window(win_length, periodic=True),
                persistent=False,
            )
            self.register_buffer(
                "mel_filter",
                mel_filterbank(
                    sample_rate_hz=sample_rate_hz,
                    n_fft=n_fft,
                    n_mels=n_mels,
                    f_min=f_min,
                    f_max=f_max,
                ),
                persistent=True,
            )

        def forward(self, waveform):
            spectrum = torch.stft(
                waveform,
                n_fft=self.n_fft,
                hop_length=self.hop_length,
                win_length=self.win_length,
                window=self.window,
                center=True,
                return_complex=True,
            )
            power = spectrum.abs().pow(2.0)
            mel = torch.einsum("mf,bft->bmt", self.mel_filter, power)
            log_mel = torch.log(mel.clamp_min(1e-6))
            mean = log_mel.mean(dim=(1, 2), keepdim=True)
            std = log_mel.std(dim=(1, 2), keepdim=True).clamp_min(1e-5)
            return (log_mel - mean) / std

    class CompactLogMelCnn(nn.Module):
        def __init__(self):
            super().__init__()
            self.frontend = LogMelFrontend()
            self.encoder = nn.Sequential(
                nn.Conv2d(1, 16, kernel_size=3, padding=1, bias=False),
                nn.BatchNorm2d(16),
                nn.ReLU(),
                nn.MaxPool2d(2),
                nn.Conv2d(16, 32, kernel_size=3, padding=1, bias=False),
                nn.BatchNorm2d(32),
                nn.ReLU(),
                nn.MaxPool2d(2),
                nn.Conv2d(32, 64, kernel_size=3, padding=1, bias=False),
                nn.BatchNorm2d(64),
                nn.ReLU(),
                nn.MaxPool2d(2),
                nn.Conv2d(64, 96, kernel_size=3, padding=1, bias=False),
                nn.BatchNorm2d(96),
                nn.ReLU(),
                nn.AdaptiveAvgPool2d((1, 1)),
            )
            self.head = nn.Linear(96, num_targets)

        def forward(self, waveform):
            features = self.frontend(waveform).unsqueeze(1)
            encoded = self.encoder(features).flatten(1)
            return self.head(encoded)

    return CompactLogMelCnn()

"""Deterministic fixed-window replay primitives."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Sequence


@dataclass(frozen=True)
class ReplayWindow:
    index: int
    start_sample: int
    end_sample: int
    waveform: tuple[float, ...]


def iter_replay_windows(
    waveform: Sequence[float],
    *,
    sample_rate_hz: int,
    window_seconds: float,
    hop_seconds: float,
    pad_final: bool = False,
) -> Iterator[ReplayWindow]:
    if sample_rate_hz <= 0:
        raise ValueError("sample_rate_hz must be positive")
    if window_seconds <= 0 or hop_seconds <= 0:
        raise ValueError("window_seconds and hop_seconds must be positive")

    window = int(round(window_seconds * sample_rate_hz))
    hop = int(round(hop_seconds * sample_rate_hz))
    if window <= 0 or hop <= 0:
        raise ValueError("window/hop rounded to zero samples")

    total = len(waveform)
    index = 0
    start = 0
    while start < total:
        end = start + window
        if end > total and not pad_final:
            break
        values = list(float(v) for v in waveform[start:min(end, total)])
        if end > total:
            values.extend([0.0] * (end - total))
        yield ReplayWindow(
            index=index,
            start_sample=start,
            end_sample=end,
            waveform=tuple(values),
        )
        index += 1
        start += hop

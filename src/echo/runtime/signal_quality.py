"""Deterministic, pre-inference PCM validity boundary for ECHO-MVP-001.

Only exact digital zero, empty PCM and nonfinite samples are classified here.
A finite nonzero window is NOT evidence of usable field audio: low-level,
frozen, muted, clipped and noisy device streams require separate calibration.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence


@dataclass(frozen=True)
class SignalInspection:
    state: str
    reason: str

    @property
    def analysis_allowed(self) -> bool:
        return self.state == "UNASSESSED_NONZERO"


def inspect_pcm_window(samples: Sequence[float]) -> SignalInspection:
    """Fail closed for unusable PCM without inventing an amplitude threshold.

    The check is per complete inference window. It prevents target scoring on
    exact digital silence (including signed zero) or malformed/nonfinite PCM.
    It does not claim near-silence/device signal quality is calibrated.
    """
    if len(samples) == 0:
        return SignalInspection("INVALID_SIGNAL", "EMPTY_PCM")

    has_nonzero = False
    for sample in samples:
        try:
            value = float(sample)
        except (TypeError, ValueError, OverflowError):
            return SignalInspection("INVALID_SIGNAL", "NONNUMERIC_PCM")
        if not isfinite(value):
            return SignalInspection("INVALID_SIGNAL", "NONFINITE_PCM")
        if value != 0.0:
            has_nonzero = True

    if not has_nonzero:
        return SignalInspection("NO_SIGNAL", "EXACT_DIGITAL_ZERO")
    return SignalInspection("UNASSESSED_NONZERO", "NONZERO_NOT_FIELD_CALIBRATED")

"""Runtime scorers for trained ECHO MVP benchmark artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from .backbones import PannsCnn14EmbeddingBackbone, YAMNetEmbeddingBackbone
from .compact_cnn import build_compact_cnn
from .embedding_head import build_embedding_head
from .manifest import MVP_TARGETS


def _require_stack():
    try:
        import numpy as np
        import torch
    except ImportError as exc:
        raise RuntimeError(
            "MVP inference requires numpy and torch; install the 'mvp' extra"
        ) from exc
    return np, torch


class EmbeddingHeadScorer:
    def __init__(
        self,
        *,
        checkpoint: str | Path,
        backbone: str,
        device: str = "cpu",
        yamnet_handle: str = "https://tfhub.dev/google/yamnet/1",
        panns_checkpoint: str | None = None,
    ) -> None:
        np, torch = _require_stack()
        payload = torch.load(Path(checkpoint), map_location=device)
        targets = tuple(payload.get("targets") or ())
        if targets != MVP_TARGETS:
            raise ValueError(f"checkpoint targets {targets} != {MVP_TARGETS}")

        if backbone == "yamnet":
            self.backbone = YAMNetEmbeddingBackbone(model_handle=yamnet_handle)
            expected_name = "YAMNET_EMBEDDINGS_HEAD"
        elif backbone == "panns":
            self.backbone = PannsCnn14EmbeddingBackbone(
                checkpoint_path=panns_checkpoint,
                device=device,
            )
            expected_name = "PANNS_CNN14_HEAD"
        else:
            raise ValueError(f"unsupported embedding backbone: {backbone}")

        if payload.get("backbone") != expected_name:
            raise ValueError(
                f"checkpoint backbone {payload.get('backbone')!r} != {expected_name!r}"
            )

        self.sample_rate_hz = self.backbone.sample_rate_hz
        self.model_version = str(Path(checkpoint))
        self.validation_thresholds = dict(payload.get("validation_thresholds") or {})
        self._device = device
        self._np = np
        self._torch = torch
        self._head = build_embedding_head(
            input_dim=int(payload["input_dim"]),
            hidden_dim=int(payload.get("hidden_dim", 256)),
            dropout=float(payload.get("dropout", 0.2)),
        ).to(device)
        self._head.load_state_dict(payload["state_dict"])
        self._head.eval()

    def score(self, waveform: Sequence[float]) -> dict[str, float]:
        vector = self._np.asarray(
            self.backbone.embed(waveform),
            dtype=self._np.float32,
        )
        tensor = self._torch.as_tensor(vector[None, :], dtype=self._torch.float32)
        with self._torch.no_grad():
            logits = self._head(tensor.to(self._device))
            probabilities = self._torch.sigmoid(logits)[0].cpu().tolist()
        return {
            target: float(probabilities[i])
            for i, target in enumerate(MVP_TARGETS)
        }


class CompactCnnScorer:
    def __init__(self, *, checkpoint: str | Path, device: str = "cpu") -> None:
        np, torch = _require_stack()
        payload = torch.load(Path(checkpoint), map_location=device)
        targets = tuple(payload.get("targets") or ())
        if targets != MVP_TARGETS:
            raise ValueError(f"checkpoint targets {targets} != {MVP_TARGETS}")
        if payload.get("benchmark") != "COMPACT_LOGMEL_CNN":
            raise ValueError("checkpoint is not COMPACT_LOGMEL_CNN")

        self.sample_rate_hz = int(payload["sample_rate_hz"])
        self.clip_seconds = float(payload["clip_seconds"])
        self.model_version = str(Path(checkpoint))
        self.validation_thresholds = dict(payload.get("validation_thresholds") or {})
        self._device = device
        self._np = np
        self._torch = torch
        self._model = build_compact_cnn(
            num_targets=len(MVP_TARGETS),
            sample_rate_hz=self.sample_rate_hz,
            f_max=self.sample_rate_hz / 2,
        ).to(device)
        self._model.load_state_dict(payload["state_dict"])
        self._model.eval()

    def score(self, waveform: Sequence[float]) -> dict[str, float]:
        values = self._np.asarray(waveform, dtype=self._np.float32)
        target_samples = int(round(self.sample_rate_hz * self.clip_seconds))
        if values.size >= target_samples:
            start = (values.size - target_samples) // 2
            values = values[start : start + target_samples]
        else:
            values = self._np.pad(
                values,
                (0, target_samples - values.size),
                mode="constant",
            )
        tensor = self._torch.as_tensor(
            values[None, :],
            dtype=self._torch.float32,
            device=self._device,
        )
        with self._torch.no_grad():
            probabilities = self._torch.sigmoid(self._model(tensor))[0].cpu().tolist()
        return {
            target: float(probabilities[i])
            for i, target in enumerate(MVP_TARGETS)
        }

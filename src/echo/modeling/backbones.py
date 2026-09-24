"""Optional pretrained embedding backbones for ECHO MVP Benchmark A/B."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence


class EmbeddingBackbone(Protocol):
    name: str
    sample_rate_hz: int
    embedding_dim: int

    def embed(self, waveform: Sequence[float]):
        ...


@dataclass
class YAMNetEmbeddingBackbone:
    """Official TensorFlow Hub YAMNet/1 embedding extractor."""

    model_handle: str = "https://tfhub.dev/google/yamnet/1"
    name: str = "YAMNET_EMBEDDINGS_HEAD"
    sample_rate_hz: int = 16000
    embedding_dim: int = 1024

    def __post_init__(self) -> None:
        try:
            import tensorflow_hub as hub
        except ImportError as exc:
            raise RuntimeError(
                "YAMNet requires the 'yamnet' optional dependencies"
            ) from exc
        self._model = hub.load(self.model_handle)

    def embed(self, waveform: Sequence[float]):
        try:
            import numpy as np
        except ImportError as exc:
            raise RuntimeError("YAMNet benchmark requires numpy") from exc

        audio = np.asarray(waveform, dtype=np.float32)
        if audio.ndim != 1 or audio.size == 0:
            raise ValueError("YAMNet waveform must be non-empty mono PCM")
        _scores, embeddings, _spectrogram = self._model(audio)
        values = embeddings.numpy()
        if values.ndim != 2 or values.shape[1] != self.embedding_dim:
            raise RuntimeError(
                f"unexpected YAMNet embedding shape: {values.shape}"
            )
        return values.mean(axis=0, dtype=np.float32)


@dataclass
class PannsCnn14EmbeddingBackbone:
    """Official panns-inference Cnn14 embedding extractor."""

    checkpoint_path: str | None = None
    device: str = "cpu"
    name: str = "PANNS_CNN14_HEAD"
    sample_rate_hz: int = 32000
    embedding_dim: int = 2048

    def __post_init__(self) -> None:
        if not self.checkpoint_path:
            raise ValueError(
                "PANNs requires an explicit checkpoint_path; implicit upstream "
                "weight download is not allowed in ECHO benchmark/replay."
            )
        try:
            from panns_inference import AudioTagging
        except ImportError as exc:
            raise RuntimeError(
                "PANNs requires the 'panns' optional dependencies"
            ) from exc
        self._tagger = AudioTagging(
            checkpoint_path=self.checkpoint_path,
            device=self.device,
        )

    def embed(self, waveform: Sequence[float]):
        try:
            import numpy as np
        except ImportError as exc:
            raise RuntimeError("PANNs benchmark requires numpy") from exc

        audio = np.asarray(waveform, dtype=np.float32)
        if audio.ndim != 1 or audio.size == 0:
            raise ValueError("PANNs waveform must be non-empty mono PCM")
        _clipwise, embedding = self._tagger.inference(audio[None, :])
        values = np.asarray(embedding, dtype=np.float32)
        if values.ndim == 1:
            vector = values
        elif values.ndim == 2 and values.shape[0] == 1:
            vector = values[0]
        else:
            raise RuntimeError(f"unexpected PANNs embedding shape: {values.shape}")
        if vector.shape[0] != self.embedding_dim:
            raise RuntimeError(
                f"expected {self.embedding_dim} PANNs features, got {vector.shape[0]}"
            )
        return vector

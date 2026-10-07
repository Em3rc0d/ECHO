#!/usr/bin/env python3
"""Build deterministic long-stream temporal calibration fixtures from validation only.

The frozen benchmark validation split is partitioned by recording_group_id into
non-overlapping temporal_tune (80%) and temporal_holdout (20%) pools. The test
split is never read into calibration scenarios.

Scenarios are synthetic compositions of real governed validation audio:
- mixed: isolated/interleaved positive events separated by real background;
- burst_<target>: same-class events separated by short real-background gaps;
- negative: real background-only material.

A short edge fade suppresses concatenation discontinuities. This is controlled
validation evidence, not field calibration.
"""

from __future__ import annotations

import argparse
from array import array
import hashlib
import json
from pathlib import Path
import struct
import sys
import wave

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from echo.modeling.audio import decode_audio_f32_mono
from echo.modeling.manifest import MVP_TARGETS, BenchmarkRow, load_benchmark_manifest
from echo.modeling.media_index import load_media_index

TARGETS = tuple(MVP_TARGETS)


def stable_key(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def partition_for_group(recording_group_id: str) -> str:
    digest = hashlib.sha256(recording_group_id.encode("utf-8")).digest()
    return "temporal_holdout" if int.from_bytes(digest[:4], "big") % 5 == 0 else "temporal_tune"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def apply_edge_fade(values, sample_rate_hz: int, seconds: float = 0.02):
    import numpy as np

    audio = np.asarray(values, dtype=np.float32).copy()
    count = min(int(round(sample_rate_hz * seconds)), audio.size // 2)
    if count <= 0:
        return audio
    ramp = np.linspace(0.0, 1.0, count, endpoint=True, dtype=np.float32)
    audio[:count] *= ramp
    audio[-count:] *= ramp[::-1]
    return audio


def write_pcm16_wav(path: Path, values, sample_rate_hz: int) -> None:
    import numpy as np

    audio = np.asarray(values, dtype=np.float32)
    audio = np.clip(audio, -1.0, 1.0)
    pcm = (audio * 32767.0).round().astype("<i2", copy=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate_hz)
        handle.writeframes(pcm.tobytes())


class FixtureBuilder:
    def __init__(
        self,
        *,
        media: dict[str, str],
        sample_rate_hz: int,
        positive_clip_max_seconds: float,
    ) -> None:
        import numpy as np

        self.np = np
        self.media = media
        self.sample_rate_hz = sample_rate_hz
        self.positive_clip_max_samples = int(
            round(sample_rate_hz * positive_clip_max_seconds)
        )
        self.cache: dict[str, object] = {}

    def decoded(self, row: BenchmarkRow):
        if row.media_sha256 not in self.cache:
            values = decode_audio_f32_mono(
                self.media[row.media_sha256],
                sample_rate_hz=self.sample_rate_hz,
            )
            self.cache[row.media_sha256] = apply_edge_fade(
                values,
                self.sample_rate_hz,
            )
        return self.cache[row.media_sha256]

    def positive(self, row: BenchmarkRow):
        audio = self.decoded(row)
        if audio.size <= self.positive_clip_max_samples:
            return audio.copy()
        start = (audio.size - self.positive_clip_max_samples) // 2
        return audio[start : start + self.positive_clip_max_samples].copy()


def select_positive_rows(
    rows: list[BenchmarkRow],
    *,
    quotas: dict[str, int],
) -> list[BenchmarkRow]:
    pools = {
        target: sorted(
            [row for row in rows if target in row.positive_labels],
            key=lambda row: stable_key(row.asset_id),
        )
        for target in TARGETS
    }
    selected: list[BenchmarkRow] = []
    used: set[str] = set()
    counts = {target: 0 for target in TARGETS}

    while any(counts[target] < quotas[target] for target in TARGETS):
        progressed = False
        for target in TARGETS:
            if counts[target] >= quotas[target]:
                continue
            candidate = next(
                (row for row in pools[target] if row.asset_id not in used),
                None,
            )
            if candidate is None:
                raise RuntimeError(
                    f"insufficient unique {target} validation positives for quota "
                    f"{quotas[target]}"
                )
            selected.append(candidate)
            used.add(candidate.asset_id)
            for label in candidate.positive_labels:
                if label in counts:
                    counts[label] += 1
            progressed = True
        if not progressed:
            raise RuntimeError("positive fixture selection stalled")

    return sorted(selected, key=lambda row: stable_key("mixed:" + row.asset_id))


def build_scenario(
    *,
    scenario_id: str,
    partition: str,
    positive_rows: list[BenchmarkRow],
    background_rows: list[BenchmarkRow],
    builder: FixtureBuilder,
    gap_pattern_seconds: list[float],
    initial_seconds: float,
    final_seconds: float,
):
    np = builder.np
    chunks = []
    truth = []
    source_segments = []
    cursor = 0
    background_cursor = 0

    def append_background(seconds: float):
        nonlocal cursor, background_cursor
        wanted = int(round(seconds * builder.sample_rate_hz))
        remaining = wanted
        segment_start = cursor
        asset_ids = []
        while remaining > 0:
            row = background_rows[background_cursor % len(background_rows)]
            background_cursor += 1
            audio = builder.decoded(row)
            take = min(remaining, int(audio.size))
            chunks.append(audio[:take])
            cursor += take
            remaining -= take
            asset_ids.append(row.asset_id)
        source_segments.append(
            {
                "kind": "background",
                "start_seconds": segment_start / builder.sample_rate_hz,
                "end_seconds": cursor / builder.sample_rate_hz,
                "asset_ids": asset_ids,
            }
        )

    append_background(initial_seconds)
    for index, row in enumerate(positive_rows):
        audio = builder.positive(row)
        start = cursor
        chunks.append(audio)
        cursor += int(audio.size)
        end = cursor
        labels = [label for label in row.positive_labels if label in TARGETS]
        truth.append(
            {
                "asset_id": row.asset_id,
                "media_sha256": row.media_sha256,
                "labels": labels,
                "start_seconds": start / builder.sample_rate_hz,
                "end_seconds": end / builder.sample_rate_hz,
            }
        )
        source_segments.append(
            {
                "kind": "positive",
                "asset_id": row.asset_id,
                "labels": labels,
                "start_seconds": start / builder.sample_rate_hz,
                "end_seconds": end / builder.sample_rate_hz,
            }
        )
        if index < len(positive_rows) - 1:
            append_background(gap_pattern_seconds[index % len(gap_pattern_seconds)])
    append_background(final_seconds)

    waveform = np.concatenate(chunks).astype(np.float32, copy=False)
    return {
        "scenario_id": scenario_id,
        "partition": partition,
        "sample_rate_hz": builder.sample_rate_hz,
        "duration_seconds": waveform.size / builder.sample_rate_hz,
        "ground_truth": truth,
        "segments": source_segments,
    }, waveform


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "MK1/mining-site/materialization/mvp-benchmark-manifest.jsonl",
    )
    parser.add_argument("--media-index", type=Path, required=True)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "artifacts/mvp-temporal",
    )
    parser.add_argument("--sample-rate", type=int, default=32000)
    parser.add_argument("--positive-clip-max-seconds", type=float, default=12.0)
    args = parser.parse_args()

    if args.sample_rate <= 0 or args.positive_clip_max_seconds <= 0:
        raise SystemExit("sample rate and positive clip max must be positive")

    rows = [
        row
        for row in load_benchmark_manifest(args.manifest)
        if row.split == "validation"
    ]
    if not rows:
        raise SystemExit("validation split is empty")
    media = load_media_index(args.media_index)

    partitions = {
        name: [
            row
            for row in rows
            if partition_for_group(row.recording_group_id) == name
        ]
        for name in ("temporal_tune", "temporal_holdout")
    }

    output_dir = args.output_dir.resolve()
    stream_dir = output_dir / "streams"
    stream_dir.mkdir(parents=True, exist_ok=True)
    builder = FixtureBuilder(
        media=media,
        sample_rate_hz=args.sample_rate,
        positive_clip_max_seconds=args.positive_clip_max_seconds,
    )

    scenarios = []
    pool_stats = {}
    for partition, pool in partitions.items():
        backgrounds = sorted(
            [
                row
                for row in pool
                if not row.positive_labels
                and all(row.supervision.get(target) == 0 for target in TARGETS)
            ],
            key=lambda row: stable_key("background:" + row.asset_id),
        )
        positive_counts = {
            target: sum(target in row.positive_labels for row in pool)
            for target in TARGETS
        }
        pool_stats[partition] = {
            "rows": len(pool),
            "recording_groups": len({row.recording_group_id for row in pool}),
            "pure_background_rows": len(backgrounds),
            "positive_counts": positive_counts,
        }
        if len(backgrounds) < 3:
            raise RuntimeError(f"{partition}: insufficient pure background rows")

        quotas = (
            {"GLASS_SHATTER": 9, "SIREN": 12, "VEHICLE_HORN": 12}
            if partition == "temporal_tune"
            else {"GLASS_SHATTER": 5, "SIREN": 6, "VEHICLE_HORN": 6}
        )
        quotas = {
            target: min(quotas[target], positive_counts[target])
            for target in TARGETS
        }
        mixed_rows = select_positive_rows(pool, quotas=quotas)
        spec, waveform = build_scenario(
            scenario_id=f"{partition}-mixed",
            partition=partition,
            positive_rows=mixed_rows,
            background_rows=backgrounds,
            builder=builder,
            gap_pattern_seconds=[4.0, 7.0, 3.0, 9.0, 5.0],
            initial_seconds=8.0,
            final_seconds=8.0,
        )
        wav = stream_dir / f"{spec['scenario_id']}.wav"
        write_pcm16_wav(wav, waveform, args.sample_rate)
        spec["wav"] = str(wav)
        spec["wav_sha256"] = sha256_file(wav)
        scenarios.append(spec)

        negative_spec, negative_waveform = build_scenario(
            scenario_id=f"{partition}-negative",
            partition=partition,
            positive_rows=[],
            background_rows=backgrounds,
            builder=builder,
            gap_pattern_seconds=[1.0],
            initial_seconds=120.0 if partition == "temporal_tune" else 90.0,
            final_seconds=0.0,
        )
        negative_wav = stream_dir / f"{negative_spec['scenario_id']}.wav"
        write_pcm16_wav(negative_wav, negative_waveform, args.sample_rate)
        negative_spec["wav"] = str(negative_wav)
        negative_spec["wav_sha256"] = sha256_file(negative_wav)
        scenarios.append(negative_spec)

        for target in TARGETS:
            target_rows = sorted(
                [row for row in pool if target in row.positive_labels],
                key=lambda row: stable_key(f"burst:{target}:{row.asset_id}"),
            )[:3]
            burst_spec, burst_waveform = build_scenario(
                scenario_id=f"{partition}-burst-{target.lower()}",
                partition=partition,
                positive_rows=target_rows,
                background_rows=backgrounds,
                builder=builder,
                gap_pattern_seconds=[1.0, 2.0],
                initial_seconds=8.0,
                final_seconds=8.0,
            )
            burst_wav = stream_dir / f"{burst_spec['scenario_id']}.wav"
            write_pcm16_wav(burst_wav, burst_waveform, args.sample_rate)
            burst_spec["wav"] = str(burst_wav)
            burst_spec["wav_sha256"] = sha256_file(burst_wav)
            scenarios.append(burst_spec)

    tune_groups = {
        row.recording_group_id for row in partitions["temporal_tune"]
    }
    holdout_groups = {
        row.recording_group_id for row in partitions["temporal_holdout"]
    }
    overlap = sorted(tune_groups & holdout_groups)
    if overlap:
        raise RuntimeError(f"temporal partition group leakage: {overlap[:5]}")

    payload = {
        "schema_version": "echo.mvp-temporal-fixtures.v1",
        "profile_id": "ECHO-MVP-001",
        "status": "CONTROLLED_VALIDATION_FIXTURES",
        "source_split": "validation",
        "partition_rule": (
            "recording_group_id SHA256 first-32-bit modulo 5; bucket 0 holdout, "
            "buckets 1-4 tune"
        ),
        "test_split_used": False,
        "sample_rate_hz": args.sample_rate,
        "positive_clip_max_seconds": args.positive_clip_max_seconds,
        "edge_fade_seconds": 0.02,
        "pool_stats": pool_stats,
        "recording_group_overlap_count": 0,
        "scenarios": scenarios,
        "boundary": (
            "Synthetic long streams composed from real governed validation audio. "
            "Suitable for controlled temporal calibration, not field calibration."
        ),
    }
    output = output_dir / "fixtures.json"
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "output": str(output),
                "scenario_count": len(scenarios),
                "pool_stats": pool_stats,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

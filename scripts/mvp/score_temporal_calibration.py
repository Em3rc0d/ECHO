#!/usr/bin/env python3
"""Score controlled temporal fixtures with the selected ECHO MVP model.

Scores are cached per scenario so threshold sweeps never rerun PANNs. The cache
identity includes the stream WAV, selected ECHO head, PANNs checkpoint and
window/hop contract.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from echo.modeling.audio import decode_audio_f32_mono
from echo.modeling.inference import EmbeddingHeadScorer
from echo.runtime.replay import iter_replay_windows


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_checkpoint(raw: str, selection: Path) -> Path:
    path = Path(raw)
    candidates = [path]
    normalized_name = Path(str(raw).replace("\\", "/")).name
    candidates.append(selection.resolve().parent / "panns" / normalized_name)
    if not path.is_absolute():
        candidates.append((ROOT / path).resolve())
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise SystemExit(
        "selected PANNs head not found: "
        + ", ".join(str(candidate) for candidate in candidates)
    )


def resolve_stream(fixtures: Path, row: dict) -> Path:
    stored = Path(str(row.get("wav") or ""))
    candidates = [
        stored,
        fixtures.resolve().parent / "streams" / stored.name,
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise SystemExit(
        f"scenario {row.get('scenario_id')}: WAV not found in "
        + ", ".join(str(candidate) for candidate in candidates)
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixtures", type=Path, required=True)
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--panns-checkpoint", type=Path, required=True)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "artifacts/mvp-temporal/scores",
    )
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--window-seconds", type=float, default=6.0)
    parser.add_argument("--hop-seconds", type=float, default=1.0)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.window_seconds <= 0 or args.hop_seconds <= 0:
        raise SystemExit("window/hop must be positive")

    fixtures = json.loads(args.fixtures.read_text(encoding="utf-8"))
    if fixtures.get("source_split") != "validation":
        raise SystemExit("temporal fixtures must be derived from validation")
    if fixtures.get("test_split_used") is not False:
        raise SystemExit("refusing temporal fixtures that used test")

    selection = json.loads(args.selection.read_text(encoding="utf-8"))
    winner = selection.get("winner") or {}
    if winner.get("benchmark") != "PANNS_CNN14_HEAD":
        raise SystemExit(
            "ECHO-MVP-001 temporal calibration currently requires "
            "PANNS_CNN14_HEAD as selected winner"
        )

    head_checkpoint = resolve_checkpoint(
        str(winner.get("checkpoint") or ""),
        args.selection,
    )
    panns_checkpoint = args.panns_checkpoint.resolve()
    if not panns_checkpoint.is_file():
        raise SystemExit(f"PANNs checkpoint missing: {panns_checkpoint}")

    head_sha = sha256_file(head_checkpoint)
    panns_sha = sha256_file(panns_checkpoint)
    scorer = EmbeddingHeadScorer(
        checkpoint=head_checkpoint,
        backbone="panns",
        device=args.device,
        panns_checkpoint=str(panns_checkpoint),
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    scenario_results = []

    for scenario in fixtures.get("scenarios") or []:
        scenario_id = str(scenario["scenario_id"])
        wav = resolve_stream(args.fixtures, scenario)
        wav_sha = sha256_file(wav)
        expected_wav_sha = str(scenario.get("wav_sha256") or "")
        if expected_wav_sha and wav_sha != expected_wav_sha:
            raise RuntimeError(
                f"{scenario_id}: WAV SHA mismatch {wav_sha} != {expected_wav_sha}"
            )

        identity = {
            "schema_version": "echo.mvp-temporal-score-cache.v1",
            "scenario_id": scenario_id,
            "wav_sha256": wav_sha,
            "head_sha256": head_sha,
            "panns_sha256": panns_sha,
            "window_seconds": args.window_seconds,
            "hop_seconds": args.hop_seconds,
            "sample_rate_hz": scorer.sample_rate_hz,
        }
        identity_sha = hashlib.sha256(
            json.dumps(identity, sort_keys=True).encode("utf-8")
        ).hexdigest()
        scores_path = args.output_dir / f"{scenario_id}.jsonl"
        meta_path = args.output_dir / f"{scenario_id}.meta.json"

        if not args.force and scores_path.is_file() and meta_path.is_file():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            if (
                meta.get("status") == "COMPLETE"
                and meta.get("identity_sha256") == identity_sha
            ):
                print(f"scores {scenario_id}: cache HIT", flush=True)
                scenario_results.append(meta)
                continue

        waveform = decode_audio_f32_mono(
            wav,
            sample_rate_hz=scorer.sample_rate_hz,
        )
        temp = scores_path.with_suffix(".jsonl.part")
        window_count = 0
        with temp.open("w", encoding="utf-8") as handle:
            for window in iter_replay_windows(
                waveform,
                sample_rate_hz=scorer.sample_rate_hz,
                window_seconds=args.window_seconds,
                hop_seconds=args.hop_seconds,
                pad_final=True,
            ):
                scores = scorer.score(window.waveform)
                row = {
                    "schema_version": "echo.mvp-temporal-window-score.v1",
                    "scenario_id": scenario_id,
                    "partition": scenario["partition"],
                    "window_index": window.index,
                    "start_seconds": window.start_sample / scorer.sample_rate_hz,
                    "end_seconds": window.end_sample / scorer.sample_rate_hz,
                    "scores": scores,
                }
                handle.write(json.dumps(row, sort_keys=True) + "\n")
                window_count += 1
                if window_count % 50 == 0:
                    print(
                        f"scores {scenario_id}: {window_count} windows",
                        flush=True,
                    )
        temp.replace(scores_path)

        meta = {
            **identity,
            "identity_sha256": identity_sha,
            "status": "COMPLETE",
            "score_file": str(scores_path),
            "window_count": window_count,
        }
        meta_path.write_text(
            json.dumps(meta, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        scenario_results.append(meta)
        print(
            f"scores {scenario_id}: COMPLETE windows={window_count}",
            flush=True,
        )

    summary = {
        "schema_version": "echo.mvp-temporal-score-summary.v1",
        "profile_id": "ECHO-MVP-001",
        "status": "COMPLETE",
        "model_benchmark": "PANNS_CNN14_HEAD",
        "head_checkpoint": str(head_checkpoint),
        "head_sha256": head_sha,
        "panns_checkpoint": str(panns_checkpoint),
        "panns_sha256": panns_sha,
        "window_seconds": args.window_seconds,
        "hop_seconds": args.hop_seconds,
        "scenario_count": len(scenario_results),
        "scenarios": scenario_results,
    }
    output = args.output_dir.parent / "score-summary.json"
    output.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": summary["status"],
                "output": str(output),
                "scenario_count": len(scenario_results),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "imageio-ffmpeg",
#   "mlx-whisper",
#   "numpy",
# ]
# ///
"""Align supplied lyric lines to local recordings with word-timestamped Whisper."""
from __future__ import annotations

import argparse
from difflib import SequenceMatcher
import json
from pathlib import Path
import re
import subprocess
import unicodedata

ROOT = Path(__file__).resolve().parent.parent
SYNC_PREFIX = "window.ANS_SYNC = "


def load_catalog() -> dict:
    text = (ROOT / "data.js").read_text()
    return json.loads(re.sub(r"^window\.ANS_DATA\s*=\s*", "", text).rstrip().removesuffix(";"))


def load_sync(path: Path) -> dict:
    if not path.exists():
        return {}
    text = path.read_text().strip()
    if not text.startswith(SYNC_PREFIX):
        raise ValueError(f"unexpected sync-file prefix in {path}")
    return json.loads(text.removeprefix(SYNC_PREFIX).removesuffix(";"))


def merge_sync(existing: dict, updates: dict, catalog_order: list[str]) -> dict:
    merged = {**existing, **updates}
    return {track_id: merged[track_id] for track_id in catalog_order if track_id in merged}


def normalize_word(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "", value)


def lyric_lines(lyrics: str) -> list[dict]:
    lines = []
    stanza_start = True
    for raw in lyrics.splitlines():
        text = raw.strip()
        if not text:
            stanza_start = True
            continue
        tokens = [token for token in (normalize_word(part) for part in text.split()) if token]
        lines.append({"text": text, "tokens": tokens, "stanzaStart": stanza_start})
        stanza_start = False
    return lines


def decode_audio(path: Path):
    import imageio_ffmpeg
    import numpy as np

    command = [
        imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i", str(path),
        "-ac", "1", "-ar", "16000", "-f", "f32le", "pipe:1",
    ]
    result = subprocess.run(command, check=True, stdout=subprocess.PIPE)
    return np.frombuffer(result.stdout, dtype=np.float32)


def transcribe(path: Path, lyrics: str, model: str) -> list[dict]:
    import mlx_whisper

    prompt = " ".join(lyrics.split())[:1800]
    result = mlx_whisper.transcribe(
        decode_audio(path),
        path_or_hf_repo=model,
        word_timestamps=True,
        initial_prompt=prompt,
        language="en",
        verbose=None,
        condition_on_previous_text=False,
    )
    return [word for segment in result["segments"] for word in segment.get("words", [])]


def interpolate_missing(values: list[float | None], weights: list[int], duration: float) -> list[float]:
    known = [index for index, value in enumerate(values) if value is not None]
    if not known:
        total = sum(weights) or 1
        cursor = min(8.0, duration * 0.06)
        end = max(cursor + 1, duration - min(4.0, duration * 0.025))
        output = []
        for weight in weights:
            output.append(cursor)
            cursor += (end - output[0]) * weight / total
        return output

    output = list(values)
    first = known[0]
    if first:
        first_time = float(output[first])
        total_weight = sum(weights[:first]) or first
        available = min(first_time, max(2.0, total_weight * 0.45))
        cursor = max(0.0, first_time - available)
        for index in range(first):
            output[index] = cursor
            cursor += available * weights[index] / total_weight

    for left, right in zip(known, known[1:]):
        if right - left <= 1:
            continue
        left_time = float(output[left])
        right_time = float(output[right])
        middle_weights = weights[left + 1:right]
        total_weight = sum(middle_weights) or len(middle_weights)
        cursor = left_time
        available = max(0.05 * len(middle_weights), right_time - left_time)
        for offset, weight in enumerate(middle_weights, start=left + 1):
            cursor += available * weight / (total_weight + weights[left])
            output[offset] = min(cursor, right_time - 0.03 * (right - offset))

    last = known[-1]
    if last < len(output) - 1:
        last_time = float(output[last])
        tail_weights = weights[last + 1:]
        total_weight = sum(tail_weights) or len(tail_weights)
        cursor = last_time
        available = max(0.5, duration - last_time)
        for offset, weight in enumerate(tail_weights, start=last + 1):
            cursor += available * weight / (total_weight + weights[last])
            output[offset] = min(cursor, duration - 0.03 * (len(output) - offset))

    result = [max(0.0, min(duration, float(value))) for value in output]
    for index in range(1, len(result)):
        result[index] = max(result[index], result[index - 1] + 0.03)
    return result


def align(lyrics: str, words: list[dict], duration: float) -> tuple[list[dict], float]:
    lines = lyric_lines(lyrics)
    expected = []
    expected_lines = []
    for line_index, line in enumerate(lines):
        expected.extend(line["tokens"])
        expected_lines.extend([line_index] * len(line["tokens"]))

    recognized_words = []
    recognized = []
    for word in words:
        token = normalize_word(word.get("word", ""))
        if token:
            recognized.append(token)
            recognized_words.append(word)

    matcher = SequenceMatcher(None, expected, recognized, autojunk=False)
    token_times: dict[int, float] = {}
    for block in matcher.get_matching_blocks():
        for offset in range(block.size):
            token_times[block.a + offset] = float(recognized_words[block.b + offset]["start"])

    line_times: list[float | None] = [None] * len(lines)
    matches_per_line = [0] * len(lines)
    for expected_index, timestamp in token_times.items():
        line_index = expected_lines[expected_index]
        matches_per_line[line_index] += 1
        if line_times[line_index] is None:
            line_times[line_index] = timestamp

    weights = [max(2, len(line["tokens"])) for line in lines]
    starts = interpolate_missing(line_times, weights, duration)
    cues = []
    for index, line in enumerate(lines):
        end = starts[index + 1] - 0.03 if index + 1 < len(starts) else duration
        cues.append({
            "start": round(starts[index], 2),
            "end": round(max(starts[index] + 0.03, end), 2),
            "text": line["text"],
            "stanzaStart": line["stanzaStart"],
        })
    confidence = len(token_times) / max(1, len(expected))
    return cues, confidence


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="mlx-community/whisper-tiny")
    parser.add_argument("--only", action="append", help="Generate one or more track IDs")
    args = parser.parse_args()

    catalog = load_catalog()
    selected = set(args.only or [])
    known = {track["id"] for track in catalog["tracks"]}
    unknown = selected - known
    if unknown:
        parser.error(f"unknown track ID(s): {', '.join(sorted(unknown))}")
    instrumental = {track["id"] for track in catalog["tracks"] if track.get("instrumental")}
    unsupported = selected & instrumental
    if unsupported:
        parser.error(f"instrumental track(s) do not need lyric cues: {', '.join(sorted(unsupported))}")
    destination = ROOT / "lyrics-sync.js"
    output = load_sync(destination) if selected else {}
    updates = {}
    cache = {}
    for track in catalog["tracks"]:
        if selected and track["id"] not in selected:
            continue
        if track.get("instrumental"):
            continue
        path = ROOT / track["audio"]
        key = (path.resolve(), track["lyrics"])
        if key not in cache:
            words = transcribe(path, track["lyrics"], args.model)
            cache[key] = align(track["lyrics"], words, float(track["duration"]))
        cues, confidence = cache[key]
        updates[track["id"]] = {
            "duration": track["duration"],
            "confidence": round(confidence, 3),
            "model": args.model,
            "cues": cues,
        }
        print(f"{track['id']}: {len(cues)} lines, {confidence:.0%} exact-token alignment", flush=True)

    order = [track["id"] for track in catalog["tracks"]]
    output = merge_sync(output, updates, order)
    destination.write_text("window.ANS_SYNC = " + json.dumps(output, ensure_ascii=False, indent=2) + ";\n")
    print(f"Wrote {len(output)} synchronized tracks to {destination}")


if __name__ == "__main__":
    main()

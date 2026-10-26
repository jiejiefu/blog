#!/usr/bin/env python3
"""Build a WebVTT subtitle file from any audio or video file.

Two modes:

  1. Exact script mode (recommended for narrated articles) -- pass --cues.
     The cue text is taken verbatim from the file; ASR only supplies word
     timings. Unmatched tokens (numbers, abbreviations, punctuation) are
     interpolated between their nearest matched neighbours.

  2. Transcript mode -- omit --cues. The ASR transcript becomes the subtitle
     text, split at punctuation and by --max-chars / --max-duration.

Use --words-per-cue N to break both modes into short cues of roughly N words.
Cues are made contiguous (each cue ends where the next begins) so the caption
never disappears between lines.

Output defaults to ``<media-stem>.vtt`` next to the media file. Pass --out to
change it; if --out is an existing directory, the default filename is used
inside that directory.

The model is never downloaded. The script sets HF_HUB_OFFLINE=1 and passes
local_files_only=True. Use --model with a local snapshot directory if the
model is not already in the Hugging Face cache.

Requires faster-whisper. In this repo, VoiceStudio's runtime venv already has
it (and the large-v3 weights):

  ~/Library/Application Support/VoiceStudio/runtime/project/.venv/bin/python \
    scripts/build_audio_vtt.py content/en/projects/foo/audio/foo.m4a \
    --cues scripts/foo/foo.cues.txt --language en

Transcript mode:

  python3 scripts/build_audio_vtt.py path/to/talk.mp4 --language en
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

NUMBER_WORDS = {
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "eleven": "11",
    "twelve": "12",
    "thirteen": "13",
    "fourteen": "14",
    "fifteen": "15",
    "sixteen": "16",
    "seventeen": "17",
    "eighteen": "18",
    "nineteen": "19",
    "twenty": "20",
}

TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:['\u2019][A-Za-z]+)*")
SENTENCE_END_RE = re.compile(r"[.!?;:]\s*$")


def resolve_path(path: Path) -> Path:
    return path if path.is_absolute() else Path.cwd() / path


def normalise_token(raw: str) -> str:
    token = raw.lower().replace("\u2019", "'")
    token = token.strip(".,!?;:\"'()[]{}<>\u2014\u2013-")
    if token in NUMBER_WORDS:
        token = NUMBER_WORDS[token]
    return token


def tokenize(text: str) -> list[str]:
    return [t for t in (normalise_token(m.group(0)) for m in TOKEN_RE.finditer(text)) if t]


def read_cues(path: Path) -> list[str]:
    cues = []
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if text:
            cues.append(text)
    if not cues:
        raise SystemExit(f"no cue text found in {path}")
    return cues


def format_timestamp(seconds: float) -> str:
    total_ms = max(0, int(round(seconds * 1000)))
    hours, total_ms = divmod(total_ms, 3_600_000)
    minutes, total_ms = divmod(total_ms, 60_000)
    secs, millis = divmod(total_ms, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def merge_single_letters(tokens: list[str], times: list[tuple[float, float]]):
    """Turn ASR runs like ``R U L`` into ``rul`` so they can match ``RUL``."""
    merged_tokens: list[str] = []
    merged_times: list[tuple[float, float]] = []
    i = 0
    while i < len(tokens):
        if len(tokens[i]) == 1 and tokens[i].isalpha():
            j = i
            letters = []
            while j < len(tokens) and len(tokens[j]) == 1 and tokens[j].isalpha():
                letters.append(tokens[j])
                j += 1
            if j - i >= 2:
                merged_tokens.append("".join(letters))
                merged_times.append((times[i][0], times[j - 1][1]))
                i = j
                continue
        merged_tokens.append(tokens[i])
        merged_times.append(times[i])
        i += 1
    return merged_tokens, merged_times


def dedupe_repeats(
    words: list[tuple[str, float, float]], max_gap: float = 1.0
) -> list[tuple[str, float, float]]:
    """Drop immediate ASR stutters such as the trailing ``systems. systems.``.

    The duplicate is folded into the previous word so the cue still covers the
    spoken audio, but the text appears once.
    """
    out: list[tuple[str, float, float]] = []
    prev_norm = None
    prev_end = -1.0
    for word, start, end in words:
        norm = normalise_token(word)
        if norm and norm == prev_norm and start - prev_end <= max_gap and out:
            previous = out[-1]
            out[-1] = (previous[0], previous[1], end)
            prev_end = end
            continue
        out.append((word, start, end))
        prev_norm = norm
        prev_end = end
    return out


def clean_asr_text(text: str) -> str:
    text = re.sub(r"\s+-\s*(?=\w)", "-", text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    return re.sub(r"\s{2,}", " ", text).strip()


def align_times(
    article_tokens: list[str],
    asr_tokens: list[str],
    asr_times: list[tuple[float, float]],
    duration: float,
) -> list[tuple[float, float]]:
    matcher = SequenceMatcher(None, article_tokens, asr_tokens, autojunk=False)
    times: list[tuple[float, float] | None] = [None] * len(article_tokens)
    for i, j, n in matcher.get_matching_blocks():
        for k in range(n):
            times[i + k] = asr_times[j + k]

    if not any(times):
        raise SystemExit(
            "ASR produced no usable alignment with the cue text. "
            "Run with --dump-transcript and adjust the cues."
        )

    idx = 0
    while idx < len(times):
        if times[idx] is not None:
            idx += 1
            continue
        gap_start = idx
        while idx < len(times) and times[idx] is None:
            idx += 1
        gap_end = idx
        prev = times[gap_start - 1] if gap_start > 0 else None
        nxt = times[gap_end] if gap_end < len(times) else None
        lo = prev[1] if prev else 0.0
        hi = nxt[0] if nxt else duration
        if hi < lo:
            hi = lo
        count = gap_end - gap_start
        step = (hi - lo) / count if count else 0.0
        for k in range(count):
            times[gap_start + k] = (lo + step * k, lo + step * (k + 1))
    return [t for t in times if t is not None]


def build_cues(
    raw: list[tuple[float, float]],
    duration: float,
    start_pad: float,
    end_pad: float,
) -> list[tuple[float, float]]:
    cues = []
    prev_end = 0.0
    for i, (raw_start, raw_end) in enumerate(raw):
        start = max(0.0, raw_start - start_pad)
        if start < prev_end + 0.001:
            start = prev_end + 0.001
        end = raw_end + end_pad
        if end <= start:
            end = start + 0.25
        if i == len(raw) - 1:
            end = duration
        if end <= start:
            end = min(duration, start + 0.25)
        cues.append((start, end))
        prev_end = end
    return cues


def make_contiguous(times: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """End every cue where the next one starts, so captions never go blank."""
    out = [[start, end] for start, end in times]
    for i in range(len(out) - 1):
        start, end = out[i]
        next_start = out[i + 1][0]
        if next_start > start + 0.001:
            out[i][1] = next_start
        else:
            out[i][1] = max(start + 0.05, end)
    return [(start, end) for start, end in out]


def split_cue_words(text: str, words_per_cue: int) -> list[tuple[str, int]]:
    """Split cue text into chunks of roughly N whitespace words.

    Returns ``(chunk_text, token_count)``. Punctuation-only chunks are folded
    into the previous chunk so every chunk can be assigned a timing.
    """
    if words_per_cue <= 0:
        return [(text, len(tokenize(text)))]
    words = text.split()
    if len(words) <= words_per_cue:
        return [(text, len(tokenize(text)))]

    count_chunks = (len(words) + words_per_cue - 1) // words_per_cue
    base, extra = divmod(len(words), count_chunks)
    sizes = [base + (1 if i < extra else 0) for i in range(count_chunks)]

    chunks: list[tuple[str, int]] = []
    cursor = 0
    for size in sizes:
        chunk = " ".join(words[cursor:cursor + size])
        cursor += size
        count = len(tokenize(chunk))
        if count == 0:
            if chunks:
                previous, previous_count = chunks[-1]
                chunks[-1] = (previous + " " + chunk, previous_count)
            else:
                chunks.append((chunk, 0))
            continue
        chunks.append((chunk, count))

    if len(chunks) > 1 and chunks[0][1] == 0:
        prefix, _ = chunks.pop(0)
        first, first_count = chunks[0]
        chunks[0] = (prefix + " " + first, first_count)
    return chunks


def asr_cues(
    words: list[tuple[str, float, float]],
    duration: float,
    max_chars: int,
    max_duration: float,
    words_per_cue: int,
    start_pad: float,
    end_pad: float,
) -> tuple[list[str], list[tuple[float, float]]]:
    """Group ASR words into readable cues when no script is supplied."""
    if words_per_cue > 0:
        texts: list[str] = []
        raw: list[tuple[float, float]] = []
        for i in range(0, len(words), words_per_cue):
            group = words[i:i + words_per_cue]
            text = clean_asr_text(" ".join(w[0] for w in group))
            if text:
                texts.append(text)
                raw.append((group[0][1], group[-1][2]))
        if not texts:
            raise SystemExit("ASR produced no words; cannot build subtitles")
        times = make_contiguous(build_cues(raw, duration, start_pad, end_pad))
        return texts, times

    cues: list[tuple[str, float, float]] = []
    current: list[tuple[str, float, float]] = []

    def flush() -> None:
        if not current:
            return
        text = clean_asr_text(" ".join(w[0] for w in current))
        if text:
            cues.append((text, current[0][1], current[-1][2]))
        current.clear()

    for word, start, end in words:
        if not word.strip():
            continue
        candidate = " ".join([w[0] for w in current] + [word])
        too_long = bool(current) and len(candidate) > max_chars
        too_slow = bool(current) and (end - current[0][1]) > max_duration
        if too_long or too_slow:
            flush()
        current.append((word, start, end))
        text = " ".join(w[0] for w in current)
        if SENTENCE_END_RE.search(word) and len(text) >= 20:
            flush()

    flush()
    if not cues:
        raise SystemExit("ASR produced no words; cannot build subtitles")

    raw = [(start, end) for _, start, end in cues]
    times = make_contiguous(build_cues(raw, duration, start_pad, end_pad))
    return [text for text, _, _ in cues], times


def write_vtt(path: Path, cues: list[str], times: list[tuple[float, float]]) -> None:
    blocks = ["WEBVTT", ""]
    for text, (start, end) in zip(cues, times):
        if "-->" in text:
            raise SystemExit(f"cue text must not contain '-->': {text!r}")
        blocks.append(f"{format_timestamp(start)} --> {format_timestamp(end)}")
        blocks.append(text)
        blocks.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(blocks), encoding="utf-8", newline="\n")


def dump_differences(article_tokens, asr_tokens, limit=20) -> None:
    matcher = SequenceMatcher(None, article_tokens, asr_tokens, autojunk=False)
    shown = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        print(
            f"  {tag}: article={article_tokens[i1:i2]!r} "
            f"asr={asr_tokens[j1:j2]!r}",
            file=sys.stderr,
        )
        shown += 1
        if shown >= limit:
            print("  ...", file=sys.stderr)
            break


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "media",
        nargs="?",
        type=Path,
        help="Audio or video file to transcribe",
    )
    parser.add_argument(
        "--audio",
        type=Path,
        help="Deprecated alias for the positional media path",
    )
    parser.add_argument(
        "--cues",
        type=Path,
        help="One cue per line. Omit to use the ASR transcript as subtitle text.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="Output .vtt path, or an existing directory. Default: next to the media file.",
    )
    parser.add_argument(
        "--model",
        default="Systran/faster-whisper-large-v3",
        help="Local model directory or a model id already present in the HF cache",
    )
    parser.add_argument("--language", default=None, help="ISO language code, e.g. en; default: auto")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--compute-type", default="int8")
    parser.add_argument("--cpu-threads", type=int, default=0)
    parser.add_argument("--start-pad", type=float, default=0.05)
    parser.add_argument("--end-pad", type=float, default=0.18)
    parser.add_argument(
        "--words-per-cue",
        type=int,
        default=0,
        help="Split into cues of roughly N words (0 = one cue per line / ASR sentence)",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=84,
        help="Transcript mode: split a cue above this many characters",
    )
    parser.add_argument(
        "--max-duration",
        type=float,
        default=7.0,
        help="Transcript mode: split a cue above this many seconds",
    )
    parser.add_argument(
        "--min-similarity",
        type=float,
        default=0.80,
        help="Script mode: abort without writing if transcript match is below this",
    )
    parser.add_argument("--force", action="store_true", help="Write even if similarity is low")
    parser.add_argument("--vad", action="store_true", help="Enable voice activity detection")
    parser.add_argument(
        "--dump-transcript",
        action="store_true",
        help="Print ASR segments and word timings, then exit without writing VTT",
    )
    args = parser.parse_args()

    if args.media and args.audio:
        parser.error("pass the media path positionally or with --audio, not both")
    media_arg = args.media or args.audio
    if not media_arg:
        parser.error("a media path is required")

    media = resolve_path(media_arg)
    if not media.is_file():
        raise SystemExit(f"media not found: {media}")

    cues: list[str] | None = None
    cues_path: Path | None = None
    if args.cues:
        cues_path = resolve_path(args.cues)
        if not cues_path.is_file():
            raise SystemExit(f"cue file not found: {cues_path}")
        cues = read_cues(cues_path)

    if args.out:
        out = resolve_path(args.out)
        if out.is_dir():
            out = out / f"{media.stem}.vtt"
    else:
        out = media.with_suffix(".vtt")

    article_tokens: list[str] = []
    cue_ranges: list[tuple[int, int]] = []
    article_text = ""
    if cues is not None:
        for cue in cues:
            toks = tokenize(cue)
            if not toks:
                raise SystemExit(f"cue has no tokens: {cue!r}")
            start = len(article_tokens)
            article_tokens.extend(toks)
            cue_ranges.append((start, len(article_tokens)))
        article_text = " ".join(cues)

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print(
            "faster-whisper is not installed in this interpreter.\n"
            "Install it, or run with VoiceStudio's venv:\n"
            "  ~/Library/Application Support/VoiceStudio/runtime/project/.venv/bin/python "
            f"{Path(__file__).name} ...",
            file=sys.stderr,
        )
        return 2

    print(f"loading model offline: {args.model}", file=sys.stderr)
    try:
        model = WhisperModel(
            args.model,
            device=args.device,
            compute_type=args.compute_type,
            cpu_threads=args.cpu_threads,
            local_files_only=True,
        )
    except Exception as exc:  # noqa: BLE001 - surface the cache hint to the user
        print(
            f"could not load the model without downloading: {exc}\n"
            "Pass --model with a local snapshot directory, or pre-populate the HF cache.",
            file=sys.stderr,
        )
        return 2

    print(f"transcribing: {media}", file=sys.stderr)
    segments, info = model.transcribe(
        str(media),
        language=args.language or None,
        task="transcribe",
        beam_size=5,
        temperature=0.0,
        condition_on_previous_text=False,
        word_timestamps=True,
        vad_filter=args.vad,
        initial_prompt=article_text or None,
    )

    raw_words: list[tuple[str, float, float]] = []
    asr_tokens: list[str] = []
    asr_times: list[tuple[float, float]] = []
    segment_rows = []
    for segment in segments:
        words = list(segment.words or [])
        segment_rows.append((segment.start, segment.end, segment.text.strip(), words))
        for word in words:
            raw_words.append((word.word.strip(), word.start, word.end))
            word_tokens = tokenize(word.word)
            for token in word_tokens:
                asr_tokens.append(token)
                asr_times.append((word.start, word.end))

    duration = float(info.duration or 0.0)
    if duration <= 0 and raw_words:
        duration = raw_words[-1][2]
    if duration <= 0:
        raise SystemExit("could not determine media duration")

    if args.dump_transcript:
        for start, end, text, words in segment_rows:
            print(f"[{start:7.3f} --> {end:7.3f}] {text}")
            for word in words:
                print(f"    {word.start:7.3f} --> {word.end:7.3f}  {word.word!r}")
        return 0

    if cues is None:
        raw_words = dedupe_repeats(raw_words)
        cue_texts, cue_times = asr_cues(
            raw_words,
            duration,
            args.max_chars,
            args.max_duration,
            args.words_per_cue,
            args.start_pad,
            args.end_pad,
        )
    else:
        asr_tokens, asr_times = merge_single_letters(asr_tokens, asr_times)
        similarity = SequenceMatcher(
            None, article_tokens, asr_tokens, autojunk=False
        ).ratio()
        print(
            f"token similarity: {similarity:.3f} "
            f"({len(article_tokens)} script tokens, {len(asr_tokens)} ASR tokens)",
            file=sys.stderr,
        )
        if similarity < args.min_similarity:
            print("transcript differs too much from the cue text:", file=sys.stderr)
            dump_differences(article_tokens, asr_tokens)
            if not args.force:
                print("refusing to write VTT (use --force to override)", file=sys.stderr)
                return 2

        aligned = align_times(article_tokens, asr_tokens, asr_times, duration)
        cue_texts = []
        raw_cue_times = []
        for cue, (start, _) in zip(cues, cue_ranges):
            position = start
            for chunk, count in split_cue_words(cue, args.words_per_cue):
                if count <= 0:
                    continue
                chunk_times = aligned[position:position + count]
                if not chunk_times:
                    break
                cue_texts.append(chunk)
                raw_cue_times.append((chunk_times[0][0], chunk_times[-1][1]))
                position += count
        cue_times = make_contiguous(
            build_cues(raw_cue_times, duration, args.start_pad, args.end_pad)
        )

    write_vtt(out, cue_texts, cue_times)

    print(f"wrote {out} ({len(cue_texts)} cues)", file=sys.stderr)
    for i, (text, (start, end)) in enumerate(zip(cue_texts, cue_times), 1):
        print(f"{i:4d}  {start:6.2f} --> {end:6.2f}  {text}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

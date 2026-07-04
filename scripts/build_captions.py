#!/usr/bin/env python3
"""
build_captions.py — deterministic caption builder (P7).

Reads outputs/<slug>/04-scenes-final.json (alignment-based timing only) and
writes three sibling artifacts derived from the SAME cue list:

  05-captions.json  machine-readable cues (captions-file.schema.json, P8)
                    -> consumed by the render layer's "video-captioned" comp
  05-captions.srt   upload to YouTube as a subtitle file
  05-captions.vtt   same cues, WebVTT

Cue rules (all deterministic):
  * scene narration is split on sentence ends, then greedily re-merged while
    a cue stays <= MAX_CUE_CHARS and <= MAX_CUE_SEC (word-proportional time);
  * timing is allocated word-proportionally inside [startTime, endTime];
  * the last cue of a scene may linger up to LEAD_OUT_SEC into the following
    narration gap (readability), never into the next scene;
  * text is wrapped to <= 2 lines of <= MAX_LINE_CHARS.

Usage:
    python scripts/build_captions.py <video-slug>
    python scripts/build_captions.py --self-test

Refuses estimated timing: captions must match the real voiceover, mirroring
the voiced-render guard in render/src/lib/data.ts.
"""
from pathlib import Path
import argparse
import json
import re
import sys

REPO = Path(__file__).resolve().parent.parent
SCHEMA_FILE = REPO / "templates" / "schemas" / "captions-file.schema.json"

ALIGNMENT_MODES = {"forced-alignment", "transcript-guided-alignment"}

MAX_LINE_CHARS = 42   # target chars per rendered line
MAX_LINE_SLACK = 46   # hard cap (schema maxLength) for unbreakable overflow
MAX_CUE_CHARS = 84    # ~2 full lines
MAX_CUE_SEC = 4.0     # split cues longer than this
LEAD_OUT_SEC = 0.4    # linger into a narration gap, at most this much


# --- cue building ------------------------------------------------------------

def _sentences(text: str) -> list[str]:
    """Split narration into sentence-ish chunks, keeping punctuation."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    parts = re.findall(r"[^.!?…]+[.!?…]*\s*", text)
    return [p.strip() for p in parts if p.strip()]


def _chunks_for_scene(narration: str, duration: float) -> list[str]:
    """Sentence chunks greedily merged under the char/second caps."""
    sents = _sentences(narration)
    total_words = sum(len(s.split()) for s in sents) or 1
    sec_per_word = duration / total_words

    def est(words: int) -> float:
        return words * sec_per_word

    merged: list[str] = []
    for s in sents:
        if (
            merged
            and len(merged[-1]) + 1 + len(s) <= MAX_CUE_CHARS
            and est(len((merged[-1] + " " + s).split())) <= MAX_CUE_SEC
        ):
            merged[-1] = merged[-1] + " " + s
        else:
            merged.append(s)

    # halve anything still over the caps (long single sentences)
    out: list[str] = []
    for chunk in merged:
        stack = [chunk]
        while stack:
            c = stack.pop(0)
            words = c.split()
            if len(c) <= MAX_CUE_CHARS and est(len(words)) <= MAX_CUE_SEC:
                out.append(c)
            elif len(words) < 2:
                out.append(c)  # unbreakable; line-wrap may still fail loudly
            else:
                mid = len(words) // 2
                stack = [" ".join(words[:mid]), " ".join(words[mid:])] + stack
    return out


def _wrap_lines(text: str) -> list[str]:
    """<= 2 balanced lines. Raises if a line cannot fit the hard cap."""
    if len(text) <= MAX_LINE_CHARS:
        return [text]
    words = text.split()
    best: list[str] | None = None
    best_diff = None
    for i in range(1, len(words)):
        l1, l2 = " ".join(words[:i]), " ".join(words[i:])
        if len(l1) <= MAX_LINE_SLACK and len(l2) <= MAX_LINE_SLACK:
            diff = abs(len(l1) - len(l2))
            if best is None or diff < best_diff:
                best, best_diff = [l1, l2], diff
    if best is None:
        raise ValueError(f"Cannot wrap into 2 lines of <= {MAX_LINE_SLACK}: {text!r}")
    return best


def build_cues(scenes_data: dict) -> list[dict]:
    """The whole video's cue list from an alignment-timed scenes file."""
    mode = scenes_data.get("timingMode")
    if mode not in ALIGNMENT_MODES:
        raise ValueError(
            f"CAPTIONS BLOCKED: timingMode {mode!r} is not alignment-based. "
            "Re-run align.py Mode A against the real voiceover first."
        )
    audio_duration = float(scenes_data.get("audio", {}).get("duration") or 0)
    scenes = scenes_data["scenes"]

    cues: list[dict] = []
    for i, scene in enumerate(scenes):
        start, end = float(scene["startTime"]), float(scene["endTime"])
        chunks = _chunks_for_scene(scene["narration"], end - start)
        if not chunks:
            continue
        # word-proportional boundaries inside the scene span
        counts = [len(c.split()) for c in chunks]
        total = sum(counts)
        bounds = [start]
        acc = 0
        for n in counts:
            acc += n
            bounds.append(start + (end - start) * acc / total)
        # linger into the gap after the scene (readability)
        next_start = (
            float(scenes[i + 1]["startTime"]) if i + 1 < len(scenes)
            else (audio_duration or bounds[-1])
        )
        bounds[-1] = min(bounds[-1] + LEAD_OUT_SEC, max(next_start, bounds[-1]))

        for j, chunk in enumerate(chunks):
            cues.append({
                "index": len(cues) + 1,
                "sceneNumber": scene["sceneNumber"],
                "startTime": round(bounds[j], 3),
                "endTime": round(bounds[j + 1], 3),
                "lines": _wrap_lines(chunk),
            })
    return cues


# --- SRT / VTT rendering -----------------------------------------------------

def fmt_timestamp(seconds: float, decimal_sep: str) -> str:
    ms = round(seconds * 1000)
    h, rem = divmod(ms, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}{decimal_sep}{ms:03d}"


def to_srt(cues: list[dict]) -> str:
    blocks = []
    for c in cues:
        blocks.append(
            f"{c['index']}\n"
            f"{fmt_timestamp(c['startTime'], ',')} --> {fmt_timestamp(c['endTime'], ',')}\n"
            + "\n".join(c["lines"])
        )
    return "\n\n".join(blocks) + "\n"


def to_vtt(cues: list[dict]) -> str:
    blocks = ["WEBVTT"]
    for c in cues:
        blocks.append(
            f"{fmt_timestamp(c['startTime'], '.')} --> {fmt_timestamp(c['endTime'], '.')}\n"
            + "\n".join(c["lines"])
        )
    return "\n\n".join(blocks) + "\n"


# --- main --------------------------------------------------------------------

def run(slug: str) -> int:
    out_dir = REPO / "outputs" / slug
    src = out_dir / "04-scenes-final.json"
    if not src.exists():
        print(f"ERROR: {src} not found", file=sys.stderr)
        return 1
    scenes_data = json.loads(src.read_text(encoding="utf-8"))

    cues = build_cues(scenes_data)
    captions = {
        "videoSlug": slug,
        "sourceFile": "04-scenes-final.json",
        "timingMode": scenes_data["timingMode"],
        "cues": cues,
    }

    # schema validation (soft dependency, but never silent)
    try:
        import jsonschema
        schema = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
        jsonschema.validate(captions, schema)
        validated = "schema: OK"
    except ImportError:
        validated = "schema: SKIPPED (jsonschema not installed)"

    (out_dir / "05-captions.json").write_text(
        json.dumps(captions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "05-captions.srt").write_text(to_srt(cues), encoding="utf-8")
    (out_dir / "05-captions.vtt").write_text(to_vtt(cues), encoding="utf-8")

    total = cues[-1]["endTime"] if cues else 0
    print(
        f"05-captions.json/.srt/.vtt written: {len(cues)} cues over "
        f"{len(scenes_data['scenes'])} scenes, last cue ends {total:.2f}s | {validated}"
    )
    return 0


# --- self-test ---------------------------------------------------------------

def self_test() -> int:
    checks: list[tuple[str, bool]] = []

    def check(name: str, ok: bool) -> None:
        checks.append((name, ok))
        print(("PASS " if ok else "FAIL ") + name)

    base = {
        "timingMode": "transcript-guided-alignment",
        "audio": {"duration": 30.0},
        "scenes": [
            {"sceneNumber": 1, "narration": "Rome falls. Nobody notices.",
             "startTime": 0.0, "endTime": 4.0},
            {"sceneNumber": 2, "narration":
                "The empire had survived plagues, civil wars, and bad emperors "
                "for centuries before the money finally ran out completely.",
             "startTime": 5.0, "endTime": 12.5},
            {"sceneNumber": 3, "narration": "So what actually broke it?",
             "startTime": 12.5, "endTime": 15.0},
        ],
    }
    cues = build_cues(base)

    check("cues produced", len(cues) >= 4)
    check("indices sequential from 1",
          [c["index"] for c in cues] == list(range(1, len(cues) + 1)))
    mono = all(cues[k]["startTime"] < cues[k]["endTime"] for k in range(len(cues)))
    check("every cue start < end", mono)
    overlap = all(cues[k]["endTime"] <= cues[k + 1]["startTime"] + 1e-9
                  for k in range(len(cues) - 1))
    check("no overlapping cues", overlap)
    check("line length caps",
          all(len(line) <= MAX_LINE_SLACK for c in cues for line in c["lines"]))
    check("max two lines per cue", all(len(c["lines"]) <= 2 for c in cues))

    s1 = [c for c in cues if c["sceneNumber"] == 1]
    check("scene 1 single cue", len(s1) == 1)
    check("scene 1 starts at scene start", s1[0]["startTime"] == 0.0)
    check("scene 1 lead-out into gap (4.0 -> 4.4)",
          abs(s1[0]["endTime"] - 4.4) < 1e-9)

    s2 = [c for c in cues if c["sceneNumber"] == 2]
    check("long scene split into multiple cues", len(s2) >= 2)
    check("split cues within scene span",
          s2[0]["startTime"] == 5.0 and s2[-1]["endTime"] <= 12.5 + 1e-9)
    check("no lead-out into an adjacent scene (gap=0)",
          s2[-1]["endTime"] <= 12.5 + 1e-9)

    s3 = [c for c in cues if c["sceneNumber"] == 3]
    check("last scene lead-out capped by audio duration",
          s3[-1]["endTime"] <= 30.0)

    check("timestamp SRT format", fmt_timestamp(3661.5, ",") == "01:01:01,500")
    check("timestamp VTT format", fmt_timestamp(0.041, ".") == "00:00:00.041")
    srt = to_srt(cues)
    check("SRT block numbering", srt.startswith("1\n00:00:00,000 --> "))
    check("VTT header", to_vtt(cues).startswith("WEBVTT\n\n"))

    try:
        build_cues({**base, "timingMode": "word-count-estimate"})
        check("guard: estimated timing refused", False)
    except ValueError:
        check("guard: estimated timing refused", True)

    balanced = _wrap_lines(
        "a fairly long single sentence that must wrap into two lines cleanly"
    )
    check("wrap balances two lines",
          len(balanced) == 2 and all(len(x) <= MAX_LINE_SLACK for x in balanced))

    try:
        import jsonschema
        schema = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
        jsonschema.validate(
            {"videoSlug": "x-y", "sourceFile": "04-scenes-final.json",
             "timingMode": base["timingMode"], "cues": cues},
            schema,
        )
        check("schema validation of self-test cues", True)
    except ImportError:
        print("NOTE schema check skipped (jsonschema not installed)")

    failed = [n for n, ok in checks if not ok]
    print(f"\nself-test: {len(checks) - len(failed)}/{len(checks)} PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slug", nargs="?", help="video slug under outputs/")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        sys.exit(self_test())
    if not args.slug:
        ap.error("slug required (or --self-test)")
    sys.exit(run(args.slug))

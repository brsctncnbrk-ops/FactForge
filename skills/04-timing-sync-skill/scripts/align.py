#!/usr/bin/env python3
"""align.py — replace estimated scene durations with real ones (P1 executor).

Modes (auto-selected, --mode can force one; patch Section 7):
  A  transcript-guided-alignment  audio + faster-whisper (CTranslate2, no
     torch; default model "base", compute_type "int8" — fits 4GB RAM; the
     transcript is known, whisper only anchors word timestamps)
     -> 04-scenes-final.json
  B  proportional-estimate        audio exists, A unavailable/failed:
     ffprobe duration, word-proportional distribution normalized to the
     real audio length -> 04-scenes-final-estimated.json
  C  word-count-estimate          no audio: duration = wordCount / 2.5
     -> 04-scenes-final-estimated.json

Confidence (Mode A): reference = 02-script-voiceover.txt paragraphs (one per
scene, ascending scene order); transcript and reference words are normalized
and globally aligned (rapidfuzz if importable, stdlib difflib otherwise —
never torch tools). Scene confidence = matched scene words / scene words.
Mode A succeeds only if global coverage >= 0.90 AND every scene >= 0.60;
otherwise it refuses to write 04-scenes-final.json and falls back to Mode B.
(quality-gate.py: confidence < 0.80 WARN, < 0.60 FAIL.)

Hard rules: 04-scenes-final-estimated.json is NEVER a voiced-final-render
input; durations are never clamped (warnings instead); inter-scene breathing
buffer is parametric (--buffer, 0.2-0.4s). Sanity warnings in all modes:
scene > 12s LONG SCENE, < 2s SHORT SCENE, total-vs-150wpm deviation report.

This script never edits STATUS.md (the QG block belongs to quality-gate.py);
fallback/user-action messages go to stdout for the session log.

Exit codes: 0 ok (warnings allowed), 2 fail closed (missing/inconsistent
inputs, forced mode unavailable). Usage:
    python align.py /outputs/{video-slug} [--mode auto|transcript|proportional|wordcount]
                    [--model base] [--buffer 0.3]
    python align.py --self-test
"""

import argparse
import copy
import difflib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

GLOBAL_MIN_COVERAGE = 0.90
SCENE_MIN_COVERAGE = 0.60
WORDS_PER_SECOND = 2.5
LONG_SCENE_S = 12.0
SHORT_SCENE_S = 2.0
DEFAULT_BUFFER = 0.3
DEFAULT_MODEL = "base"

MODE_A = "transcript-guided-alignment"
MODE_B = "proportional-estimate"
MODE_C = "word-count-estimate"


class SetupError(Exception):
    """Missing/inconsistent inputs — fail closed (exit 2)."""


class AlignmentQualityError(Exception):
    """Coverage below thresholds — Mode A result must not be trusted."""


_ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven",
         "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen",
         "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
_TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy",
         "eighty", "ninety"]


def _int_to_words(n):
    """Deterministic English word tokens for 0 <= n < 10**9."""
    if n < 20:
        return [_ONES[n]]
    if n < 100:
        tens, rest = divmod(n, 10)
        return [_TENS[tens]] + (_int_to_words(rest) if rest else [])
    for scale, name in ((10 ** 6, "million"), (10 ** 3, "thousand"),
                        (100, "hundred")):
        if n >= scale:
            head, rest = divmod(n, scale)
            return (_int_to_words(head) + [name]
                    + (_int_to_words(rest) if rest else []))
    return [str(n)]  # unreachable for n < 10**9


def normalize_words(text):
    """Lowercase tokens with digits expanded to English words.

    ASR output writes numbers as digits ("400,000", "90") while scripts spell
    them out ("four hundred thousand", "ninety"); expanding digit tokens on
    BOTH sides makes matching representation-invariant without touching the
    coverage thresholds. Digit groups of exactly three ("400" "000" from
    "400,000") are re-joined before conversion; mixed tokens ("270s") are
    left untouched.
    """
    tokens = re.findall(r"[a-z0-9']+", text.lower())
    out, i = [], 0
    while i < len(tokens):
        tok = tokens[i]
        if not tok.isdigit():
            out.append(tok)
            i += 1
            continue
        j = i + 1
        while (j < len(tokens) and tokens[j].isdigit()
               and len(tokens[j]) == 3 and len(tok) <= 3):
            j += 1
        value = int("".join(tokens[i:j]))
        if value < 10 ** 9:
            out.extend(_int_to_words(value))
        else:
            out.extend(tokens[i:j])
        i = j
    return out


def matching_pairs(ref, hyp):
    """(ref_index, hyp_index) pairs of equal words after global alignment."""
    try:
        from rapidfuzz.distance import Levenshtein
        opcodes = Levenshtein.opcodes(ref, hyp)
        blocks = [
            (op.src_start, op.dest_start, op.src_end - op.src_start)
            for op in opcodes
            if op.tag == "equal"
        ]
    except Exception:
        sm = difflib.SequenceMatcher(None, ref, hyp, autojunk=False)
        blocks = [(b.a, b.b, b.size) for b in sm.get_matching_blocks()]
    return [
        (a + k, b + k)
        for a, b, size in blocks
        for k in range(size)
    ]


def scene_spans(paragraphs):
    """Per-paragraph (start, end) index ranges in the concatenated word list."""
    spans, words, pos = [], [], 0
    for p in paragraphs:
        w = normalize_words(p)
        spans.append((pos, pos + len(w)))
        words.extend(w)
        pos += len(w)
    return spans, words


def compute_alignment_timings(paragraphs, hyp_words, audio_duration, buffer_s):
    """Mode A core. hyp_words: [{"word","start","end"}, ...] in time order.

    Returns (timings, global_coverage): timings is a list (one per paragraph)
    of {"startTime","endTime","duration","confidence"}. Raises
    AlignmentQualityError below thresholds.
    """
    spans, ref = scene_spans(paragraphs)
    hyp_norm = []
    hyp_flat = []  # (start, end) per normalized hyp token
    for w in hyp_words:
        for token in normalize_words(w["word"]):
            hyp_norm.append(token)
            hyp_flat.append((float(w["start"]), float(w["end"])))
    pairs = matching_pairs(ref, hyp_norm)
    by_ref = dict(pairs)

    coverages, bounds = [], []
    for a, b in spans:
        matched = [by_ref[i] for i in range(a, b) if i in by_ref]
        coverage = len(matched) / (b - a) if b > a else 0.0
        coverages.append(coverage)
        bounds.append(
            (hyp_flat[matched[0]][0], hyp_flat[matched[-1]][1])
            if matched else None
        )
    global_coverage = len(pairs) / len(ref) if ref else 0.0
    if global_coverage < GLOBAL_MIN_COVERAGE or min(coverages) < SCENE_MIN_COVERAGE:
        raise AlignmentQualityError(
            f"coverage too low (global {global_coverage:.2f}, "
            f"min scene {min(coverages):.2f}; need >= {GLOBAL_MIN_COVERAGE} "
            f"global and >= {SCENE_MIN_COVERAGE} per scene)"
        )

    starts = []
    for i, b in enumerate(bounds):
        starts.append(0.0 if i == 0 else b[0])
    timings = []
    for i, (start, cov) in enumerate(zip(starts, coverages)):
        if i + 1 < len(bounds):
            end = min(bounds[i][1] + buffer_s, starts[i + 1])
        else:
            end = audio_duration
        end = max(end, start + 0.01)
        timings.append({
            "startTime": round(start, 3),
            "endTime": round(end, 3),
            "duration": round(end - start, 3),
            "confidence": round(cov, 3),
        })
    return timings, global_coverage


def word_counts(paragraphs):
    return [len(p.split()) for p in paragraphs]


def compute_proportional_timings(paragraphs, audio_duration):
    """Mode B: word-proportional, normalized to the real audio duration."""
    counts = word_counts(paragraphs)
    total = sum(counts)
    if total == 0:
        raise SetupError("no narration words — cannot distribute duration")
    timings, t = [], 0.0
    for i, c in enumerate(counts):
        end = audio_duration if i == len(counts) - 1 else t + audio_duration * c / total
        timings.append({
            "startTime": round(t, 3),
            "endTime": round(end, 3),
            "duration": round(end - t, 3),
        })
        t = end
    return timings


def compute_wordcount_timings(paragraphs):
    """Mode C: pure 150 wpm estimate (duration = words / 2.5)."""
    timings, t = [], 0.0
    for c in word_counts(paragraphs):
        end = t + c / WORDS_PER_SECOND
        timings.append({
            "startTime": round(t, 3),
            "endTime": round(end, 3),
            "duration": round(end - t, 3),
        })
        t = end
    return timings


def sanity_warnings(timings, paragraphs):
    warnings = []
    total = timings[-1]["endTime"] if timings else 0.0
    for t, p in zip(timings, paragraphs):
        n = t["duration"]
        label = f"scene at {t['startTime']}s ({p.split()[0]}...)" if p else "scene"
        if n > LONG_SCENE_S:
            warnings.append(f"LONG SCENE: {label} runs {n}s (> {LONG_SCENE_S}s) — split candidate")
        if n < SHORT_SCENE_S:
            warnings.append(f"SHORT SCENE: {label} runs {n}s (< {SHORT_SCENE_S}s) — merge candidate")
    wpm_estimate = sum(word_counts(paragraphs)) / WORDS_PER_SECOND
    if wpm_estimate > 0:
        dev = (total - wpm_estimate) / wpm_estimate * 100
        warnings.append(
            f"REPORT: total {round(total, 1)}s vs 150wpm estimate "
            f"{round(wpm_estimate, 1)}s ({dev:+.0f}%)"
        ) if abs(dev) > 15 else None
    return warnings


def repo_rel(path, root):
    try:
        return "/" + Path(path).resolve().relative_to(Path(root).resolve()).as_posix()
    except ValueError:
        return Path(path).resolve().as_posix()


def build_output(doc, timings, timing_mode, audio_block):
    out = copy.deepcopy(doc)
    out["timingMode"] = timing_mode
    out["audio"] = audio_block
    for scene, t in zip(sorted(out["scenes"], key=lambda s: s["sceneNumber"]), timings):
        scene.update(t)
        scene["estimatedDuration"] = t["duration"]
    return out


def probe_audio(audio_path):
    """(duration_s, sample_rate) via ffprobe, or None if unavailable."""
    try:
        raw = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration:stream=sample_rate", "-of", "json", str(audio_path)],
            capture_output=True, text=True, timeout=60,
        )
        info = json.loads(raw.stdout)
        duration = float(info["format"]["duration"])
        rates = [int(s["sample_rate"]) for s in info.get("streams", [])
                 if s.get("sample_rate")]
        return duration, (rates[0] if rates else 44100)
    except Exception:
        return None


def transcribe_words(audio_path, model_size):
    """faster-whisper word timestamps: ([{word,start,end}], audio_duration)."""
    from faster_whisper import WhisperModel  # optional dependency (Mode A)
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        str(audio_path), word_timestamps=True, language="en"
    )
    words = [
        {"word": w.word, "start": w.start, "end": w.end}
        for seg in segments
        for w in (seg.words or [])
    ]
    return words, float(info.duration)


def load_inputs(out_dir):
    scenes_path = out_dir / "03-scenes.json"
    vo_path = out_dir / "02-script-voiceover.txt"
    if not scenes_path.is_file():
        raise SetupError(f"{scenes_path} not found")
    if not vo_path.is_file():
        raise SetupError(f"{vo_path} not found (alignment reference text)")
    try:
        doc = json.loads(scenes_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise SetupError(f"03-scenes.json is not valid JSON: {e}")
    scenes = sorted(doc.get("scenes") or [], key=lambda s: s.get("sceneNumber", 0))
    paragraphs = [p for p in vo_path.read_text(encoding="utf-8").split("\n\n") if p.strip()]
    paragraphs = [" ".join(p.split()) for p in paragraphs]
    if len(paragraphs) != len(scenes):
        raise SetupError(
            f"VO has {len(paragraphs)} paragraphs but 03-scenes.json has "
            f"{len(scenes)} scenes — re-run derive_vo.py / fix inputs first"
        )
    return doc, paragraphs


def run(target, mode, model_size, buffer_s):
    out_dir = Path(target)
    if out_dir.suffix == ".json":
        out_dir = out_dir.parent
    if not out_dir.is_dir():
        raise SetupError(f"output folder not found: {out_dir}")
    root = _find_root(out_dir)
    doc, paragraphs = load_inputs(out_dir)
    audio_path = out_dir / "audio" / "voiceover.mp3"
    vo_rel = repo_rel(out_dir / "02-script-voiceover.txt", root)
    audio_rel = repo_rel(audio_path, root)
    notes = []

    def audio_block(duration, sample_rate, source, tool, warning=None):
        block = {
            "file": audio_rel,
            "duration": round(duration, 3),
            "sampleRate": sample_rate,
            "timingSource": source,
            "alignmentTool": tool,
            "transcriptFile": vo_rel,
        }
        if warning:
            block["warning"] = warning
        return block

    chosen, timings, out_doc = None, None, None

    if mode in ("auto", "transcript"):
        if not audio_path.is_file():
            if mode == "transcript":
                raise SetupError(f"audio file missing: {audio_path}")
            notes.append(f"no audio at {audio_rel} -> word-count-estimate mode")
        else:
            try:
                hyp_words, wav_duration = transcribe_words(audio_path, model_size)
                probed = probe_audio(audio_path)
                duration = probed[0] if probed else wav_duration
                sample_rate = probed[1] if probed else 44100
                timings, coverage = compute_alignment_timings(
                    paragraphs, hyp_words, duration, buffer_s)
                chosen = MODE_A
                out_doc = build_output(doc, timings, MODE_A, audio_block(
                    duration, sample_rate, MODE_A, "faster-whisper"))
                notes.append(f"alignment coverage: {coverage:.3f}")
            except ImportError:
                msg = ("faster-whisper not installed — USER ACTION: pip install "
                       "faster-whisper, then re-run align.py")
                if mode == "transcript":
                    raise SetupError(msg)
                notes.append(msg + " (falling back to proportional-estimate)")
            except AlignmentQualityError as e:
                msg = (f"alignment rejected: {e} — USER ACTION: check that "
                       f"{audio_rel} matches the script, then re-run align.py")
                if mode == "transcript":
                    raise SetupError(msg)
                notes.append(msg + " (falling back to proportional-estimate)")

    if chosen is None and mode in ("auto", "proportional") and audio_path.is_file():
        probed = probe_audio(audio_path)
        if probed is None:
            msg = "ffprobe unavailable/failed — cannot measure audio duration"
            if mode == "proportional":
                raise SetupError(msg)
            notes.append(msg + " (falling back to word-count-estimate)")
        else:
            duration, sample_rate = probed
            timings = compute_proportional_timings(paragraphs, duration)
            chosen = MODE_B
            out_doc = build_output(doc, timings, MODE_B, audio_block(
                duration, sample_rate, MODE_B, None,
                "estimated timing (word-proportional, normalized to audio) — "
                "NOT valid for voiced final render"))
    elif chosen is None and mode == "proportional":
        raise SetupError(f"audio file missing: {audio_path}")

    if chosen is None:
        timings = compute_wordcount_timings(paragraphs)
        chosen = MODE_C
        out_doc = build_output(doc, timings, MODE_C, audio_block(
            timings[-1]["endTime"] if timings else 0.0, 44100, MODE_C, None,
            "no audio file — durations are pure 150wpm estimates; NOT valid "
            "for voiced final render"))

    out_name = ("04-scenes-final.json" if chosen == MODE_A
                else "04-scenes-final-estimated.json")
    out_path = out_dir / out_name
    out_path.write_text(json.dumps(out_doc, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8", newline="\n")

    print(f"Mode: {chosen}")
    print(f"Wrote {out_path}")
    scenes = sorted(out_doc["scenes"], key=lambda s: s["sceneNumber"])
    for s in scenes:
        conf = f"  conf {s['confidence']:.2f}" if "confidence" in s else ""
        print(f"Scene {s['sceneNumber']}: {s['startTime']:.2f} -> "
              f"{s['endTime']:.2f}  ({s['duration']:.2f}s){conf}")
    for w in sanity_warnings(
            [{k: s[k] for k in ("startTime", "endTime", "duration")} for s in scenes],
            paragraphs):
        print(f"WARNING: {w}")
    for n in notes:
        print(f"NOTE: {n}")
    if chosen != MODE_A:
        print("NOTE: estimated output — draft/silent preview only; voiced final "
              "render requires transcript-guided alignment (Mode A).")
    return 0


def _find_root(start):
    for p in [start] + list(start.parents):
        if (p / "templates" / "schemas" / "scenes-file.schema.json").is_file():
            return p
    return start


# --- self-test ---------------------------------------------------------------

PARAGRAPHS = [
    "Rome did not fall in a single night.",
    "For three hundred years something inside the empire had been quietly "
    "breaking while its rulers kept spending money they did not have.",
    "This is that story.",
]


def _scene(n, narration, template="text-emphasis"):
    return {
        "sceneNumber": n,
        "narration": narration,
        "wordCount": len(narration.split()),
        "estimatedDuration": len(narration.split()) / WORDS_PER_SECOND,
        "template": template,
        "props": {"text": "SAMPLE"},
        "assets": {"fromLibrary": [], "newAssets": []},
    }


def _doc():
    return {
        "videoSlug": "sample-video",
        "fps": 30,
        "resolution": "1920x1080",
        "scenes": [_scene(i + 1, p) for i, p in enumerate(PARAGRAPHS)],
    }


def _synthetic_hyp(paragraphs, step=0.4):
    words, t = [], 0.0
    for p in paragraphs:
        for w in normalize_words(p):
            words.append({"word": w, "start": round(t, 3), "end": round(t + step * 0.8, 3)})
            t += step
        t += 0.5  # inter-scene silence
    return words, round(t, 3)


def self_test():
    failures = []

    def check(name, cond):
        print(f"  {'PASS' if cond else 'FAIL'}  {name}")
        if not cond:
            failures.append(name)

    # Mode A core on synthetic word timestamps — full match
    hyp, total = _synthetic_hyp(PARAGRAPHS)
    timings, coverage = compute_alignment_timings(PARAGRAPHS, hyp, total, DEFAULT_BUFFER)
    check("full match -> global coverage 1.0", coverage == 1.0)
    check("all scene confidences 1.0", all(t["confidence"] == 1.0 for t in timings))
    check("scene 1 starts at 0.0", timings[0]["startTime"] == 0.0)
    check("last scene ends at audio duration", timings[-1]["endTime"] == total)
    starts = [t["startTime"] for t in timings]
    ends = [t["endTime"] for t in timings]
    check("timeline monotonic, no overlap",
          all(e <= s for e, s in zip(ends, starts[1:]))
          and all(e > s for s, e in zip(starts, ends)))
    check("buffer applied but clamped to next scene start",
          all(ends[i] <= starts[i + 1] for i in range(len(ends) - 1)))
    t2, c2 = compute_alignment_timings(PARAGRAPHS, hyp, total, DEFAULT_BUFFER)
    check("deterministic", (t2, c2) == (timings, coverage))

    # digit-vs-spelled-number robustness (ASR writes "400,000"/"90", script
    # spells them out) — expansion is symmetric, thresholds untouched
    check("digit tokens expand to spelled words",
          normalize_words("between 400,000 and 600,000 men")
          == ["between", "four", "hundred", "thousand", "and",
              "six", "hundred", "thousand", "men"])
    check("plain digits expand (90 -> ninety, 1453 -> words)",
          normalize_words("90") == ["ninety"]
          and normalize_words("1453") == ["one", "thousand",
                                          "four", "hundred", "fifty", "three"])
    check("mixed tokens like '270s' stay untouched",
          normalize_words("the 270s") == ["the", "270s"])
    num_ref = ["The army had four hundred thousand men.",
               "The coin was ninety percent silver."]
    hyp_n, tot_n = _synthetic_hyp(["The army had 400,000 men.",
                                   "The coin was 90 percent silver."])
    _, cov_n = compute_alignment_timings(num_ref, hyp_n, tot_n, DEFAULT_BUFFER)
    check("digit transcript matches spelled-out reference -> coverage 1.0",
          cov_n == 1.0)

    # degraded transcript -> quality error (scene 3 fully corrupted)
    bad = [dict(w) for w in hyp]
    n3 = len(normalize_words(PARAGRAPHS[2]))
    for w in bad[-n3:]:
        w["word"] = "zzz"
    try:
        compute_alignment_timings(PARAGRAPHS, bad, total, DEFAULT_BUFFER)
        check("corrupted scene -> AlignmentQualityError", False)
    except AlignmentQualityError:
        check("corrupted scene -> AlignmentQualityError", True)

    # Mode B — normalized to real audio duration
    timings = compute_proportional_timings(PARAGRAPHS, 100.0)
    check("mode B: last end == audio duration", timings[-1]["endTime"] == 100.0)
    counts = word_counts(PARAGRAPHS)
    check("mode B: proportional to word counts",
          abs(timings[0]["duration"] / 100.0 - counts[0] / sum(counts)) < 0.001)
    check("mode B: LONG SCENE warned",
          any("LONG SCENE" in w for w in sanity_warnings(timings, PARAGRAPHS)))

    # Mode C — pure 150 wpm
    timings = compute_wordcount_timings(PARAGRAPHS)
    check("mode C: duration = words / 2.5",
          timings[0]["duration"] == counts[0] / WORDS_PER_SECOND)
    check("mode C: SHORT SCENE warned (4-word scene)",
          any("SHORT SCENE" in w for w in sanity_warnings(timings, PARAGRAPHS)))

    # outputs validate against the real scenes-file schema
    try:
        import jsonschema
        schema = json.loads(
            (_find_root(Path(__file__).resolve().parent) / "templates" / "schemas"
             / "scenes-file.schema.json").read_text(encoding="utf-8"))
        hyp, total = _synthetic_hyp(PARAGRAPHS)
        a_t, _ = compute_alignment_timings(PARAGRAPHS, hyp, total, DEFAULT_BUFFER)
        audio = {"file": "/x/audio/voiceover.mp3", "duration": total,
                 "sampleRate": 44100, "timingSource": MODE_A,
                 "alignmentTool": "faster-whisper", "transcriptFile": "/x/vo.txt"}
        doc_a = build_output(_doc(), a_t, MODE_A, audio)
        errs_a = list(jsonschema.Draft7Validator(schema).iter_errors(doc_a))
        audio_c = dict(audio, timingSource=MODE_C, alignmentTool=None,
                       warning="no audio")
        doc_c = build_output(_doc(), compute_wordcount_timings(PARAGRAPHS),
                             MODE_C, audio_c)
        doc_c["timingMode"] = MODE_C
        errs_c = list(jsonschema.Draft7Validator(schema).iter_errors(doc_c))
        check("mode A output schema-valid (incl. confidence)", errs_a == [])
        check("mode C output schema-valid (alignmentTool null + warning)",
              errs_c == [])
        check("confidence only in mode A output",
              all("confidence" in s for s in doc_a["scenes"])
              and all("confidence" not in s for s in doc_c["scenes"]))
    except ImportError:
        check("jsonschema available for output validation", False)

    # fail-closed: VO paragraphs vs scene count mismatch
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        (out / "03-scenes.json").write_text(json.dumps(_doc()), encoding="utf-8")
        (out / "02-script-voiceover.txt").write_text(
            "only one paragraph here\n", encoding="utf-8")
        try:
            load_inputs(out)
            check("VO/scene count mismatch -> SetupError", False)
        except SetupError:
            check("VO/scene count mismatch -> SetupError", True)

    print()
    if failures:
        print(f"SELF-TEST: {len(failures)} FAILURE(S): {failures}")
        return 1
    print("SELF-TEST: ALL CHECKS PASSED")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("target", nargs="?",
                    help="video output folder (or its 03-scenes.json)")
    ap.add_argument("--mode", default="auto",
                    choices=["auto", "transcript", "proportional", "wordcount"])
    ap.add_argument("--model", default=DEFAULT_MODEL,
                    help="faster-whisper model size (default: base; use tiny "
                         "if RAM is tight)")
    ap.add_argument("--buffer", type=float, default=DEFAULT_BUFFER,
                    help="inter-scene breathing buffer in seconds (0.2-0.4)")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        sys.exit(self_test())
    if not args.target:
        ap.error("target folder required (or use --self-test)")
    if not 0.2 <= args.buffer <= 0.4:
        print(f"WARNING: --buffer {args.buffer} outside the 0.2-0.4 range")
    try:
        sys.exit(run(args.target, args.mode, args.model, args.buffer))
    except SetupError as e:
        print(f"SETUP ERROR: {e}", file=sys.stderr)
        print("No output written (fail closed).", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()

---
name: 04-timing-sync-skill
description: Use this skill when the user has dropped an ElevenLabs voiceover (audio/voiceover.mp3) and wants real scene timings, or asks to run alignment, fix timing, produce 04-scenes-final.json / 04-scenes-final-estimated.json, or preview timings without audio. It runs scripts/align.py (transcript-guided alignment via faster-whisper, with proportional-estimate and word-count-estimate fallbacks) and never invents durations by hand (P1/P7).
---

# 04-timing-sync-skill

Turn the estimated durations in `03-scenes.json` into real ones from the voiceover audio. Audio is the master clock (P1). All timing work is deterministic script work (P7) — this skill runs `align.py` and interprets its report; it NEVER hand-writes or hand-adjusts timestamps.

## Inputs

```text
/outputs/{video-slug}/audio/voiceover.mp3      (user drops manually)
/outputs/{video-slug}/03-scenes.json           (validate.py must pass first)
/outputs/{video-slug}/02-script-voiceover.txt  (alignment reference text)
```

## Run

```text
python skills/04-timing-sync-skill/scripts/align.py /outputs/{video-slug} [--mode auto] [--model base] [--buffer 0.3]
```

Auto mode picks the best available path and falls back gracefully; forced modes (`--mode transcript|proportional|wordcount`) fail closed instead of falling back. Read `references/timing-modes-and-fallbacks.md` for the mode table and thresholds; read `references/alignment-troubleshooting.md` when Mode A is unavailable or rejects the audio.

## The three modes (patch Section 7)

1. **transcript-guided-alignment** (target): faster-whisper (`base` int8, `--model tiny` if RAM is tight; no torch) produces word timestamps; words are fuzzy-matched back to the VO text (rapidfuzz if installed, stdlib difflib otherwise); per-scene confidence recorded → **`04-scenes-final.json`** — the ONLY valid voiced-final-render input.
2. **proportional-estimate** (audio exists, alignment unavailable/rejected): ffprobe duration, word-proportional distribution normalized to real audio length → `04-scenes-final-estimated.json`.
3. **word-count-estimate** (no audio): `duration = wordCount / 2.5` → `04-scenes-final-estimated.json`.

**Hard rule:** `04-scenes-final-estimated.json` is never a voiced-final-render input, regardless of how it was produced (quality-gate.py FAILs it). No duration clamping — out-of-range scenes get warnings, not silent fixes.

## Confidence thresholds

align.py accepts Mode A output only if global word coverage ≥ 0.90 AND every scene ≥ 0.60; below that it refuses the file and falls back to Mode B with a user-action note. quality-gate.py then: scene confidence < 0.80 → WARN, < 0.60 → FAIL.

## Sanity checks (all modes, from align.py output)

Scene > 12 s → LONG SCENE (split candidate, back to 02); scene < 2 s → SHORT SCENE (merge candidate); total-vs-150wpm deviation report; (Mode A) last scene pinned to real audio duration.

## After running

- Record align.py's warnings and any USER ACTION notes in STATUS.md under **Warnings / Required User Action** (never touch the QG block — that belongs to quality-gate.py).
- LONG/SHORT scene warnings that need script changes go back to 02-script-skill as targeted scene edits, then 03 → validate.py → re-run align.py.
- Never edit the produced 04 file by hand; fix inputs and re-run.

## Quality criteria

- Mode A: every scene duration comes from alignment output, none estimated; audio metadata block present (`alignmentTool: "faster-whisper"`).
- Mode B: total duration exactly matches the audio duration.
- Fallback modes: `alignmentTool: null` + `warning` field present.
- Warning report produced and acted on (or consciously deferred in STATUS.md).

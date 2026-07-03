# Timing Modes & Fallbacks

Authoritative behavior lives in `scripts/align.py` (its docstring is the contract); this file explains the decisions.

## Mode table

| | A — transcript-guided-alignment | B — proportional-estimate | C — word-count-estimate |
|---|---|---|---|
| Needs | audio + faster-whisper | audio + ffprobe | nothing |
| Output file | `04-scenes-final.json` | `04-scenes-final-estimated.json` | `04-scenes-final-estimated.json` |
| timingMode / timingSource | `transcript-guided-alignment` | `proportional-estimate` | `word-count-estimate` |
| alignmentTool | `"faster-whisper"` | `null` + `warning` | `null` + `warning` |
| Durations | real word timestamps | word-proportional, normalized to real audio length (no cumulative drift) | `wordCount / 2.5` (150 wpm) |
| Per-scene `confidence` | yes (0–1) | no | no |
| Voiced final render | **the only valid input** | never | never |
| Use for | final render | draft/preview render | silent preview |

## Tool choice (patch Section 7)

faster-whisper: CTranslate2 backend, **no torch**, `compute_type="int8"` — `base` model ≈150 MB, `tiny` ≈75 MB; peak RAM well under 1 GB, comfortable on the 4 GB machine. The exact narration text already exists (P4), so whisper is not trusted for transcription — only for anchoring word timestamps. torch-dependent tools (whisperX etc.) are excluded. The `forced-alignment` enum value stays reserved for a true forced aligner; align.py honestly reports `transcript-guided-alignment`.

## Alignment mechanics

1. Reference = `02-script-voiceover.txt` paragraphs (one per scene, ascending scene order; count must equal scene count or align.py exits 2).
2. Both word streams normalized (lowercase, punctuation stripped) and globally aligned — rapidfuzz if importable, stdlib difflib otherwise (identical semantics).
3. Scene start = its first matched word's timestamp (scene 1 pinned to 0.0); scene end = last matched word's end + buffer (`--buffer`, default 0.3 s, range 0.2–0.4), clamped to the next scene's start; last scene pinned to audio duration. Timeline is continuous and non-overlapping.
4. **Scene confidence = matched scene words / scene words.**

## Thresholds (concrete, non-negotiable)

```text
align.py accepts Mode A only if:  global coverage >= 0.90  AND  min scene >= 0.60
quality-gate.py (alignment mode): confidence < 0.80 -> WARN, < 0.60 -> FAIL
```

Rationale: ElevenLabs reads the VO text verbatim, so healthy coverage is ≈1.0; the margins absorb whisper fumbling proper nouns. Coverage far below 1.0 almost always means wrong audio file, missing sentences, or a stale VO file — not a tuning problem.

## Fallback ladder (auto mode)

```text
audio + faster-whisper OK ──> Mode A ──(coverage too low / import error)──> Mode B
audio, no ffprobe ──────────> Mode C (with note)
no audio ───────────────────> Mode C
```

Every fallback prints an explicit `USER ACTION` line (install command / file check / retry command) — copy it into STATUS.md → Required User Action.

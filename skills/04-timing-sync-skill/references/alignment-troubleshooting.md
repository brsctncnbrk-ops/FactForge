# Alignment Troubleshooting

Work top-down; after each fix re-run:
`python skills/04-timing-sync-skill/scripts/align.py /outputs/{video-slug} --mode transcript`
(forced mode, so a silent fallback cannot mask the problem).

## "faster-whisper not installed"

```text
C:\Users\brsct\AppData\Local\Programs\Python\Python314\python.exe -m pip install faster-whisper
```

(PATH `python` is broken on this machine — always use the full interpreter path.) First run downloads the model (~150 MB for `base`) to the HuggingFace cache; needs network once. If RAM is tight, add `--model tiny`.

## "alignment rejected: coverage too low"

In likelihood order:

1. **Wrong audio file** — a different script's voiceover in `audio/voiceover.mp3`. Listen to the first 10 seconds.
2. **Stale VO text** — script edited after the audio was generated. Re-run derive_vo.py; if the VO text changes, the audio must be regenerated in ElevenLabs.
3. **Missing/duplicated sentences in audio** — ElevenLabs skipped or repeated a block. Regenerate the audio.
4. **Heavy proper-noun text** — coverage slightly under 0.90 with all scenes matching well. Acceptable fix: none automatic; regenerate audio with clearer pronunciation, or accept Mode B for a draft while investigating. Never lower the thresholds in code.

## "ffprobe unavailable" (Mode B blocked)

ffprobe ships with ffmpeg: `winget install Gyan.FFmpeg`, then reopen the terminal. Only affects Mode B; Modes A and C don't need it.

## Low per-scene confidence in an otherwise good run

quality-gate.py WARNs at < 0.80 and FAILs at < 0.60 per scene. Check that scene's narration for numerals, abbreviations, or names whisper may render differently ("476 AD" vs "four seventy six a d"). The normalization absorbs case/punctuation but not spelled-out numbers — prefer writing numbers as words in narration (also better for ElevenLabs).

## Sanity warnings

- `LONG SCENE` (> 12 s): split the scene in 02-script-annotated.md (targeted edit), re-derive VO, re-map in 03, re-validate, re-align. Requires regenerating audio only if narration text changed.
- `SHORT SCENE` (< 2 s): merge candidate — same loop.
- Total-vs-150wpm deviation beyond ±15%: the voice is much faster/slower than planned; word budgets for future scripts should adapt, but do NOT rescale timings by hand — the audio is the master clock.

## What never to do

- Never hand-edit `04-scenes-final*.json` timestamps.
- Never rename an estimated file to `04-scenes-final.json` to get past the gate.
- Never weaken the coverage/confidence thresholds to make a run pass.

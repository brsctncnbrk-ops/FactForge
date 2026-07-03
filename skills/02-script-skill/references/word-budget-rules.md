# 02-script-skill — Word Budget Rules

## The numbers (binding)

```text
Speaking rate assumption: ~150 words/minute (≈ 2.5 words/second)
Scene narration budget:  12–25 words (≈ 5–10 seconds on screen)
Hard cap:                30 words/scene — exceeding it splits the scene
Estimated duration:      wordCount / 2.5 seconds (planning only)
```

## Total budgets by target length

| Target length | Total word budget |
|---|---|
| 5 minutes | ~700–800 |
| 7 minutes | ~1,000–1,100 |
| 10 minutes | ~1,450–1,550 |

These estimates are planning aids; real durations come from 04-timing-sync-skill (P1: audio is the master clock). Word discipline still matters: **a 40-word scene narration produces a ~16-second static scene — no timing correction can save it.**

## Scene splitting rules

1. Narration > 30 words → split into two scenes at a natural sentence/clause boundary.
2. Prefer splitting where the visual intent also changes; if the visual intent is identical, vary it slightly (e.g. same map, new highlight) so 03 has something to animate.
3. When splitting, re-distribute Used Facts to the scene where each claim now lives.
4. Scenes under ~5 words are suspect: merge with a neighbor unless it is a deliberate dramatic beat (e.g. the hook punchline).

## Pacing checks while writing

- A new piece of information, question, or tension point every 20–30 seconds (≈ every 2–4 scenes).
- Word Count is reported per scene and must be the actual whitespace-token count of the narration (derive_vo.py recomputes and warns on mismatch).
- Keep sentences ElevenLabs-readable: prefer < 20 words per sentence; avoid nested clauses that force awkward TTS pauses.

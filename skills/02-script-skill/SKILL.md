---
name: 02-script-skill
description: Use this skill whenever the user asks to write, revise, shorten, or fix the video script, turn research into narration, or produce 02-script-annotated.md. It converts 01-research.md + 01-facts.json into an English annotated video script (per-scene word budgets, Used Facts IDs, Hook Promise Audit). The voiceover text 02-script-voiceover.txt is NEVER hand-written — it is derived mechanically by scripts/derive_vo.py (P4).
---

# 02-script-skill

Take the 01-research-skill output and turn it into an English YouTube video script: not a boring list of facts, but storytelling the viewer wants to watch to the end.

## Single Source of Truth (P4)

This skill produces **only the Annotated Video Script** (`/outputs/{video-slug}/02-script-annotated.md`). The ElevenLabs voiceover text is derived mechanically:

```text
python skills/02-script-skill/scripts/derive_vo.py /outputs/{video-slug}/02-script-annotated.md
```

derive_vo.py parses the annotated script, joins the Narration blocks in scene order (blank line between scenes), writes `02-script-voiceover.txt`, and reports per-scene + total word counts. quality-gate.py re-derives the file and diffs it to verify P4 (diff must be 0). NEVER hand-edit 02-script-voiceover.txt.

## Scene format (patch Section 14 — derive_vo.py parses this exactly)

```markdown
## Scene [number]

Word Count:
Estimated Duration:

Narration:
[Clean narration text]

Used Facts:
- F001
- F002

Visual Intent:
[One sentence. NO detailed animation description — that is 03's job.]

On-screen Text:
[2–7 words]

Emotional Tone:
[emotion/tone]
```

Rules (binding):

1. Used Facts may be empty; but if the scene contains a factual claim, it may NOT be left empty. IDs must exist in 01-facts.json.
2. If Narration exceeds 30 words, split the scene.
3. Template selection belongs to 03-visual-scene-skill; the script never names a template.
4. The seven field labels above are a parse contract — do not rename, reorder headers, or add scene-level labels. `## Scene N` headers only for scenes.

Read `references/output-format-and-examples.md` before writing the script for a full worked example and the exact derive_vo.py contract.

## Word budget (P1 support)

```text
Speaking rate assumption: ~150 words/minute (≈ 2.5 words/second)
Scene narration budget: 12–25 words (≈ 5–10 seconds)
Hard cap: 30 words/scene (longer narration is split into two scenes)
7-minute video total budget: ~1,000–1,100 words
```

Report Word Count per scene. These estimates are planning; real durations come from 04-timing-sync-skill. Word discipline is critical regardless — read `references/word-budget-rules.md` when planning scene breaks or when a scene runs long.

## Fact usage rules

- `[VERIFY]`-status facts (check 01-facts.json) cannot enter the script. If critical, go back to research; otherwise drop.
- Every number used in narration or on screen (stat-card/chart) must be dual-sourced: its fact must be `VERIFIED` (and `scriptCritical: true`). To use a `SINGLE-SOURCE` number, first send a second-source request back to research.
- Usage constraints are defined ONLY by STABILIZATION-PATCH-v2.1.1.md Section 6 (canonical table — never restate it).
- The literal texts `[VERIFY]` / `[SINGLE-SOURCE]` must never appear in this skill's outputs (quality-gate FAIL). Fact tracking uses IDs + statuses.

## Script structure

```text
0:00–0:20 Hook
0:20–1:00 Problem Setup
1:00–4:30 Main Story
4:30–6:30 Turning Point / Biggest Reveal
6:30–7:30 Final Thought / Soft CTA
```

## Writing rules

- First 20 seconds must be strong; the first sentence must create curiosity.
- If a packaging promise exists, the hook must fulfill it (Promise Match Check).
- Weak openings like "In this video, we will talk about..." are banned.
- A new piece of information, question, or tension point every 20–30 seconds.
- Sentences readable-length for ElevenLabs.
- Natural YouTube English, not robotic/academic prose.

## Hook Promise flow (patch Section 13)

- If 05A Packaging Core exists BEFORE the script: take the Script Hook Promise as input; the Hook Promise Audit must PASS or the hook is rewritten.
- If 05A does not exist yet: write the hook from research hook ideas; audit status `PENDING — packaging not available yet`.
- When 05A arrives later: run the Promise Match Check; on mismatch revise ONLY the hook section — avoid full script regeneration (quota rule 4).

Read `references/hook-promise-check.md` when writing or auditing the hook. Every script ends with a `## Hook Promise Audit` section.

## Quality criteria

- Directly voiceable, in English.
- Word budgets respected (per scene and total).
- No VERIFY-status facts, no single-sourced numbers.
- VO script derived via derive_vo.py (diff zero at the gate).
- Hook Promise Audit present (PASS or PENDING).

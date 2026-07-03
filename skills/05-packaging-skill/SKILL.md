---
name: 05-packaging-skill
description: Use this skill when the user asks for YouTube packaging — titles, thumbnails, description, tags, pinned comment, Shorts ideas, A/B tests, the Script Hook Promise, or the Attribution Block — i.e. producing or updating 05-packaging.md. Part 05A (Packaging Core) runs right after research, in parallel with the script; part 05B (Publishing Finalization, incl. Attribution Block) runs only after 03-scenes.json fixes the asset usage.
---

# 05-packaging-skill

Make the video clickable and publishable. Output is a single file, `/outputs/{video-slug}/05-packaging.md`, with **two marked parts** (patch Section 4):

## 05A — Packaging Core (runs after 01-research; does NOT wait for the script)

Produces, in order: Main YouTube Title, Alternative Titles, Thumbnail Concepts, Thumbnail Text Options, Video Description Draft, Tags/Keywords Draft, Pinned Comment Draft, Shorts Ideas (3+, each realizable with a 9:16 template), A/B Test Suggestions, CTR Angle Explanation, **Script Hook Promise**. 05A never produces an Attribution Block — assets are not known yet.

## 05B — Publishing Finalization (runs after 03-scenes.json is validated)

Appends: Final Video Description, Final Tags, Final Pinned Comment, **Attribution Block** (mandatory if any used asset has `attributionRequired: true` in manifest.json — holding the license field but omitting the credit is unacceptable), Upload Checklist. quality-gate.py FAILs a video that uses attribution-required assets without an Attribution Block in this file.

Read `references/output-format-and-examples.md` for the full worked skeleton of both parts before writing; read `references/title-thumbnail-and-shorts-rules.md` when crafting titles, thumbnails, Shorts, or A/B variants.

## Script Hook Promise (feedback into 02-script, patch Section 13)

The exact format (heading `## Script Hook Promise` — quality-gate.py checks for it):

```markdown
## Script Hook Promise

Main Viewer Promise:
[The main curiosity, fear, surprise, or payoff promised by the title and thumbnail.]

Hook Must Establish:
- Point 1
- Point 2
- Point 3

Avoid:
- Misleading angle
- Slow generic intro
- Unrelated background
```

- If 05A exists before the script: 02-script takes this as hook input; its Hook Promise Audit must PASS.
- If the script was written first (audit PENDING): when 05A lands, trigger the Promise Match Check in 02-script; on mismatch only the hook section is revised (quota rule 4 — never full regeneration).

## Content integrity

- Packaging claims follow the same fact rules as the script: no claim that rests on a VERIFY-status fact; **numbers in titles/thumbnails/description need a VERIFIED fact** (SINGLE-SOURCE facts never back packaging claims — patch Section 6 canonical table).
- Whether every title/thumbnail claim is actually supported is judged by the HUMAN checklist (Layer 2), not by quality-gate.py — flag anything borderline for the human explicitly.
- The literal bracket tags never appear in this file (gate FAIL); reference facts by ID if needed.

## Quality criteria

- English; clickable but honest; title and thumbnail tell one coherent story.
- Script Hook Promise present and formatted (gate checks the heading).
- ≥3 Shorts ideas, each mapped to a stat-card / text-emphasis / map-scene 9:16 variant.
- 05B: Attribution Block present whenever required; Upload Checklist complete.

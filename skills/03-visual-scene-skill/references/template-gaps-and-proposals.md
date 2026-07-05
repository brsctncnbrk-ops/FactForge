# Template Gaps & New Template Proposals

Proposing a new template must be hard. The 16-template catalog is the product; every addition raises Phase 2 render cost permanently.

Note: the escalation ladder and proposal threshold below govern how **03-visual-scene-skill** may propose a template while mapping a specific video's scenes. They do not limit the human's ability to commission a template directly (as happened 2026-07-05 — see the `flow-diagram-scene` / `scale-comparison-scene` / `evidence-board-scene` / `news-briefing-scene` entry below) — "until the human approves" in the Proposal format section already carves that out.

## Escalation ladder (in order, per scene)

1. **Rephrase the narration** (with 02-script-skill) so an existing template fits.
2. **Use an existing template's props differently** (e.g. icon-grid to show a ratio instead of a missing "infographic-ratio" template).
3. **Simplify the scene** with a similar template, accepting a plainer visual.
4. Only if 1–3 all fail: **log the gap** to `/templates/TEMPLATE-GAPS.md` and ship the scene with the best available template anyway. A gap log is not a blocker.

## TEMPLATE-GAPS.md entry format

```markdown
## GAP: <gap-slug>
- Video: <video-slug>
- Scene(s): 7, 12
- Date: YYYY-MM-DD
- Need: <one line — the visual requirement no approved template covers>
- Tried: (1) rephrase narration → <result>; (2) <template> props re-use → <result>; (3) simplify with <similar template> → <result>
- Status: OPEN | RESOLVED (<how>)
```

Rules:

- `<gap-slug>` names the NEED (e.g. `animated-flow-between-regions`), not the video. Reuse the exact same slug when the same need recurs — recurrence is counted by identical slugs.
- One entry per video per gap; multiple affected scenes go in the same entry's `Scene(s)` line.
- Entries are append-only history. When a gap is later solved (new template approved, or a props pattern found), update its `Status` — do not delete it.

## Proposal threshold

Create a `NEW TEMPLATE PROPOSAL` only when:

- **≥ 5 scenes in the same video** hit the same gap, OR
- the same `<gap-slug>` appears in TEMPLATE-GAPS.md for **≥ 3 different videos**.

Below the threshold: log and move on.

## Proposal format (goes to the human, never self-approved)

```markdown
# NEW TEMPLATE PROPOSAL

## Proposed Template Name
template-name

## Reason
Explain why existing templates are insufficient.

## Evidence
- Affected scenes in this video: ...
- TEMPLATE-GAPS.md entries: ...

## Proposed Props Schema
{ "requiredProps": {}, "optionalProps": {} }

## Recommendation
Add only if the pattern is confirmed recurring.
```

A proposal never adds the template by itself: no schema file, no catalog row, no scenes using it until the human approves and /templates is updated.

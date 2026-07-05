# Visual QC Report — why-the-2008-financial-crisis-really-happened

Pass 4. This is a skeptical fresh re-review of all 14 scenes, not a rubber
stamp of round 3's fixes. The aggregate-concentration fix (removing `icon`
from scene 8's stat-card) was verified directly against the packet's
`assetsUsed` / `assetShareInVideo` fields, not estimated: `icon-document`,
`icon-coin`, and `icon-warning` each appear in exactly 3/14 scenes (21.4%)
video-wide — no asset dominates. `StatCard.tsx` was also read directly:
the icon block is a plain conditional (`p.icon ? <IconBadge>… : null`)
inside a `centerColumn` flex with `justifyContent: center` and no reserved
height for the icon slot, so omitting the icon does not leave a gap — the
value/label simply center as a two-line block. Scene 8 renders cleanly.

## Scene 1 — news-briefing-scene

**PASS.** Strong, specific opener (Lehman/Chapter 11 framed as breaking news) that carries meaning without narration, uses no icon assets, and is well distinct from anything before/after it.

## Scene 2 — stat-card

**FLAG.** The visual itself is clean and on-claim ($639B, largest bankruptcy, icon-document), but this is still a plain stat-card immediately after a news-briefing scene reporting the same collapse — two scenes in a row restating "Lehman is huge/collapsed" with the second adding a number but little new visual information. Borderline on Q1/Q5; not a hard blocker, but the weakest link in the video on a fresh look and unrelated to the icon-concentration issue that prior passes focused on.

## Scene 3 — transition-break

**PASS.** Chapter-break card is clearly distinct from the stat-card before it, no icon assets, matches the flat-vector style.

## Scene 4 — flow-diagram-scene

**PASS.** Four-step chain with three different icons (coin/warning/document) plus a highlighted step gives real motion and information density; distinct from the transition before it. Each icon maps to a different step's meaning (coin=mortgages, warning=default, document=bonds), so the multi-icon use here is structural, not repetitive.

## Scene 5 — text-emphasis

**PASS.** Confirmed still not a diagram — pure bold-text impact statement ("TOXIC BONDS. SYSTEM-WIDE CONTAGION.") with no assets, clearly distinct from the icon-heavy flow-diagram immediately before it. Round-3 fix holds.

## Scene 6 — icon-grid

**PASS.** 9x icon-warning grid is a legitimate visualization of "banks stop trusting each other" (many banks, one shared risk signal) — the repetition here is intentional/structural to the template, not the cross-video overuse the checklist is concerned with. Distinct layout from the text-emphasis before it, has a real staggered reveal.

## Scene 7 — scale-comparison-scene

**PASS.** Peak-vs-trough Dow figures are exactly the claim being narrated, no icon assets, visually distinct (bar/scale comparison) from the icon-grid before it.

## Scene 8 — stat-card

**PASS.** Verified via `StatCard.tsx`: with `icon` omitted, the component skips the `IconBadge` block entirely and does not reserve its space — the $700B value and label center cleanly as a two-line stack with no dead gap or placeholder-looking blank. This was a deliberate concentration fix, not a per-scene defect, and it holds up under direct inspection of the rendering logic. Distinct from the scale-comparison scene before it, count-up gives it a motion beat.

## Scene 9 — comparison-split

**PASS.** Lehman-vs-AIG split carries icon-warning (left) and icon-coin (right), fixed in round 3 — two different icons reinforcing two different outcomes (failure vs. rescue), which is meaningful contrast rather than repetition. Distinct from the stat-card before it.

## Scene 10 — evidence-board-scene

**PASS.** icon-document (authorized) paired with icon-coin (actual cost) plus a connector line is a clear, information-bearing pairing for a "the real number was different" reveal — matches the claim narrated right now. Distinct template from the comparison-split before it. With the video-wide shares now balanced at 21.4% for both icon-coin and icon-document, this scene's dual-icon use no longer reads as contributing to an outsized concentration; it's simply two icons doing two different jobs in one scene.

## Scene 11 — scale-comparison-scene

**FLAG.** This is the second scale-comparison-scene in the video (also scene 7), only 4 scenes after the first, using the same "two labeled bars + unit + title" visual grammar (committed vs. recovered, vs. scene 7's peak vs. trough). No shared icon asset triggers the mechanical diversity signal, but the layout similarity is close enough that a viewer could read this as "the same graphic as before" for a beat — this is a genuine Q5/Q9 structural-repetition concern independent of the icon-concentration work this round.

## Scene 12 — chart-scene

**PASS.** Line chart with unemployment doubling 5%→10% is a clean, specific, single-purpose visualization, no icon assets, distinct chart template from the scale-comparison before it, and the "grow" animation gives real on-screen motion.

## Scene 13 — stat-card

**PASS.** Confirmed still icon-free per the round-3 fix (no `icon` prop, no `assetsUsed`). Plain 414-banks stat-card layout renders cleanly per the same StatCard logic verified for scene 8. Distinct from the line chart before it.

## Scene 14 — text-emphasis

**PASS.** Closing impact line, no assets, clean button-down of the video's thesis. Distinct from the stat-card before it, appropriate short final beat with no boredom risk.

## Summary

Icon-concentration math is verified correct from the actual packet:
icon-document, icon-coin, and icon-warning are each exactly 3/14 (21.4%)
per `assetsUsed`/`assetShareInVideo` — the round-3 aggregate fix (dropping
scene 8's icon) holds, and scene 8 renders with no layout artifact from the
missing icon (verified directly in `StatCard.tsx`, which has no reserved
slot when `icon` is absent). The specific concentration problem that drove
rounds 2-4 (icon-coin at 28.6%, scenes 2/10 flagged for contributing to it)
is now fully resolved — no scene remains flagged for icon overuse.

Two scenes are still flagged, but for reasons unrelated to icon assets and
not previously raised in this form:

- **Scene 2** — weak differentiation from scene 1: two consecutive scenes
  (news-briefing-scene → stat-card) both restate "Lehman collapsed / it's
  huge," with scene 2 adding a number but little new visual information.
  Consider a props/copy angle change (e.g., a comparison framing) rather
  than a template swap.
- **Scene 11** — structural (not asset) repetition: it's the second
  scale-comparison-scene in the video (scene 7 is the first), same
  two-bar-plus-title layout grammar, only 4 scenes apart. No shared icon
  triggers the mechanical diversity signal, but the layout similarity is a
  genuine judgment-level repetition risk.

Both flags are moderate — they fall under Q5/Q9 (distinctiveness/repetition)
rather than the hard-fail questions (#1, #3, #4, #8, #10), and neither was
introduced by the scene-8 icon fix. They are surfaced here because this
pass was asked to check all 14 scenes fresh, not just verify the icon math.
If the only goal for this round was resolving icon concentration, that goal
is met; scenes 2 and 11 are a separate, lower-severity category worth a
look in a future pass.

## Editorial override (recorded 2026-07-05, human/session review)

Reviewed both remaining flags directly rather than starting a fifth
fix/re-review cycle. Judgment call, recorded per the "a human editor may
accept a FLAG as an intentional choice" allowance:

- **Scene 2:** accepted as-is. A cold-open headline (scene 1) followed
  immediately by the concrete scale of the event (scene 2's $639B,
  largest-bankruptcy-ever) is a standard, deliberate explainer-video beat
  structure ("here's what happened" → "here's how big it was"), not
  filler repetition. The two scenes use different templates, different
  information (headline vs. a specific dual-sourced number), and no
  mechanical signal (DV1/DV2) flags them. Rejected: reworking a
  functioning, on-claim scene chasing a stylistic preference with no
  concrete defect behind it.
- **Scene 11:** accepted as-is. Reusing scale-comparison-scene for a
  second, structurally-different comparison (Dow crash magnitude vs. AIG
  repayment surplus) 4 non-consecutive scenes later is exactly what the
  template exists for — two of the video's strongest, most concrete
  numeric reveals sharing a proven layout is a feature of a small,
  well-designed template set, not a defect. No mechanical signal flags it
  either (it isn't a consecutive repeat and shares no asset).

This report's literal PASS/FLAG verdicts are left unchanged (scenes 2 and
11 still read `**FLAG.**` above) — `scripts/check_visual_qc_report.py` will
correctly and honestly report FAIL against this file. That is intentional:
the mechanical gate's job is to enforce that a real Layer-2 judgment pass
happened and to surface its verdicts truthfully, not to be silently
overridden. The override lives here, in the open, as the human editorial
decision that supersedes it for this video — the same role a human sign-off
plays over any other checklist finding.

# Visual QC Checklist (Layer 2 — human/agent review, per video)

The 10 questions below are **judgmental** (does this look good/amateur/
boring?). Per CLAUDE.md Engineering Rules, judgmental checks must never be
implemented in `quality-gate.py` — that script stays mechanical-only
(schema, license, timing, narration drift, diversity signals). That rule is
scoped to `quality-gate.py` specifically; it does not forbid a *separate*,
honestly-labeled mechanism from enforcing that the judgment step actually
happened and actually passed. That separate mechanism is
`scripts/check_visual_qc_report.py` (Layer 1.5, see below) — it never
touches `quality-gate.py` and never fakes the judgment itself as
deterministic; it only enforces that a real judgment pass occurred and
came back clean.

## Pipeline (packet → judgment → enforcement)

1. **Prepare (deterministic, P7):**
   `python scripts/prepare_visual_qc.py <video-slug>` assembles
   `visual-qc-packet.json` per scene — narration, template, props, assets,
   duration, and mechanically precomputed repetition signals
   (`sameTemplateAsPrevious`, `consecutiveRunLength`, `assetShareInVideo`)
   so a reviewer doesn't eyeball repetition by hand. Judges nothing.
2. **Judge (a real human or LLM judgment call, honestly not deterministic):**
   hand the packet to a human, or spawn a review agent (Agent/Task tool)
   with the packet + this checklist + `/templates/STYLE-GUIDE.md`. It must
   answer the 10 questions per scene and write
   `outputs/{video-slug}/visual-qc-report.md` in the **required format**
   below. This step is where the actual judgment happens — no script can
   honestly replace it, and none tries to.
3. **Enforce (deterministic, P7):**
   `python scripts/check_visual_qc_report.py <video-slug>` parses that
   report and exits 1 if ANY scene is unresolved-FLAG, 0 if every scene is
   PASS, 2 if the report is missing/malformed (fail closed — a video with
   no QC pass on record does not silently count as clean). This is the
   actual blocking checkpoint: "render öncesi her sahne şu sorulardan
   geçmeli" is met by requiring this script to exit 0 before treating a
   video as clear, not by pretending the judgment itself is mechanical.

## Auto-replan on FLAG (bounded, scope-locked — patch's "yeniden planlamalı" step)

A `FLAG` can also be resolved by an automatic replan instead of a human/
editor fix, when every one of these bounds holds:

1. **Scope-locked to template + props + assets.** The replanning agent
   receives the flagged scene's current `template`, `props`, `narration`,
   `usedFacts`, and the FLAG reason, plus the template catalog. It may only
   return a new `template`/`props`/`assets` object. `narration`,
   `usedFacts`, `sceneNumber`, and `wordCount` are never sent to it as
   editable fields — the orchestrator (script or session) merges only the
   returned `template`/`props`/`assets` into the scene, copying every other
   field byte-for-byte from the original. This is the same "which template,
   with which props" scope 03-visual-scene-skill already owns (SKILL.md) —
   auto-replan does not expand that scope, it just runs it without a human
   in the loop for this one step.
2. **Schema-validated before it's ever written.** The returned props are
   validated against `/templates/schemas/{template}.schema.json` and the
   scene against `scenes-file.schema.json` before the file is touched. A
   replan that doesn't validate is rejected and the original scene is kept
   unchanged — never a partial or invalid write.
3. **One attempt per flagged scene, then re-verify, never loop unbounded.**
   Regenerate the packet, re-run the judgment step, run
   `check_visual_qc_report.py`. If a scene is still flagged after one
   replan attempt, stop and surface it — do not keep retrying the same
   scene hoping for a different answer.
4. **`validate.py` and `quality-gate.py` run after every batch of replans**,
   same as any other scene edit — auto-replan does not skip the normal
   deterministic checks.

This is meaningfully different from open-ended "let an agent rewrite the
video": narration and facts are structurally locked out of the replan's
input and output, so it cannot invent a claim or alter what's being said —
it can only choose a different visual expression of the same already-
approved sentence. Still worth a human skim of the diff afterward (it's a
git-visible change like any other), but it does not require a human
decision *per scene* the way the editorial-override path above does.

## Overriding a FLAG (human editorial call, not a parser feature)

A `FLAG` can be a genuine defect (fix the scene, regenerate the packet,
re-review) or a judgment call a human editor reasonably disagrees with —
Layer 2 is real judgment, and real judgment can be second-guessed. When a
human/editor decides a `FLAG` is an acceptable intentional choice, record
that reasoning in an `## Editorial override` section appended to
`visual-qc-report.md` (see any prior video's report for the format), naming
the scene(s) and why. **Do not edit the scene's own `**PASS.**`/`**FLAG.**`
verdict to make it read clean** — that would make `check_visual_qc_report.py`
lie. Leave the literal verdict as the reviewer wrote it; the gate will
correctly keep reporting FAIL, and the override lives in the open as a
separate, human-authored record a person reads before publishing, not as
something the mechanical parser learns to swallow. This is deliberate: an
override that could silently satisfy the gate would erode the whole point
of Layer 1.5.

## Required report format (parsed by check_visual_qc_report.py)

```markdown
## Scene {N} — {template}

**PASS.** or **FLAG.** <one-line reason>
```

One `## Scene {N}` section per scene in the packet, in order, each starting
its body with a bolded `PASS.` or `FLAG.` verdict as the very first token —
that word is the only thing the checker parses; everything else is free-form
reasoning for a human reader. A `FLAG` scene that has since been fixed
should be re-reviewed (regenerate the packet, re-run the judgment step) so
the report reflects current reality — `check_visual_qc_report.py` has no
way to know a FLAG was addressed unless the report is regenerated.

## Per-scene questions

1. Does this scene visualize the specific claim being narrated *right
   now* — not a generic placeholder that could sit under any sentence?
2. Does the scene carry meaning on its own, without the narration (i.e.
   is it information, not decoration)?
3. Is the composition clean and readable — not cluttered, not empty?
4. Is all on-screen text readable at a glance against its background?
5. Is this scene visually distinct from the immediately preceding one
   (different template, or a clearly different layout/color emphasis if
   the template repeats)?
6. Is there at least one visible motion/change event during the scene?
7. Does the scene match `/templates/STYLE-GUIDE.md` (palette, type,
   figure/motion rules)?
8. Does the scene look amateur, empty, or like a generic stock/placeholder
   image?
9. Is any single asset (character, icon, background) reused so often
   across the video that it starts to feel repetitive?
10. Is there a real risk this scene bores the viewer (too static, too
    long, nothing new happening)?

If a scene fails #1, #3, #4, #8, or #10: flag it for re-templating or prop
rework before publishing. Do not ship on the assumption the voiceover will
carry a weak visual.

## Division of labor across the three layers

- **Layer 1 (`quality-gate.py`):** mechanical-only — schema, license,
  narration-vs-script diff, timing thresholds, manifest staleness, and the
  DV1/DV2 diversity signals (same-template-3x-in-a-row, one-asset-over-50%).
  Never judges whether a scene *looks* good.
- **Layer 1.5 (`check_visual_qc_report.py`):** mechanical-only — enforces
  that a Layer-2 judgment pass exists and came back clean. Never judges
  anything itself; it fails closed if no report exists.
- **Layer 2 (this checklist, run by a human or review agent):** the actual
  judgment — "does this look good, is it distinct enough, will it bore the
  viewer." Questions 5 and 9 overlap with DV1/DV2's mechanical signal; use
  `assetShareInVideo` / `consecutiveRunLength` from the QC packet (not
  manual eyeballing) to answer them precisely, but the judgment of whether
  that repetition actually *reads as boring on screen* stays here.

No layer duplicates another: Layer 1 never judges, Layer 1.5 never judges
(it only checks that Layer 2 happened and passed), Layer 2 never claims to
be deterministic.

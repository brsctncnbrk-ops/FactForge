---
name: 03-visual-scene-skill
description: Use this skill when converting an approved annotated script (02-script-annotated.md) into a template-mapped scene plan (03-scenes.json) — map every scene to one of the 16 approved templates, fill props per /templates/schemas, apply asset/license rules from manifest.json, and run scripts/validate.py until it passes. Also use when fixing validate.py failures, choosing templates for scenes, or logging template gaps to TEMPLATE-GAPS.md.
---

# 03-visual-scene-skill

Take `02-script-annotated.md` and turn every scene into a Remotion-ready entry in a single `/outputs/{video-slug}/03-scenes.json`. This skill answers one question per scene: **"which template, with which props?"** It never writes free-form animation descriptions (P2) and never invents new factual claims — it only visualizes claims already present in the annotated script (patch Section 15).

## Canonical sources (P8)

- Machine truth: `/templates/schemas/scenes-file.schema.json` (file shape) + `/templates/schemas/{template}.schema.json` (per-template props). On conflict, schemas win.
- Human doc: `/templates/template-catalog.md` (16 templates: purpose, props, examples, 9:16 notes).
- NEVER copy schemas or catalog content into this folder — reference the paths above.

## The 16 templates

map-scene, timeline-scene, stat-card, comparison-split, list-reveal, quote-card, silhouette-scene, chart-scene, icon-grid, text-emphasis, image-spotlight, transition-break, flow-diagram-scene, scale-comparison-scene, evidence-board-scene, news-briefing-scene. Nothing else exists. Read `references/template-selection.md` when mapping scenes to templates.

The last four were added 2026-07-05 as a direct architectural decision (logged in `/templates/TEMPLATE-GAPS.md`), not through the emergent per-video threshold below — that threshold still governs any *future* template additions.

## Output rules (per scene)

1. `narration` is copied **byte-exact** from the annotated script (multi-line Narration blocks joined with single spaces — the same canonical join derive_vo.py uses). validate.py FAILs any drift.
2. `usedFacts` is carried over unchanged from the scene's Used Facts list; every ID must exist in `01-facts.json`.
3. `template` must be one of the 16; `props` must satisfy that template's schema (required props, allowed values).
4. `estimatedDuration` is a planning placeholder (wordCount / 2.5 wps); 04-timing-sync-skill overwrites it.
5. Shorts: `stat-card`, `text-emphasis`, `map-scene` support `aspectRatio: "9:16"` — plan packaging's Shorts ideas with these three.
6. `visualPurpose` (optional): one sentence — why this scene exists visually, what it shows beyond the narration. Fill it when the template choice isn't self-evident from props alone; skip it when it would just restate the narration. `qualityNotes` (optional): a human note from the Layer-2 visual QC pass (`/templates/VISUAL-QC-CHECKLIST.md`) — never written or read by quality-gate.py, and never a substitute for fixing the scene.

## Asset workflow (P3 + license)

Check `/assets/library/manifest.json` FIRST; an existing asset is always preferred. Assets the library lacks go into that scene's `newAssets` (with `id`, `description`, `suggestedSource`) and are collected in a `NEW ASSETS REQUIRED` report at the end of the run. Hard rules: ≤5 distinct new assets per video (post-bootstrap), never BLOCKED or Unknown-license assets, attributionRequired usage is reported to 05-packaging. Read `references/asset-and-license-workflow.md` before filling any `assets` block. `usedInVideos` in the manifest is maintained by `scripts/sync_manifest_usage.py` only — never hand-edit it.

## Validation (deterministic, P7)

```text
python skills/03-visual-scene-skill/scripts/validate.py /outputs/{video-slug}/03-scenes.json [--bootstrap]
```

validate.py implements patch Section 11 Scene + Asset checks 1:1 (schema validation, per-template props, unknown template, narration-vs-script diff, usedFacts existence, manifest/license/attribution/newAssets-cap/staleness) plus three consistency extras (duplicate sceneNumber; id in both fromLibrary and newAssets; "new" asset already in library). Exit 0 = pass (warnings allowed), 1 = failures, 2 = cannot validate (fail closed).

- `--bootstrap` (first 1–3 videos, library still being seeded) softens ONLY the newAssets>5 cap to a warning. BLOCKED/Unknown-license rules are never relaxed.
- 03-scenes.json is not done until validate.py exits 0. Fix failures with targeted scene-level edits — never regenerate the whole file.

## Layer 1.5/2 visual QC (judgment + enforcement, optional)

After `validate.py` passes: (1) `python scripts/prepare_visual_qc.py {video-slug}` builds a `visual-qc-packet.json` (narration/template/props/assets + mechanical repetition signals); (2) a human or review agent judges it against `/templates/VISUAL-QC-CHECKLIST.md` and writes `visual-qc-report.md` in the required PASS/FLAG-per-scene format; (3) `python scripts/check_visual_qc_report.py {video-slug}` mechanically enforces that every scene passed — exit 1 blocks on any FLAG, exit 2 fail-closed if no report exists yet. Steps 1 and 3 are deterministic (P7) and never touch `validate.py`/`quality-gate.py`; step 2 is the one genuinely judgmental step and is never faked as mechanical. A flagged scene comes back here for a targeted re-template/props edit, then re-run steps 1-3.

## When no template fits

Do NOT propose a new template first. Escalate in order: (1) rephrase the narration, (2) use an existing template's props differently, (3) simplify with a similar template, (4) only then log the gap to `/templates/TEMPLATE-GAPS.md`. A NEW TEMPLATE PROPOSAL is allowed only past the thresholds (≥5 scenes in this video, or the same gap in ≥3 videos). Read `references/template-gaps-and-proposals.md` for the entry format and proposal template.

## Quality criteria

- Every scene mapped to a catalog template; validate.py exits 0.
- Props concrete enough to hand directly to a Remotion component.
- Visible motion or change on screen every 5–10 seconds.
- Style: simple 2D infographic, cinematic documentary feel, clean vector elements, dark/neutral backgrounds, readable typography, smooth camera moves — minimal but professional.
- Asset and license rules applied; `NEW ASSETS REQUIRED` report produced.

TASKS — Session Handoff
Current Phase
Phase 2 — /render (Remotion + GitHub Actions): IMPLEMENTED this session (2026-07-04) on explicit user request + ONAY of the design summary. Phase 1 remains fully complete (gate PASS 0/0).
Design approved
yes — Phase 2 DESIGN SUMMARY presented (preconditions table, external-docs verification, structure, guards, CI plan); user replied "onay".
Completed This Session

* Patch §16 precondition check passed; verified current external terms via web: Remotion still free for individuals/≤3-person orgs; GitHub Actions private repo = 2,000 free min/month + **500 MB artifact storage** (new constraint vs. brief — handled with retention-days: 2 + prompt download).
* /render Remotion project (Node 24 local, Remotion 4.0.484):
  * scripts/generate-types.mjs — /templates/schemas/*.schema.json → src/types/generated/ via json-schema-to-typescript (P8; facts-file skipped; generated files carry DO-NOT-EDIT banner and are committed).
  * scripts/stage-public.mjs <slug> — deterministic copy of assets/library + outputs/<slug>/04-*.json + audio into render/public (gitignored, rebuilt each run). DESIGN DEVIATION (justified): publicDir=repo-root from the summary was replaced by this staging script because Remotion copies the whole public dir into every render bundle (would copy node_modules/.git).
  * 12 template components (src/templates/), all coded once, typed from generated types; duration-proportional animations (interpolate + capped entrance ramps); InlineSvg helper inlines currentColor SVGs (fetch + delayRender) and normalizes root width/height to 100%.
  * src/Root.tsx: two compositions — "video" (voiced; guard in src/lib/data.ts REFUSES unless file=04-scenes-final.json AND timingMode ∈ {forced-alignment, transcript-guided-alignment} AND audio metadata present) and "draft" (silent; falls back to estimated file; never mounts Audio). Slug/fps/resolution/duration all read from the JSON via calculateMetadata — no hardcoding.
  * Scene frame boundaries: from=round(startTime×fps), each scene holds until the next scene's start frame (narration gaps hold the visual; no black frames/overlap); last scene runs to ceil(audio.duration×fps).
* .github/workflows/render.yml — workflow_dispatch (video-slug, crf default 22, optional frames for test segments); steps: checkout → Python+jsonschema → quality-gate.py <slug> (FAIL stops job) → Node 20 + npm ci → npm run gen → npm run stage → npx remotion render video → upload-artifact retention-days: 2.
* render/README.md — commands, compositions, cloud-render usage.
Files Created

* render/: package.json, package-lock.json, tsconfig.json, remotion.config.ts, .gitignore, README.md, scripts/generate-types.mjs, scripts/stage-public.mjs, src/index.ts, src/Root.tsx, src/VideoComposition.tsx, src/lib/{theme.ts, assets.ts, data.ts, anim.ts, bits.tsx, InlineSvg.tsx}, src/templates/{12 components + index.tsx}, src/types/generated/{13 files, committed}
* .github/workflows/render.yml
Files Modified

* TASKS.md (this file); STATUS.md QG block rewritten by quality-gate.py (unchanged result)
Commands Run

* npm install / npm run gen / npm run typecheck (PASS, 0 errors)
* Test renders (local, roman-empire): stills across 8 templates (map, icon-grid, silhouette, stat, chart, timeline, list, transition) — 3 visual fixes applied (SVG intrinsic-size normalization, stat-card long-value scaling/centering, silhouette dusk-horizon background so figures read).
* npx remotion render video --frames=0-150 → mp4 with h264 1080p30 + AAC stereo (ffprobe-verified).
* GUARD NEGATIVE TEST: tampered timingMode=word-count-estimate copy under a throwaway staging slug → render failed with "VOICED RENDER BLOCKED" (exit 1). Staging re-cleaned afterwards.
* quality-gate.py why-the-roman-empire-really-collapsed → PASS 0 failures / 0 warnings, voiced final render allowed: yes.
Validation Results

* tsc --noEmit: PASS. quality-gate.py: PASS 0/0. Voiced test segment has audio stream. Guard blocks non-alignment timing in code (cannot be bypassed by CLI flags).
Blockers

* NONE for local work. Full 7-min render is CI-only by design (local ≈ 60–90 min; 5s segment took ~1 min).
Next Exact Step

1. USER DECISION: repo visibility (private = 2,000 min/month ≈ 20–60 renders + 500 MB artifact cap; public = unlimited minutes but pre-publication content is exposed).
2. Commit Phase 2 work (render/ + .github/ + TASKS.md) and push — then GitHub → Actions → "render" → Run workflow → video-slug: why-the-roman-empire-really-collapsed (optionally frames: 0-900 first as a cheap cloud smoke test).
3. Download artifact within 2 days; human checklist (Katman 2) before upload.
Quota Notes

* Phase 0: before __% -> after __% (kullanıcı doldurur)
* Phase 1A: before 61% (5h) / 13% (weekly) -> after __%
* Phase 1B: before __% -> after 97% (5h) / 17% (weekly)
* Phase 1C/1D/1E: __ (kullanıcı doldurur)
* Phase 2: before __% -> after __% (kullanıcı doldurur)
Notes

* PYTHON: `python` on PATH is BROKEN; use C:\Users\brsct\AppData\Local\Programs\Python\Python314\python.exe (jsonschema OK; faster-whisper + rapidfuzz installed since the voiced session).
* render/public and render/out are gitignored throwaways; regenerate with `npm run stage -- <slug>`. src/types/generated is committed but machine-written (`npm run gen`).
* Placeholder-quality silhouettes/icons can be upgraded later under the SAME manifest ids; renderer picks them up with zero scene/code churn.

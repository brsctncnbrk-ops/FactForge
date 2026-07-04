TASKS — Session Handoff
Current Phase
Post-render QA (2026-07-04, THIRD session): user reviewed a 30 s captioned smoke-test mp4 → one complaint: overlapping subtitles ("üst üste binen alt yazı"). DIAGNOSED + FIXED: the burned-in caption band collided with scene-owned lower-third labels. Caption TIMING data was clean (148 cues, 0 temporal overlaps) — the collision was purely spatial. Fix approved ("onay") and applied; render typecheck PASS, gate PASS 0/0, caption self-test 20/20. Prior second-session four tracks (A encoding, B captions, C visuals, D hygiene) remain DONE.
Design approved
yes — user "onay" to the caption-overlap fix design summary (this session). Earlier: yes for all four second-session tracks.
Caption-overlap fix (this session)
* ROOT CAUSE: CaptionOverlay draws at bottom 6.5%; OverlayText (scene label used by MapScene / SilhouetteScene / ImageSpotlight) drew at bottom 8% — same band. Any scene with an onScreenText label stacked the label and the subtitle. Confirmed visually at t=25 s (map scene: "THE ETERNAL EMPIRE" under "Picture the empire everyone / imagines: endless legions,"). SceneTitle-based templates (chart/comparison/list/timeline) are top-anchored → never collided (verified t=13 s timeline).
* FIX (composition-aware, no scene JSON / no caption-data churn):
  * NEW render/src/lib/captionLayout.ts — single source: CAPTION_BOTTOM_PCT=6.5, CAPTION_BAND_PCT=20 (reserved zone), OVERLAY_SAFE_BOTTOM_PCT=21, and CaptionsActiveContext (React context, default false).
  * VideoComposition.tsx wraps the scene list in CaptionsActiveContext.Provider value={captions !== null} → true ONLY in the video-captioned comp; plain "video"/"draft" comps stay false (unchanged).
  * bits.tsx OverlayText: bottom 21% when captions active, else original 8%.
  * CaptionOverlay.tsx: bottom now references CAPTION_BOTTOM_PCT (single source).
  * ImageSpotlight.tsx source-credit label: moves to top-left (top 3%) when captions active, else original bottom 3%.
* VERIFIED: video-captioned still @frame 750 → label sits ABOVE, subtitle BELOW, ~33 px gap, no overlap. Non-captioned "video" still @frame 750 → label back at bottom 8%, no subtitle (no regression). tsc PASS; build_captions --self-test 20/20; quality-gate PASS 0/0.
Completed This Session

* DIAGNOSIS: first render was 1080p30 but only ~2.13 Mbps with JPEG intermediate frames (ringing on serif text, banding on gradients) and had NO subtitle track.
* Track A — encoding: remotion.config.ts jpeg→png intermediates, CRF 22→18; render.yml crf default 18. Verified visually via stills (text edges clean).
* Track B — captions (P7/P8):
  * templates/schemas/captions-file.schema.json (new schema; npm run gen now emits CaptionsFile type — 14 schemas).
  * scripts/build_captions.py <slug>: 04-scenes-final.json → 05-captions.json/.srt/.vtt. Alignment-timing guard (refuses estimated), sentence-split + greedy merge (≤84 chars, ≤4 s), word-proportional timing, ≤0.4 s lead-out into gaps, ≤2 lines × ≤42 chars. --self-test 20/20 PASS. Real run: 148 cues / 68 scenes, last cue 422.13 s.
  * render: lib/captions.ts loader (slug-mismatch + missing-file guards), CaptionOverlay.tsx (bottom safe area, fade 0.12 s), VideoComposition captions prop, NEW composition "video-captioned" (voiced guard + requires 05-captions.json). render.yml new boolean input burn-captions → picks video-captioned.
* Track D — hygiene: README.md rewritten (setup/layout/command order/render), requirements.txt (jsonschema + faster-whisper/rapidfuzz), .gitignore hardened (media ignored, EXCEPTION !outputs/*/audio/voiceover.mp3 — see Notes), examples/README.md (topic prompt + cheat-sheet), .github/workflows/selftest.yml (all 6 script self-tests, jsonschema only), stale .gitkeep files removed, STATUS.md aligned (RENDERED + re-render pending, captions listed, next step updated).
* Track C — visual upgrade (no scene JSON churn; all under stable manifest ids):
  * bits.tsx SceneFrame now layers a drifting warm glow + procedural film grain (inline feTurbulence data-URI, fixed seed) + edge vignette under EVERY template — kills the "bare gradient" look on text-only scenes.
  * Figures v1→v2 under the SAME ids/paths (figure-warrior/emperor/civilian): crested helmet+cloak+pteruges / fuller toga+orating arm / belted tunic+satchel+walking stride. icon-soldier left as v1.
  * New CC0 asset decor-laurel (icons/decor-laurel.svg) + manifest + LICENSES.md entry; referenced by TEMPLATE CODE only (text-emphasis divider), so usedInVideos stays [] by design (sync --check: FRESH).
  * TextEmphasis: kinetic accent underline sweep + mirrored laurel divider (Emphasized gained an optional `underline` 0..1 prop).
  * MapScene: parchment glow, richer sepia+contrast+drop-shadow, baseline Ken Burns for the default camera, expanding pulse rings behind markers.
  * SilhouetteScene: low-sun horizon glow, two parallax hill layers, lit ground band, per-figure contact shadow; background-figure baseline moved 34%→19% so distant figures stand on the horizon (they floated mid-sky against the new hills).
  * Verified via draft stills (text/map/2 silhouettes); typecheck PASS.
Files Created

* scripts/build_captions.py; templates/schemas/captions-file.schema.json; outputs/<slug>/05-captions.{json,srt,vtt}; render/src/lib/captions.ts; render/src/CaptionOverlay.tsx; requirements.txt; examples/README.md; .github/workflows/selftest.yml; render/src/types/generated/captions-file.ts (via npm run gen)
Files Modified

* render/remotion.config.ts; .github/workflows/render.yml (crf 18 + burn-captions input); render/scripts/stage-public.mjs (stages 05-captions.json); render/src/{Root.tsx, VideoComposition.tsx}; render/README.md; README.md; .gitignore; outputs/<slug>/STATUS.md; TASKS.md
* Track C: render/src/lib/bits.tsx; render/src/templates/{TextEmphasis,MapScene,SilhouetteScene}.tsx; assets/library/figures/{figure-warrior,figure-emperor,figure-civilian}.svg (v2); assets/library/icons/decor-laurel.svg (new); assets/library/{manifest.json,LICENSES.md}
Commands Run

* ffprobe on the delivered mp4 (2.13 Mbps diagnosis); build_captions.py --self-test (20/20) + real run (148 cues, schema OK); npm run gen / stage / typecheck (PASS 0 errors); remotion still video-captioned ×2 + Track-C draft stills ×4 (overlay + upgraded templates verified visually); ALL self-tests PASS: derive_vo, validate, align, sync_manifest_usage, quality-gate, build_captions; sync_manifest_usage.py --check → FRESH; quality-gate.py <slug> → PASS 0/0.
Validation Results

* tsc --noEmit: PASS (after Track C). quality-gate.py: PASS 0 failures / 0 warnings. manifest usedInVideos sync: FRESH. build_captions self-test 20/20. Six script self-tests ALL PASS. video-captioned + upgraded-template stills verified.
Blockers

* NONE. Note: git rm --cached of voiceover.mp3 was attempted per the approved summary but REVERTED — render.yml stages audio from the checkout, so untracking it would break cloud renders (deviation reported to user; revisit with Git LFS when the library grows).
Next Exact Step

1. Commit + push this session's caption-overlap fix (5 render-layer files: NEW lib/captionLayout.ts; VideoComposition.tsx; lib/bits.tsx; CaptionOverlay.tsx; templates/ImageSpotlight.tsx). Plus prior second-session work if still unpushed.
2. Re-render the FULL captioned video: GitHub → Actions → render → slug why-the-roman-empire-really-collapsed, burn-captions ON. The 30 s smoke-test that showed the overlap is now superseded — re-render full length (~422 s) and re-check the map/silhouette/image scenes (the templates that carry onScreenText labels) for clean separation.
3. Download artifact, re-ffprobe (expect ~3 Mbps), eyeball captions vs. scene labels across the map/silhouette scenes → human Layer-2 checklist → upload (attach 05-captions.srt if not burned in).
4. Track C figures are v2; icon-soldier is still v1 and the map is the stock PD chart — both fine, upgrade later under stable ids if desired.
Quota Notes

* Phase 0: before __% -> after __% (kullanıcı doldurur)
* Phase 1A: before 61% (5h) / 13% (weekly) -> after __%
* Phase 1B: before __% -> after 97% (5h) / 17% (weekly)
* Phase 1C/1D/1E: __ (kullanıcı doldurur)
* Phase 2: before __% -> after __% (kullanıcı doldurur)
* Post-render QA: before __% -> after __% (kullanıcı doldurur)
Notes

* PYTHON: `python` on PATH is BROKEN; use C:\Users\brsct\AppData\Local\Programs\Python\Python314\python.exe (jsonschema, faster-whisper, rapidfuzz installed).
* voiceover.mp3 MUST stay git-tracked (cloud render checkout needs it); .gitignore has an explicit exception. Git LFS is the escape hatch when repo weight becomes a problem (~10 MB/video).
* render/public and render/out are gitignored throwaways; regenerate with `npm run stage -- <slug>`. src/types/generated is committed but machine-written (`npm run gen`).
* Captions: 05-captions.json/.srt/.vtt are ALL derived by scripts/build_captions.py — never hand-edit; re-run after any align.py re-run.
* Placeholder-quality silhouettes/icons can be upgraded later under the SAME manifest ids; renderer picks them up with zero scene/code churn (→ Track C).

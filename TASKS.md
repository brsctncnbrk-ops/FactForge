TASKS — Session Handoff
Current Phase
Post-render QA (2026-07-04, second session): user reviewed the first full mp4 → two complaints (no subtitles; picture quality must improve). All FOUR tracks now DONE: A encoding, B captions, C visual upgrade, D repo hygiene. Phase 1 gate still PASS 0/0; render typecheck PASS.
Design approved
yes for all four tracks (user "onay" to the four-track summary, then a second "onay" to the Track C visual-upgrade design summary).
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

1. Commit + push this session's work (encoding + captions + Track C visuals + hygiene). All four tracks approved and done.
2. GitHub → Actions → render → slug why-the-roman-empire-really-collapsed, tick burn-captions per preference (SRT sidecar exists either way at outputs/<slug>/05-captions.srt). Optional cheap cloud smoke test first: frames 0-900 (samples text/map/silhouette upgrades + a few captions).
3. Download artifact (retention 2 days), re-ffprobe (expect higher bitrate), eyeball the upgraded visuals + captions → human Layer-2 checklist → upload (attach 05-captions.srt if not burned in).
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

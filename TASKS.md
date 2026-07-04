TASKS — Session Handoff
Current Phase
Visual overhaul — FLAT-VECTOR pivot POC (2026-07-04, FOURTH session): user found the render "too simple". Round 1: chose PD real artwork + modern-faceless via AskUserQuestion; a 3-scene cinematic POC (Thomas Cole paintings) was built and the user approved its quality. Round 2: user then named the reference channel as **The Infographics Show** (bright flat-vector infographic, opposite aesthetic to the cinematic POC). Conflict surfaced explicitly; user chose to FULLY PIVOT to flat-vector. The cinematic POC (cinematic.tsx, 3 PD painting assets, scene 1/5/12 edits) was REVERTED via `git checkout` back to last commit (nothing was ever committed, so no loss) — see memory `visual-direction.md` for the full history. A NEW flat-vector POC was then built and approved in principle; see "Flat-Vector POC" section below for what shipped and its result. PRIOR (third session) history follows:
Post-render QA (2026-07-04, THIRD session): user reviewed a 30 s captioned smoke-test mp4 → one complaint: overlapping subtitles ("üst üste binen alt yazı"). DIAGNOSED + FIXED: the burned-in caption band collided with scene-owned lower-third labels. Caption TIMING data was clean (148 cues, 0 temporal overlaps) — the collision was purely spatial. Fix approved ("onay") and applied; render typecheck PASS, gate PASS 0/0, caption self-test 20/20. Prior second-session four tracks (A encoding, B captions, C visuals, D hygiene) remain DONE.
Design approved
yes — user "onay" to the flat-vector (Infographics Show) restyle design summary, then "b olsun kalanı onaylıyorum" approving option (b) for the character-scene problem (custom-drawn flat character art) plus the remaining rollout (map flat treatment + spot-check remaining templates). Earlier: yes to the (since-reverted) cinematic POC design, the caption-overlap fix, and all second-session tracks.
Flat-Vector Rollout (this session, CURRENT direction — COMPLETE for Phase-2 render layer, not yet committed)

* GOAL: restyle the render layer to a bright flat-vector infographic look (The Infographics Show) — solid flat colors, no gradient/grain/vignette, thick rounded shapes, bold geometric sans, animated flat charts/chips, colorful flat character fills (not black silhouettes).
* KEY ARCHITECTURE WIN: every template reads shared theme.ts + SceneFrame (lib/bits.tsx) — restyling those two files re-skins ALL 12 templates / all 68 scenes automatically, with ZERO scene-JSON edits for 8 of 12 templates (chart/comparison/list/timeline/quote/transition inherited the look for free, verified via stills).
* THEME/SHARED CHANGES: `render/package.json` += @remotion/google-fonts@4.0.484 (Poppins, weights 500/700/800). `lib/theme.ts` — flat palette (bg #123B6B navy, accent #FF9736 orange, accentAlt #FF5C5C coral, good #3DD68C green, text white); bgGradient is now a flat solid. `lib/bits.tsx` — SceneFrame: removed grain/glow/vignette, added 3 fixed (deterministic, non-random) flat decorative blob circles; OverlayText/SceneTitle restyled as flat solid pill/chip; NEW IconBadge. `lib/anim.ts` — NEW popIn() bouncy spring entrance (remotion spring(), damping 11/stiffness 140).
* TEMPLATES RESTYLED: TextEmphasis (spring pop-in, laurel→flat accent bar divider), StatCard (IconBadge + spring counter), IconGrid (flat colored chip squares), SilhouetteScene (flat solid ground bar; figure height bumped 420→560 to fix sparseness; intentionally never draws a background image behind figures — see in-code comment), MapScene (see below).
* CHARACTER ART (option b, resolved): figure-warrior/-emperor/-civilian.svg redrawn as v3 blocky flat-vector pictograms (rounded head/torso/limb blocks + simple accessories — crest+shield for warrior, laurel-arc+robe for emperor) — same ids/paths, CC0 project-original like v1/v2, manifest+LICENSES notes updated. FIXED both v2 problems: reads clearly upright AND mid-"fall"-rotation (flat-v3-s12-fall.png vs the old flat-s12-silhouette.png), and multi-figure group scenes (flat-v3-s26-warriors.png, 3 marching) compose well.
* MAP (resolved, 2 iterations): first tried a duotone color-blend tint over the grayscaled source map — REJECTED, it read as a vintage cream/parchment wash, not flat (see abandoned flat-s05-map.png). Second approach: grayscale the source map, mount it on a bordered flat white card (10px accent-orange border, 28px radius) so the neutral detailed atlas recedes as context while accent-colored pins/pulses/labels are the infographic layer on top (flat-v2-s05-map.png). Honest caveat: this is a pragmatic reuse of the existing complex PD atlas asset, not a true hand-simplified Infographics-Show-style continent map — that would need a new simplified basemap if pursued further.
* REMAINING TEMPLATES SPOT-CHECKED (all inherited flat style correctly, zero code changes): transition-break, chart-scene, comparison-split, quote-card, timeline-scene, list-reveal.
* VALIDATION: typecheck PASS, quality-gate PASS 0/0, manifest sync FRESH throughout — ZERO scene-JSON changes this entire session (only render code + 3 figure SVGs + manifest/LICENSES notes text).
* STILLS (draft comp, render/out/poc/): flat-s01-textemphasis, flat-s08-icongrid, flat-s11-statcard, flat-s03-timeline, flat-s06-listreveal, flat-s04-transition, flat-s18-chart, flat-s25-comparison, flat-s40-quote, flat-v3-s12-upright, flat-v3-s12-fall, flat-v3-s19-civilian, flat-v3-s26-warriors, flat-v2-s05-map.
Character Outline Recolor v4 (this session, FIFTH session — continues the approved flat-vector direction, no new design checkpoint needed)

* TRIGGER: user re-set the standing goal ("bring this automation's visual level up to The Infographics Show channel") via `/goal`. Assessed the shipped v3 flat-vector render against that bar and found one clear remaining gap: the v3 figure-warrior/-emperor/-civilian SVGs were single-fill `currentColor` silhouettes (same color for the whole body) — reads as a generic icon/pictogram, not a character. The Infographics Show's signature look is flat-colored body parts (skin tone + costume color) PLUS a dark outline stroke around every shape.
* FIX (recolor only, zero geometry change — same `d`/`rect`/`circle` coordinates, same ids/viewBox/paths as v1-v3, so no manifest/scene-JSON churn): each figure's `<g>` now sets a shared dark-navy outline (`stroke="#152A4D" stroke-width="4"`), head/limb shapes get a fixed warm skin tone (`#F0B285`), torso/robe keeps `currentColor` (still driven by `SilhouetteScene.tsx`'s existing `FIGURE_COLORS` per-type accent — warrior coral, emperor orange, civilian green), and neutral trim (leggings/sandals) gets fixed dark/brown tones. Emperor's laurel band is now fixed gold (`#D4AF37`) instead of the accent color. `SilhouetteScene.tsx` comment updated to describe the new fill contract (skin+outline baked into the asset; `color` prop now only tints the garment/crest/laurel-robe).
* VERIFIED visually via 3 fresh stills (render/out/poc/, gitignored): flat-v4-emperor (frame 9728, static), flat-v4-civilian (frame 3382, static), flat-v4-warriors (frame 4722, 3-figure march) — all read clearly as flat-colored, outlined characters, a strong step up from the v3 monochrome silhouettes.
* VALIDATION: tsc --noEmit PASS, manifest sync --check FRESH, quality-gate.py PASS 0/0 (QG block in outputs/.../STATUS.md refreshed by this run — timestamp only, no content changes).
* COMMITTED (58993c6) + pushed to origin/main (user confirmed via AskUserQuestion before push, per "ask before pushing" note).
* FULL CAPTIONED RE-RENDER completed to verify the fix in the actual deliverable, not just stills: GH Actions run 28717980285 (why-the-roman-empire-really-collapsed, burn-captions ON, crf 18) — success. Downloaded mp4: ffprobe 1920x1080 h264 30fps / ~2.07 Mbps, duration 422.19s (matches prior render). Extracted 3 frames from the encoded video itself (t=66.5s emperor mid-fall, t=111.5s civilian static, t=157.5s 3-warrior march) — the outlined multi-tone characters (skin tone + costume color + dark navy outline + gold laurel) render correctly in the final output, captions burn in cleanly with no overlap against the flat OverlayText pill. This supersedes GH Actions run 28716705909 as the current deliverable; the old run's artifact (2-day retention, already past due) still showed the v3 monochrome figures.

Caption-overlap fix (prior/third session)
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

1. DONE: user gave final sign-off ("onaylıyorum") on the full flat-vector look.
2. DONE: committed (a2a576d) + pushed to origin/main. (CORRECTION: the caption-overlap fix was NOT actually pending — it was already committed as 1472989 before this session started; a stale note from the third session's own TASKS.md draft had been carried forward uncorrected, verified via `git log`/`git show` this session and fixed.)
3. DONE: `gh` CLI installed (winget, GitHub.cli) + authenticated (`gh auth login --web`, account brsctncnbrk-ops) since it wasn't available in this environment. Full captioned re-render triggered and completed: GH Actions run 28716705909 (22m34s), slug why-the-roman-empire-really-collapsed, burn-captions ON, crf 18.
4. DONE: downloaded + verified the rendered mp4 — ffprobe: 1920x1080 h264, 30fps, ~1.75 Mbps video / ~317 kbps aac / ~2.07 Mbps total, duration 422.19s (matches the 7:00 target; lower bitrate than the old cinematic-style render is expected/good — flat color content compresses far more efficiently, not a quality regression). Extracted 3 frames (t=2s text-emphasis, t=25s map+caption, t=69s emperor-fall+caption) — flat-vector look confirmed in the actual encoded output (not just Remotion draft stills), and the caption-overlap fix holds under the new flat OverlayText pill style (clean gap, no overlap) at both caption-bearing frames checked.
5. STATUS.md updated to RENDERED + CAPTIONED, artifact link recorded (2-day retention from 2026-07-04).
6. NEXT (user/human step, not pipeline): Layer-2 checklist — title/thumbnail claim support (05A CTR notes flag the "payroll dispute" framing) + 05B Upload Checklist — then publish.
7. Housekeeping (low priority, not blocking): decor-laurel asset is no longer referenced anywhere (TextEmphasis dropped the laurel divider for a flat accent bar) — decide whether to remove it from the library or leave it for possible future reuse. If the user wants to go further than the current map-scene treatment (grayscale-on-flat-card), a genuinely simplified flat basemap would need to be sourced/drawn as a new asset. Also decide whether to commit+push the STATUS.md update from this step.
8. DONE (FIFTH SESSION): character outline recolor v4 committed (58993c6), pushed, and re-rendered — GH Actions run 28717980285, verified via extracted frames from the actual mp4 (see "Character Outline Recolor v4" section above). The current deliverable mp4 (from this run) is the one to publish, not the earlier 28716705909 artifact.
9. NEXT: download the run-28717980285 artifact locally for final human review (it was fetched to a scratch dir for verification this session, not saved into the repo/outputs — download fresh from https://github.com/brsctncnbrk-ops/FactForge/actions/runs/28717980285 before publishing, mind the 2-day artifact retention). Then proceed with the still-pending human Layer-2 checklist (step 6 above).
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

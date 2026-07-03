TASKS — Session Handoff
Current Phase
Phase 1E — Example Topic Output (completed). Phase 1 is DONE. Next: user decision on Phase 2 (/render) — never start it unprompted (CLAUDE.md).
Design approved
n/a (Phase 1E has no design checkpoint per Session Protocol rule 5)
Completed This Session

* Committed phase-1d work as `a3280cb phase-1d complete` (1C+1D landed together as anticipated; the pre-existing 01-research.md was excluded and lands with 1E).
* Phase 1E production run for `outputs/why-the-roman-empire-really-collapsed/`:
  * 01-research.md was already present (prior session); built 01-facts.json from it — 32 sources, 26 facts (23 VERIFIED, F008 SINGLE-SOURCE report-only, F026 VERIFY excluded). Validates against facts-file.schema.json.
  * 02-script-annotated.md — 68 scenes, 1,008 words (~6:43 @150wpm; budget ~1,000–1,100), max scene 19 words. Only VERIFIED facts used; every on-screen number backed by a VERIFIED scriptCritical fact.
  * 02-script-voiceover.txt via derive_vo.py — clean run, all 68 declared word counts match, zero warnings.
  * 03-scenes.json — all 68 scenes mapped to the 12 catalog templates (no TEMPLATE-GAPS entries needed). validate.py --bootstrap: PASS, 0 warnings. 5 distinct newAssets (library empty / bootstrap): map-roman-empire, icon-soldier, figure-warrior, figure-emperor, figure-civilian — exactly at the 5 cap.
  * 04-scenes-final-estimated.json via align.py --mode wordcount — 403.2s total, no LONG/SHORT warnings.
  * 05-packaging.md (05A only) — incl. Script Hook Promise; all packaging numbers carry VERIFIED fact IDs in HTML comments; "payroll dispute" title framing flagged for the human checklist.
  * Hook Promise Audit in 02-script-annotated.md updated PENDING → PASS after 05A (targeted edit of the audit section only).
  * STATUS.md created from template; quality-gate.py wrote the QG block.
Files Created

* outputs/why-the-roman-empire-really-collapsed/: 01-facts.json, 02-script-annotated.md, 02-script-voiceover.txt, 03-scenes.json, 04-scenes-final-estimated.json, 05-packaging.md, STATUS.md
Files Modified

* outputs/why-the-roman-empire-really-collapsed/02-script-annotated.md (audit section), STATUS.md (QG block by gate), TASKS.md (this file)
Commands Run

* git commit phase-1d; jsonschema validation of 01-facts.json; derive_vo.py; validate.py --bootstrap; align.py --mode wordcount; sync_manifest_usage.py --check (FRESH); quality-gate.py
Validation Results

* quality-gate.py: PASS — 0 failures, 1 warning (TC2: only estimated timing exists; voiced final render not allowed — expected at this stage, per the 1E prompt).
* derive_vo diff OK; 03 + 04 schema/scene checks OK; VERIFY violations 0; scriptCritical all VERIFIED; number-without-fact warnings 0; BLOCKED/Unknown 0; attribution not needed; sync fresh.
Blockers

* NONE. Voiced pipeline fully complete (post-1E session, 2026-07-03): user supplied audio/voiceover.mp3 (10.1MB, 422.13s); faster-whisper 1.2.1 + rapidfuzz 3.14.5 installed into the working interpreter; align.py Mode A initially rejected (min scene 0.54 — Whisper wrote digits "400 000"/"90" vs spelled-out VO words); fixed by making align.py matching number-robust (symmetric digit→words expansion in normalize_words; coverage thresholds UNTOUCHED; +4 self-test checks, 21/21 PASS); re-run → Mode A accepted: coverage 0.985, min scene confidence 0.80, no LONG/SHORT, total 7:02 → 04-scenes-final.json. 05B appended to 05-packaging.md (final description with chapter timestamps from real timings, final tags/pinned comment, Attribution Block "None required" — all assets PD/CC0, Upload Checklist). FINAL GATE: PASS — 0 failures, 0 warnings; "voiced final render allowed: yes".
ASSETS — RESOLVED (2026-07-03, post-1E session; repo pushed to GitHub as brsctncnbrk-ops/FactForge, branch main)

All 5 assets sourced/created and registered in manifest.json + LICENSES.md; 03-scenes.json switched to fromLibrary (newAssets empty everywhere); sync_manifest_usage.py wrote usedInVideos; validate.py PASS **without --bootstrap**; align.py re-run; quality-gate.py PASS (only the expected TC2 estimated-timing warning).

| id | file | license |
|---|---|---|
| map-roman-empire | assets/library/maps/map-roman-empire.svg | Public domain — Wikimedia Commons "RomanEmpire 117.svg" (verified via Commons API extmetadata) |
| icon-soldier | assets/library/icons/icon-soldier.svg | CC0 — project-original (simple v1) |
| figure-warrior | assets/library/figures/figure-warrior.svg | CC0 — project-original (simple v1) |
| figure-emperor | assets/library/figures/figure-emperor.svg | CC0 — project-original (simple v1) |
| figure-civilian | assets/library/figures/figure-civilian.svg | CC0 — project-original (simple v1) |

Silhouettes/icon are deliberately minimal placeholder-quality vectors with real licenses; upgrade them later under the SAME manifest ids (no scene churn).
Next Exact Step
Phase 1 is FULLY complete (research → script → scenes → real-audio timing → packaging 05A+05B → gate PASS 0/0). Record /usage in Quota Notes. The ONLY remaining decision: Phase 2 (/render — Remotion components + render pipeline). Per CLAUDE.md this needs the user's explicit request; Claude must not start it on its own. All render inputs are ready: 04-scenes-final.json (transcript-guided, min conf 0.80), audio/voiceover.mp3, 5 licensed assets in /assets/library, 05-packaging.md complete.
Quota Notes

* Phase 0: before __% -> after __% (kullanıcı doldurur)
* Phase 1A: before 61% (5h) / 13% (weekly) -> after __% (kullanıcı doldurur)
* Phase 1B: before __% -> after 97% (5h) / 17% (weekly) (pasted /usage, previous session)
* Phase 1C: before __% -> after __% (kullanıcı doldurur)
* Phase 1D: before __% -> after __% (kullanıcı doldurur)
* Phase 1E: before __% -> after __% (kullanıcı doldurur)
Notes

* PYTHON: `python` on PATH is BROKEN; use `C:\Users\brsct\AppData\Local\Programs\Python\Python314\python.exe` (jsonschema 4.26.0 installed). faster-whisper / rapidfuzz still NOT installed — needed before the first real audio alignment (align.py Mode A).
* Voiced-final rule: 04-scenes-final-estimated.json is never a voiced-render input; after voiceover.mp3 lands, re-run align.py (Mode A) → 04-scenes-final.json, append 05B (attribution as needed), re-run quality-gate.py.
* The 5 new assets must enter manifest.json WITH license metadata + LICENSES.md before final render; usedInVideos is sync-script-only (currently fresh — all scene assets are newAssets, none fromLibrary).

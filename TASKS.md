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

* None for Phase 1. Voiced render path blocked on user inputs: audio/voiceover.mp3 (ElevenLabs, from 02-script-voiceover.txt) + faster-whisper install + sourcing the 5 new assets with licenses into manifest.json/LICENSES.md, then 05B.
NEW ASSETS REQUIRED — why-the-roman-empire-really-collapsed

| id | what it is | scenes | suggested free source |
|---|---|---|---|
| map-roman-empire | vector empire map (provinces, E/W split layers) | 5, 13, 14, 24, 29, 31, 34, 45, 46, 49, 58, 65 | Wikimedia Commons (CC0/PD) |
| icon-soldier | minimal soldier icon | 7, 8, 51 | CC0 icon set (SVG Repo) |
| figure-warrior | generic warrior silhouette | 26, 27, 30, 38, 55, 57, 59 | CC0 silhouette pack / self-drawn |
| figure-emperor | robed emperor silhouette | 12, 30, 53 | CC0 silhouette pack / self-drawn |
| figure-civilian | civilian silhouette | 19, 22, 61 | CC0 silhouette pack / self-drawn |

Total new assets: 5 / 5 (bootstrap: yes)
Next Exact Step
Run `git add -A && git commit -m "phase-1e complete"` + record /usage in Quota Notes. Then review the PRODUCT (per WORKFLOW "Sen neyi kontrol et (1E)": fact quality, hook strength, template fit) and decide on Phase 2 (/render) — Claude must not start it on its own.
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

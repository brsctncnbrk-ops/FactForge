# Production Status

## Video Info

Video Slug: why-the-roman-empire-really-collapsed
Video Topic: Why the Roman Empire Really Collapsed
Target Language: English
Target Length: 7 minutes
Current Stage: RENDERED (first full render 2026-07-04 with CRF 22/jpeg intermediates — superseded by CRF 18/png settings; captioned re-render recommended before upload)
Last Updated: 2026-07-04

## Completed Stages

- [x] 01 Research
- [x] 02 Script
- [x] 03 Visual Scene JSON
- [x] 04 Timing Sync (Mode A transcript-guided-alignment on real audio)
- [x] 05 Packaging (05A)
- [x] 05 Packaging (05B)
- [x] Quality Gate
- [x] 06 Render (first full mp4 2026-07-04; re-render pending: CRF 18/png encoding + burned-in captions were added after it)

## Generated Files

- [x] 01-research.md
- [x] 01-facts.json
- [x] 02-script-annotated.md
- [x] 02-script-voiceover.txt
- [x] 03-scenes.json
- [x] audio/voiceover.mp3
- [x] 04-scenes-final.json
- [x] 04-scenes-final-estimated.json (superseded draft; kept as Mode B artifact)
- [x] 05-packaging.md
- [x] 05-captions.json / 05-captions.srt / 05-captions.vtt (148 cues; build_captions.py)

## Quality Gate

<!-- QG:BEGIN — bu blok quality-gate.py tarafından üretilir, elle düzenleme -->
Gate Result        : PASS (0 failure(s), 0 warning(s))
Gate Run           : 2026-07-04 21:52 | bootstrap: no
Validation Status  : derive_vo diff: OK | 03-scenes.json: OK | 04-scenes-final.json: OK | 04-scenes-final-estimated.json: OK
Fact Status        : 24 fact(s) used | VERIFY-status violations: 0 | scriptCritical all VERIFIED: yes | number-without-fact warnings: 0
Asset Status       : 5 library asset(s), 0 new | BLOCKED/Unknown violations: 0 | attribution: not needed | usedInVideos sync: fresh
Timing Status      : timingMode: transcript-guided-alignment | audio file present: yes | min scene confidence: 0.8 | voiced final render allowed: yes

Failures:
- none
Warnings:
- none
<!-- QG:END -->

## Current Blocking Issues

- None

## Warnings

- None. Mode A alignment: global coverage 0.985; per-scene confidence min 0.80 (scenes 7/16/18 in the 0.85–0.87 band — Whisper heard digits/"daenerius"; matching made number-robust in align.py, thresholds untouched). No LONG/SHORT scenes. Real total 422.13s (7:02) vs 7:00 target.

## Required User Action

- None for the pipeline. Human Layer-2 checklist before publishing: title/thumbnail claim support (see 05A CTR notes — "payroll dispute" framing flagged), and the Upload Checklist in 05B.

## Next Step

Re-render via GitHub Actions with the improved encoding (CRF 18 / png intermediates) — tick `burn-captions` for embedded subtitles, or upload 05-captions.srt to YouTube alongside the clean `video` render. Then the human Layer-2 checklist (title/thumbnail claim support + 05B Upload Checklist) before publishing.

## Session Notes

Current Phase: post-render QA (2026-07-04): encoding fix (png/CRF 18), captions layer (SRT/VTT/JSON + video-captioned comp), repo hygiene — details in TASKS.md
Previous Phase: 1E complete + post-1E finalization (assets, real audio alignment, 05B)
Completed This Session: 01-facts.json, 02-script-annotated.md, 02-script-voiceover.txt, 03-scenes.json, asset library seeded (5 licensed assets; scenes switched to fromLibrary), faster-whisper+rapidfuzz installed, align.py number-robust matching fix (+4 self-test checks, 21/21 PASS), 04-scenes-final.json via Mode A (coverage 0.985), 05-packaging.md 05A+05B, quality-gate PASS 0/0
Files Created: full output set + 5 asset files
Files Modified: align.py (digit-to-words normalization in matching — symmetric, thresholds unchanged), 03-scenes.json (fromLibrary), manifest.json, LICENSES.md
Commands Run: derive_vo.py, validate.py, align.py (wordcount → auto/Mode A), sync_manifest_usage.py, quality-gate.py (final: PASS 0 failures 0 warnings), align.py --self-test (21/21)
Blockers: none
Next Exact Step: user decides on Phase 2 (/render); record /usage in TASKS.md Quota Notes

## Quota Notes

İlk 2-3 videoda her aşama için /usage öncesi/sonrası kaydı:
- Phase 1E (full pipeline, one session): before __% → after __% (kullanıcı doldurur)

## Notes

- Script: 68 scenes, 1,008 words (target ~1,000–1,100 for 7 min), max scene 19 words (cap 30).
- Facts: 26 registered (23 VERIFIED, 1 SINGLE-SOURCE report-only, 1 VERIFY excluded, 1 quote fact); script and packaging use VERIFIED facts only.
- No template gaps: all 68 scenes mapped to the 12 catalog templates without needing TEMPLATE-GAPS.md entries.

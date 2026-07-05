# /render — Phase 2 Render Layer (Remotion)

Not a skill. The 16 scene templates are coded ONCE as Remotion components;
after that every video is JSON-only (props from `04-scenes-final.json`).
TypeScript prop types are GENERATED from `/templates/schemas` (P8) — never
edit `src/types/generated/*` by hand; run `npm run gen`.

## Commands

```bash
npm ci                 # install (Node 20+)
npm run gen            # /templates/schemas/*.schema.json -> src/types/generated/
npm run stage -- <slug># copy assets + 04-*.json + audio into ./public (throwaway)
npm run studio         # local preview (silent; use the "draft" composition)
npm run typecheck
```

## Compositions

- `video` — voiced final render. Loads `outputs/<slug>/04-scenes-final.json`
  and REFUSES (hard error in `src/lib/data.ts`) unless `timingMode` is
  `forced-alignment` or `transcript-guided-alignment`. Audio is mounted here
  and in `video-captioned` only.
- `video-captioned` — same as `video` plus burned-in subtitles. Additionally
  REFUSES unless `outputs/<slug>/05-captions.json` exists — generate it with
  `python scripts/build_captions.py <slug>` (also emits the SRT/VTT sidecars
  for YouTube), then re-run `npm run stage -- <slug>`.
- `draft` — silent preview; falls back to `04-scenes-final-estimated.json`
  when no final file exists. Never mounts audio.

Slug is an input prop:
`npx remotion still video out/x.png --frame=700 --props='{"slug":"<slug>"}'`

## Full renders run in the cloud

Local machine only does stills / short `--frames` test segments (4 GB RAM;
a full 7-min 1080p30 render takes ~60-90 min anywhere). Full render:
GitHub Actions → workflow "render" → Run workflow → enter the video slug
(tick "burn-captions" to render the `video-captioned` composition).
`quality-gate.py` runs first and a FAIL stops the render. The mp4 artifact
has retention-days: 2 — download it promptly.

Encoding: PNG intermediate frames + CRF 18 (set in `remotion.config.ts`) — a
visually lossless master so YouTube's re-encode starts from clean input.

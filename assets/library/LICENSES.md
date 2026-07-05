# Asset Licenses

Source and license notes for every asset in `/assets/library`. The machine record is `manifest.json`; this file holds the human-readable notes and source-level license documentation.

## Rules (binding, from the brief + patch Section 9)

1. No asset enters the library without a `license` value in `manifest.json`.
2. `license: "Unknown"` → `status: "BLOCKED"` automatically. BLOCKED assets may not appear in any `03-scenes.json`.
3. `attributionRequired: true` assets are reported to 05B Publishing Finalization (Attribution Block).
4. Remote URLs may not be used directly in final render JSON — assets must be downloaded, licensed, and added to the library first.
5. `usedInVideos` is maintained by `/scripts/sync_manifest_usage.py` only — never hand-edited.

## Source License Notes

| Source | License | Attribution | Notes |
|---|---|---|---|
| Wikimedia Commons | Public domain (per file page) | Not required | License verified per file via the Commons API (`extmetadata.LicenseShortName`) at download time; verification date noted in each asset's manifest `notes`. |
| Project original (FactForge in-house vectors) | CC0 | Not required | Simple flat SVG silhouettes/icons drawn for this project; freely reusable across videos. |

## Per-Asset Notes

- **map-roman-empire** — `File:RomanEmpire_117.svg` by ArdadN (English Wikipedia), Public domain. Source page: https://commons.wikimedia.org/wiki/File:RomanEmpire_117.svg — verified 2026-07-03 via Commons API. No attribution required (credit kept here as a courtesy).
- **icon-soldier, figure-warrior, figure-emperor, figure-civilian** — project-original CC0 SVGs. Figures upgraded to detailed v2 silhouettes on 2026-07-04, then redrawn again the same day as v3 blocky flat-vector pictograms (rounded head/torso/limb blocks) to fit the flat-infographic render style — the fine v2 detail didn't survive rotation transforms or small render sizes. Recolored again the same day as v4: skin/costume/trim tones + a dark outline stroke per shape, matching the Infographics-Show "flat color + black outline" character look (v3 was a flat single-fill silhouette). All under the SAME ids/paths (scene files untouched); icon-soldier remains v1 (small chip/badge icon, not a hero character — single-fill currentColor is correct at that scale and matches how the reference channel treats small icons too).
- **decor-laurel** — project-original CC0 laurel-branch ornament (2026-07-04). Referenced directly by render template code (text-emphasis divider), not by scene JSONs, so `usedInVideos` legitimately stays empty.
- **icon-warning, icon-coin, icon-document, icon-megaphone** — project-original CC0 SVGs added 2026-07-05 for the new flow-diagram/scale-comparison/evidence-board/news-briefing templates and general non-Roman icon-grid use. `usedInVideos` is empty until a video actually references them (expected — none exist yet for the second video).
- **map-world-generic** — project-original CC0 SVG added 2026-07-05: simplified/schematic world continent shapes (not traced from a real atlas, not politically accurate — deliberately stylized so it never overclaims precision). Closes the gap left by map-roman-empire being the only map asset in the library; map-scene's grayscale+card treatment and generic north/south/east/west/center placements already supported non-Roman use, only the asset itself was missing.
- **figure-civilian genericness correction (2026-07-05)** — re-examining the actual SVG geometry found it has no period-specific styling at all (plain rounded torso, no crest/toga/shield like figure-warrior/figure-emperor). It was mistakenly treated as Roman-only in an earlier gap analysis; tags/notes updated in manifest.json to reflect it's genuinely reusable as a generic person silhouette for any topic. No SVG changes — same id/paths, so no scene JSON is affected.

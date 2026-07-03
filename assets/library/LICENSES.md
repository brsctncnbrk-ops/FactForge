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
- **icon-soldier, figure-warrior, figure-emperor, figure-civilian** — project-original CC0 SVGs (v1, deliberately minimal). Replace freely later; keep the manifest `id` stable so scene files don't churn.

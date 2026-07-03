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
| _(none yet)_ | | | |

## Per-Asset Notes

_(none yet — add an entry here when an asset needs licensing context beyond its manifest fields)_

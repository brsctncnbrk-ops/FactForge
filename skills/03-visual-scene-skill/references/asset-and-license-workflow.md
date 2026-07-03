# Asset & License Workflow

Canonical manifest: `/assets/library/manifest.json` (schema and rules: brief 03 section + patch Sections 8–9). License notes live in `/assets/library/LICENSES.md`.

## Per-scene procedure

1. **Library first (P3).** Search the manifest by `tags` and `type` before imagining a new asset. An existing ACTIVE asset always wins over a new one, even if slightly less ideal.
2. Assets found in the library go into `assets.fromLibrary` (manifest `id` strings).
3. Assets the library lacks go into `assets.newAssets` as objects:

```json
{ "id": "map-mediterranean-trade-routes",
  "description": "Simple vector map of Mediterranean trade routes, 2nd century",
  "suggestedSource": "Wikimedia Commons (CC0/PD search)" }
```

   - `id` is kebab-case, prefixed by type (`map-`, `icon-`, `bg-`, `img-`, `figure-`, `texture-`).
   - The same new asset reused in several scenes keeps the SAME id (it counts once against the cap).
4. Never reference a remote URL in props — assets enter the library (downloaded, licensed, manifest entry) before any final render JSON may use them.

## Hard rules (validate.py enforces)

- Every props asset reference must be declared in that scene's `fromLibrary`/`newAssets`; every `fromLibrary` id must exist in the manifest.
- `status: BLOCKED` or `license: Unknown` assets are NEVER usable — no flag relaxes this.
- Distinct `newAssets` ids per video: ≤ 5. During library bootstrap (first 1–3 videos) run validate.py with `--bootstrap`: the cap becomes a warning, but every new asset must still be reusable (`reusable: true`), licensed, and added to the manifest + LICENSES.md. After bootstrap, over-cap means revising scenes to reuse library assets — not raising the cap.
- `attributionRequired: true` assets used → 05-packaging (05B) must carry an Attribution Block; until 05-packaging.md exists this is a pending warning, enforced finally by quality-gate.py.
- `usedInVideos` is written by `scripts/sync_manifest_usage.py` ONLY. If validate.py warns it is stale, run the sync script — never hand-edit the field.

## NEW ASSETS REQUIRED report

At the end of the run, output (in chat — it is not a pipeline file) one consolidated section so the human can source assets in a single pass:

```markdown
# NEW ASSETS REQUIRED — {video-slug}

| id | what it is | scenes | suggested free source |
|---|---|---|---|
| map-mediterranean-trade-routes | vector trade-route map | 4, 11 | Wikimedia Commons |

Total new assets: N / 5 (bootstrap: yes/no)
```

Each sourced asset is then added to `manifest.json` **with license metadata** (license, attributionRequired, attributionText, sourceUrl) and to `LICENSES.md` before final render. An asset added without a license field is invalid; `Unknown` license auto-BLOCKs it.

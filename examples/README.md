# Examples

Minimal reference inputs for starting a new video. Copy-paste and adapt.

## Example topic prompt (Phase 1E, full pipeline)

```
Read TASKS.md. Run Phase 1E for a new video:

Topic: Why the Roman Empire Really Collapsed
Slug: why-the-roman-empire-really-collapsed
Target language: English
Target length: 7 minutes
Angle: the fall was administrative/fiscal, not a single dramatic battle
```

The pipeline then produces, in order, under `outputs/<slug>/`:
`01-research.md` + `01-facts.json` → `02-script-annotated.md` + `02-script-voiceover.txt`
→ `03-scenes.json` → (record voiceover, run align.py) → `04-scenes-final.json`
→ `05-packaging.md` → quality gate PASS in `STATUS.md`.

## Phase commands cheat-sheet

| When | Command |
|---|---|
| After script | `python skills/02-script-skill/scripts/derive_vo.py <slug>` |
| After scenes | `python skills/03-visual-scene-skill/scripts/validate.py <slug>` |
| After voiceover | `python skills/04-timing-sync-skill/scripts/align.py <slug>` |
| Captions | `python scripts/build_captions.py <slug>` |
| Before render | `python scripts/sync_manifest_usage.py <slug>` then `python scripts/quality-gate.py <slug>` |

## Reference output

A complete Phase 1 output set lives in
[`outputs/why-the-roman-empire-really-collapsed/`](../outputs/why-the-roman-empire-really-collapsed/)
— use it as the shape reference for every artifact.

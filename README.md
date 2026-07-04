# FactForge — YouTube Production Skill System v2.1.1

Pipeline for producing infographic-style documentary YouTube videos:
**5 Core Skills** (research → script → scenes → timing → packaging) + a **Remotion render layer** (Phase 2).
Deterministic work lives in scripts; the LLM only does judgment work (principle P7).

## Binding documents

- [PROJECT-BRIEF-v2.1.md](PROJECT-BRIEF-v2.1.md) and [STABILIZATION-PATCH-v2.1.1.md](STABILIZATION-PATCH-v2.1.1.md)
  (on conflict: P1–P8 principles > patch > brief).
- Project rules for Claude Code: [CLAUDE.md](CLAUDE.md)
- Phase execution guide (human): [WORKFLOW.md](WORKFLOW.md)
- Session handoff / current state: [TASKS.md](TASKS.md)

## Repo layout

| Path | What it is |
|---|---|
| `skills/` | The 5 core skills (SKILL.md + their deterministic scripts) |
| `templates/schemas/` | JSON Schemas — machine source of truth (P8) |
| `templates/` | Template catalog and shared references |
| `assets/library/` | Licensed reusable assets + `manifest.json` + `LICENSES.md` |
| `outputs/<video-slug>/` | Per-video artifacts (research, script, scenes, timing, packaging, STATUS.md) |
| `scripts/` | Cross-cutting scripts: `quality-gate.py`, `sync_manifest_usage.py`, `build_captions.py` |
| `render/` | Phase 2 Remotion project (see [render/README.md](render/README.md)) |
| `.github/workflows/` | `render.yml` (cloud render), `selftest.yml` (script self-tests) |

## Setup

Prerequisites: Python 3.12+ and Node 20+ (render layer only).

```
python -m pip install -r requirements.txt   # jsonschema (+ faster-whisper/rapidfuzz for Mode A)
cd render && npm ci                         # only if you will render
```

> Windows note: if `python` on PATH is broken, call the interpreter by full path
> (e.g. `C:\Users\<you>\AppData\Local\Programs\Python\Python314\python.exe`).

## Producing a video (command order)

Phases are driven through Claude Code prompts (see [WORKFLOW.md](WORKFLOW.md)); the
deterministic checkpoints in between are:

```
# after 02-script:
python skills/02-script-skill/scripts/derive_vo.py <video-slug>

# after 03-scenes:
python skills/03-visual-scene-skill/scripts/validate.py <video-slug>

# after recording voiceover (Mode A alignment):
python skills/04-timing-sync-skill/scripts/align.py <video-slug>

# captions (SRT/VTT sidecars from the aligned scenes):
python scripts/build_captions.py <video-slug>

# asset bookkeeping + final gate:
python scripts/sync_manifest_usage.py <video-slug>
python scripts/quality-gate.py <video-slug>
```

Every script also supports `--self-test`. The quality gate writes the QG block in
`outputs/<slug>/STATUS.md`; a FAIL blocks rendering.

## Rendering (Phase 2)

- Local draft/stills: see [render/README.md](render/README.md) (`npm run gen`, `npm run stage -- <slug>`, Remotion Studio).
- Full render: GitHub → Actions → **render** → Run workflow → `video-slug`.
  The workflow re-runs the quality gate first; artifact retention is 2 days.
- The voiced composition refuses to render unless timing comes from real-audio
  alignment (`04-scenes-final.json`) — this guard must never be weakened.

## Content integrity (short version)

- Facts live in `outputs/<slug>/01-facts.json`; scriptCritical facts must be VERIFIED.
- Never use BLOCKED/Unknown-license assets; `usedInVideos` in the manifest is
  script-maintained only.
- Before publishing, run the human Layer-2 checklist in `05-packaging.md`
  (title/thumbnail claim support is a human judgment, not a gate check).

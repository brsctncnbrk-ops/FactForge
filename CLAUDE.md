YouTube Production Skill System v2.1.1 — Project Rules
Documents & Precedence

* Binding documents: PROJECT-BRIEF-v2.1.md and STABILIZATION-PATCH-v2.1.1.md.
* On conflict: P1–P8 principles > STABILIZATION-PATCH-v2.1.1.md > rest of the brief > SKILL.md files.
System Boundaries

* This is a 5 Core Skills + Render Layer system. 06-Render is NOT a skill; it belongs to Phase 2.
* Never implement /render, Remotion components, or GitHub Actions workflows unless the user explicitly requests Phase 2.
* Work only on the phase the user explicitly requests. Never implement everything in one pass.
Session Protocol (every session)

1. Read TASKS.md first. Do not re-read the whole project; read only the sections of the brief and the patch relevant to the current phase.
2. For phases 1A–1D: before writing ANY file, present a compact DESIGN SUMMARY (WORKFLOW.md defines what each phase's summary must contain), then STOP and wait.
3. Do not create or modify files until the user replies with the word "ONAY". Feedback without "ONAY" means: revise the summary only.
4. If TASKS.md says "Design approved: yes" for the current phase, skip the summary and continue implementation directly.
5. Phase 1E has no design checkpoint; it is production output.
6. If the user says "stop now": write current state + next exact step to TASKS.md and stop immediately.
End of Session (mandatory)

* Run available validation scripts and report results.
* Update TASKS.md: current phase, design approved yes/no, files created/modified, commands run, validation results, blockers, Next Exact Step.
* Then stop. Never start the next phase on your own.
Engineering Rules

* Deterministic work goes to scripts, never to the LLM (P7): derive_vo.py, validate.py, align.py, quality-gate.py, sync_manifest_usage.py.
* /templates/schemas is the machine source of truth (P8). Fact records live in 01-facts.json (facts-file.schema.json), not in markdown.
* Never duplicate schemas or catalogs inside skill folders; reference /templates by path.
* SKILL.md bodies < 500 lines; long examples go to /references. Keep this file < 200 lines.
* Never regenerate large JSON files when a targeted scene-level edit suffices.
* Never weaken, bypass, or delete validation/gate checks to make them pass.
* No placeholder logic without a clear TODO marker. Never silently skip files.
Content Integrity Rules

* Never invent sources or facts. Unknown values are marked TBD.
* VERIFY facts never appear outside 01-research.md / 01-facts.json.
* SINGLE-SOURCE facts: minor supporting claims only — never numbers, stat-cards, chart data, main claims, or packaging claims. Patch Section 6 is the single canonical table; do not restate or reinterpret it elsewhere.
* scriptCritical facts must be VERIFIED before use.
* Never use BLOCKED or Unknown-license assets.
* usedInVideos in manifest.json is maintained by sync_manifest_usage.py only; never hand-edit it.
* quality-gate.py writes the QG block in STATUS.md between the QG markers; judgmental checks (e.g. title/thumbnail claim support) belong to the human checklist, never to quality-gate.py.

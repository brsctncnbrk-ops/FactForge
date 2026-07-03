---
name: 01-research-skill
description: Use this skill whenever the user mentions a video topic, asks for research for a video, starts the production pipeline, or asks for 01-research.md / 01-facts.json. It researches the topic into a verified, source-backed Research Report (01-research.md) plus a machine fact registry (01-facts.json with S/F IDs and VERIFIED / SINGLE-SOURCE / VERIFY statuses), within a hard budget of 15 web searches. It never writes the video script — it produces the raw material for 02-script-skill.
---

# 01-research-skill

Research the given video topic and build a solid, **verifiable** knowledge base for script writing. This skill does not write video narration; it researches, organizes, and hands quality raw material to 02-script-skill.

## Outputs (both, same pass)

1. `/outputs/{video-slug}/01-research.md` — human document: narrative, timeline, hook ideas, structure suggestion. References facts by ID in prose (e.g. "military costs strained the budget (F002)").
2. `/outputs/{video-slug}/01-facts.json` — canonical machine registry of all sources and facts. Schema: `/templates/schemas/facts-file.schema.json` (P8 — validate against it). On conflict, 01-facts.json wins. quality-gate.py reads ONLY the JSON, never the markdown.

Read `references/output-format-and-examples.md` before producing either file for the exact section list, formats, and worked examples.

## Working modes

```text
If user provided sources AND web search available → Hybrid (manual first, web fills gaps + second sources)
If user provided sources only                     → Manual Source Mode
If web search available only                      → Web Search Mode
If no sources and no web search                   → Research Request Output (facts are NEVER invented)
```

Read `references/research-modes.md` when selecting a mode, when the user supplies sources, or when no sources are available. If the user pastes NotebookLM output, read `references/notebooklm-workflow.md` first.

## ID assignment rules (binding)

1. Every source gets an S-ID (`S001`, `S002`, ...) in order of first use; every Key Fact gets an F-ID (`F001`, `F002`, ...) in report appearance order. Zero-padded, 3 digits.
2. IDs are NEVER renumbered or reused after assignment. Later edits append new IDs; removed facts keep their ID slot retired.
3. A fact without a source cannot enter the JSON as anything but `status: "VERIFY"` with empty `sources` (an explicit "unresolved" record).

## Verification rules (binding)

1. **Every Key Fact carries a source.** Sourceless facts cannot appear in the output.
2. **Narrowed dual-source rule:** only **script-critical numbers** — numeric data that will appear in narration or on screen (stat-card, chart-scene) — require ≥ 2 independent sources. Other supporting numbers may stay single-sourced with a reliability note, marked `[SINGLE-SOURCE]` in the report. If the script wants a single-sourced number: run a targeted second-source search within budget; if not found, the number becomes `[VERIFY]` and stays out of the script.
3. **Search budget: max 15 web searches per video**, including second-source searches. Track the count live; record `searchesUsed` and `searchBudget` in 01-facts.json. When the budget is exhausted, remaining unverified claims are marked `[VERIFY]` and listed under Missing Sources.
4. **Anything uncertain gets `[VERIFY]`.** Usage constraints for VERIFY and SINGLE-SOURCE facts are defined ONLY by STABILIZATION-PATCH-v2.1.1.md Section 6 (canonical table — never restate or reinterpret it).
5. **Source Notes section is mandatory**, with a reliability note per source (academic / institutional / encyclopedic / popular / weak).

## Fact field rules (01-facts.json)

- `status`: VERIFIED (≥ 2 independent sources) | SINGLE-SOURCE (exactly 1 + reliability note) | VERIFY (unresolved). The schema machine-enforces source counts per status.
- `scriptCritical: true` = numbers that will appear in narration/on screen AND the video's main claims. scriptCritical facts MUST be VERIFIED (schema-enforced) — otherwise find a second source or keep the fact out of the script.
- `isNumber`: `true` when the claim contains numeric data — quantities, percentages, counts, monetary values. Bare year/date references ("in 476 CE") do NOT set isNumber. An isNumber fact intended for script use must be VERIFIED.
- The literal texts `[VERIFY]` and `[SINGLE-SOURCE]` may exist ONLY in 01-research.md and 01-facts.json (patch Section 6, Literal Tag Rule).

## Research depth

Research must not be superficial. Find interesting, surprising, curiosity-holding details usable in the video. For "Why the Roman Empire Really Collapsed", "barbarian invasions" alone is insufficient: economy, army cost, political instability, inflation, border security, internal decay, and effects on ordinary people must be covered.

## Quality criteria

- No invented information — the verification rules above are the mechanism.
- Rich enough to be converted into a video script.
- Story-friendly fact selection, not encyclopedia prose.
- Search budget respected and the count reported.
- 01-facts.json validates against `/templates/schemas/facts-file.schema.json`.

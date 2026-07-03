# 01-research-skill — Output Format and Examples

## 01-research.md — required sections (in order)

```text
1. Topic Summary
2. Core Story Angle
3. Key Facts (each with source + fact ID)
4. Timeline / Sequence of Events
5. Important Characters, Groups, Countries, or Institutions
6. Numbers, Data, and Statistics (script-critical ones dual-sourced)
7. Common Misconceptions
8. Surprising Details
9. Conflict / Tension Points
10. Possible Hook Ideas
11. Suggested Video Structure
12. Source Notes (mandatory, with reliability notes)
13. Missing Sources (conditional — only if unresolved claims exist)
```

## 01-research.md — format template

```markdown
# Research Report

## Topic Summary
Short explanation of the topic.

## Core Story Angle
The main narrative angle of the video.

## Key Facts
- Fact 1 (F001) — [Source: URL]
- Fact 2 (F002) — [Source: URL]
- Fact 3 (F003) [VERIFY] — single source found, second source could not be verified

## Timeline / Sequence
1. Event (F004) — [Source: URL]
2. Event (F005) — [Source: URL]

## Numbers, Data, and Statistics
- Statistic (F006) — [Sources: URL1, URL2]            ← script-ready (dual-sourced)
- Statistic (F007) — [Source: URL1] [SINGLE-SOURCE]   ← report-only; needs a second
                                                        source before entering script

## Surprising Details
- Detail 1 (F008) — [Source: URL]

## Hook Ideas
1. Hook idea
2. Hook idea
3. Hook idea

## Suggested Video Structure
- Intro
- Problem setup
- Main story
- Turning point
- Final lesson

## Source Notes
1. S001 — URL — source type, reliability assessment
2. S002 — URL — source type, reliability assessment

## Missing Sources (conditional)
- Claim: ...
  Status: [VERIFY]
  Needed Source Type: ...
```

Notes:

- Every Key Fact line carries its F-ID so prose and registry stay linked.
- Sections 5, 7, 9 follow the same "claim (F-ID) — [Source: URL]" pattern for any factual statement.
- The literal tags `[VERIFY]` / `[SINGLE-SOURCE]` are allowed here and in 01-facts.json ONLY (patch Section 6).

## 01-facts.json — worked example

Schema: `/templates/schemas/facts-file.schema.json`. Example (shape from patch Section 5):

```json
{
  "videoSlug": "why-rome-really-collapsed",
  "searchesUsed": 11,
  "searchBudget": 15,
  "sources": [
    {
      "id": "S001",
      "title": "Source title",
      "url": "https://...",
      "type": "academic",
      "reliability": "high",
      "notes": ""
    }
  ],
  "facts": [
    {
      "id": "F001",
      "claim": "Rome's western imperial authority ended in 476 CE.",
      "sources": ["S001", "S002"],
      "status": "VERIFIED",
      "scriptCritical": true,
      "isNumber": false,
      "notes": ""
    },
    {
      "id": "F002",
      "claim": "Military costs placed pressure on the imperial budget.",
      "sources": ["S003"],
      "status": "SINGLE-SOURCE",
      "scriptCritical": false,
      "isNumber": false,
      "notes": ""
    },
    {
      "id": "F003",
      "claim": "Uncertain claim.",
      "sources": [],
      "status": "VERIFY",
      "scriptCritical": false,
      "isNumber": false,
      "notes": "No second source found."
    }
  ]
}
```

## isNumber examples

| Claim | isNumber | Why |
|---|---|---|
| "Rome's western imperial authority ended in 476 CE." | false | bare year/date reference |
| "The denarius fell to about 5% silver content by 270 CE." | true | percentage (quantity) |
| "The late Roman army numbered roughly 400,000 soldiers." | true | count |
| "Diocletian split the empire's administration." | false | no numeric data |

An `isNumber: true` fact that will be used in the script (narration, stat-card, chart-scene) must be `VERIFIED` and `scriptCritical: true`.

## Source `type` and `reliability` guidance

- `academic` — peer-reviewed work, university press books → usually `high`
- `institutional` — museums, government archives, established encyclopedic institutions → `high`/`medium`
- `encyclopedic` — general encyclopedias → `medium` (fine for VERIFIED pairing, weak alone for script-critical numbers)
- `popular` — journalism, popular history sites → `medium`/`low`
- `weak` — blogs, forums, unattributed pages → `low`; never the sole source of a Key Fact

# 01-research-skill — Research Modes

## Mode selection

```text
If user provided sources AND web search available → Hybrid
If user provided sources only                     → Manual Source Mode
If web search available only                      → Web Search Mode (default)
If no sources and no web search                   → Research Request Output
                                                    (facts are NEVER invented)
```

## Manual Source Mode rules

```text
- If the user supplied sources, those sources are used first.
- Important information without a source cannot be written as a Key Fact.
- Information with unclear sourcing gets the [VERIFY] tag.
- If sources are insufficient, a "Missing Sources" section is produced
  at the end of the output.
```

NotebookLM output pasted by the user is Manual Source Mode input — see `notebooklm-workflow.md` for the [S1] → S001 ID mapping and normalization steps.

## Web Search Mode

- Default when no user sources exist and search tooling is available.
- Budget: max 15 searches per video, including targeted second-source searches. Track and report the count; record it in 01-facts.json (`searchesUsed`).
- Spend the budget deliberately: broad overview first, then targeted verification of script-critical numbers and main claims (they need 2 independent sources), then color (surprising details, misconceptions).
- Independent means independent: two pages citing the same origin count as one source.

## Hybrid

1. Process the user's manual sources first (Manual Source Mode rules apply).
2. Use web search to fill gaps and find second sources for script-critical claims.
3. Budget still applies to the web-search portion.

## Research Request Output (no sources, no web search)

Produce exactly this and stop — research cannot complete without sources:

```markdown
# Research Request

This topic requires external sources before a verified script can be produced.

## Topic
[video topic]

## Sources Needed
1. Academic or institutional overview source
2. At least one source for key dates and events
3. At least one source for numbers/statistics
4. Optional: one popular source for audience-friendly framing

## Suggested Search Queries
- query 1
- query 2
- query 3

## Current Status
Research cannot be marked complete until sources are provided or web search is available.
```

# 01-research-skill — Optional NotebookLM Pre-Flow

Not mandatory; enable it if quota measurements come out high. The goal: move source reading/extraction OUT of Claude's token budget, leaving Claude only normalization, quality grading, dual-source checking, and VERIFY tagging.

## Flow

```text
1. Topic → NotebookLM "Discover Sources" + manual source additions
   → curate down to 5–10 sources.
2. Paste a NUMBERED source list (with URLs) into the notebook as its own
   source document.
3. A standard extraction prompt (embedded in the notebook's Custom
   Instructions) produces the Research Report format; every fact line MUST
   end with a source reference like [S1], [S2].
4. Paste the NotebookLM output to Claude → processed under Manual Source
   Mode (see research-modes.md).
5. Claude's remaining work: normalization, reliability grading, dual-source
   check, [VERIFY] tagging, and producing 01-research.md + 01-facts.json.
```

## [S1] → S001 ID mapping (binding)

- NotebookLM references map **positionally** against the numbered source list from step 2: `[S1]` → `S001`, `[S2]` → `S002`, ... `[S12]` → `S012` (zero-pad to 3 digits).
- The numbered source list becomes the `sources` array of 01-facts.json in the same order (id, title, url, type, reliability filled by Claude).
- Write the mapping table into 01-research.md's Source Notes section, e.g.:

```markdown
## Source Notes
1. S001 (NotebookLM [S1]) — URL — institutional, high
2. S002 (NotebookLM [S2]) — URL — popular, medium
```

- A NotebookLM fact line with no [Sn] reference is treated as sourceless: it cannot become a Key Fact; at most a `VERIFY` record.

## Warning

Grounded ≠ error-free. NotebookLM answers only from the curated sources, but extraction mistakes and source quality remain the user's curation responsibility. The dual-source rule for script-critical numbers still applies unchanged.

# 02-script-skill — Promise Match Check + Hook Promise Audit

## Inputs

The Script Hook Promise block produced by 05A Packaging Core (title promise + thumbnail promise). If it does not exist yet, the audit is PENDING (see below).

## Promise Match Check (run after writing the hook)

```text
1. Do the first 20 seconds clearly deliver the title's promise?
2. Are the first 20 seconds visually/emotionally consistent with the
   thumbnail concept?
3. Does the hook create curiosity without misleading?
4. Does the hook avoid slow/generic background narration?
```

If ANY answer is "no": rewrite the hook and re-run the check. Do not rationalize a borderline hook into a PASS.

## Audit output (mandatory script footer)

Append to the end of 02-script-annotated.md:

```markdown
## Hook Promise Audit

Title Promise:
[title from 05A]

Thumbnail Promise:
[thumbnail text from 05A]

Hook Match:
PASS

Reason:
[1–3 sentences explaining why the first 20 seconds deliver the promise]
```

## Feedback flow (patch Section 13 — binding)

```text
05A exists BEFORE the script:
- The hook takes the Script Hook Promise as input.
- The audit must be PASS, or the hook is revised until it is.

05A does not exist yet:
- Write the hook from the research report's hook ideas.
- Audit status: PENDING — packaging not available yet.

05A is produced later:
- Run the Promise Match Check then.
- On mismatch, revise ONLY the hook section (targeted edit of Scene 1 /
  early scenes). Avoid full-script regeneration (quota rule 4).
```

Judgmental evaluation of whether the title/thumbnail claims are SUPPORTED by the video content belongs to the human checklist (Layer 2), never to quality-gate.py. This audit is the script-side self-check, not the gate.

# 02-script-skill — Output Format and Examples

## File header

`02-script-annotated.md` starts with a short header before the first scene:

```markdown
# Annotated Video Script — [Video Title / Slug]

Target Length: 7 minutes | Target Words: ~1,000–1,100 | Speaking Rate: 150 wpm
```

Then scenes only, in the exact patch Section 14 format. After the last scene: the Hook Promise Audit section.

## Worked example (two scenes)

```markdown
## Scene 1

Word Count: 8
Estimated Duration: ~3 seconds

Narration:
Rome did not fall in a single night.

Used Facts:
- F001

Visual Intent:
Map of the Roman Empire beginning to crack.

On-screen Text:
ROME DIDN'T FALL IN ONE DAY

Emotional Tone:
Mysterious, serious, dramatic.

## Scene 2

Word Count: 12
Estimated Duration: ~5 seconds

Narration:
For three hundred years, something inside the empire had been quietly breaking.

Used Facts:
- F004

Visual Intent:
Timeline hinting at a long decline before the final fall.

On-screen Text:
A 300-YEAR COLLAPSE

Emotional Tone:
Ominous, intriguing.
```

Notes:

- `Narration:` content may span multiple lines; derive_vo.py joins them with single spaces.
- `Used Facts:` is a dash list of F-IDs that exist in 01-facts.json. May be empty ONLY if the scene makes no factual claim.
- `Visual Intent:` is one sentence of intent, never an animation recipe.
- `On-screen Text:` 2–7 words.
- No template names anywhere — template mapping is 03's job.

## derive_vo.py contract

- Scene delimiter: a line matching `^## Scene (\d+)\s*$`.
- Field labels (exact, at line start): `Word Count:`, `Estimated Duration:`, `Narration:`, `Used Facts:`, `Visual Intent:`, `On-screen Text:`, `Emotional Tone:`. Only these labels terminate a Narration block.
- Narration text = lines between `Narration:` and the next label/scene/EOF, stripped, joined with single spaces.
- Output: one paragraph per scene in ascending scene order, exactly one blank line between paragraphs, UTF-8, LF endings, single trailing newline.
- Deterministic: same input → byte-identical output (quality-gate re-derives and diffs; diff must be 0).
- Fails closed (exit 2, no output written): no scenes found, a scene without narration, duplicate scene numbers.
- Warns (exit 0): declared vs computed Word Count mismatch, narration > 30 words, non-sequential scene numbers.

The expected VO output for the two-scene example above:

```text
Rome did not fall in a single night.

For three hundred years, something inside the empire had been quietly breaking.
```

## Hook Promise Audit (script footer)

```markdown
## Hook Promise Audit

Title Promise:
Why Rome Was Already Dead Before It Fell

Thumbnail Promise:
ROME WAS ALREADY DEAD

Hook Match:
PASS

Reason:
The first 20 seconds clearly state that Rome did not collapse in one moment and
frames the story as an internal breakdown that began before the final invasions.
```

If packaging does not exist yet:

```markdown
## Hook Promise Audit

Hook Match:
PENDING — packaging not available yet

Reason:
05A Packaging Core has not been produced; the hook was written from research
hook ideas. Run the Promise Match Check after 05A exists.
```

Note: derive_vo.py ignores this section automatically — `## Hook Promise Audit` is not a `## Scene N` header, and narration capture ends at the previous scene's next field label.

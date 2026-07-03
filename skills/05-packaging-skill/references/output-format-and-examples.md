# 05-packaging.md — Format & Worked Example

One file, two parts. 05A is written first; 05B is APPENDED later (never rewrite 05A when adding 05B — quota rule: targeted edits only). Headings below are the contract; `## Script Hook Promise` and `## Attribution Block` are checked mechanically by quality-gate.py.

```markdown
# 05A — Packaging Core

## Main YouTube Title

Why Rome Was Already Dead Before It Fell

## Alternative Titles

1. Rome Didn't Fall. It Broke.
2. The Slow Death of the Roman Empire
3. Why the Richest Empire in History Collapsed
4. The Empire That Became Too Big to Survive

## Thumbnail Concepts

1. Cracked marble bust of an emperor, one half crumbling to dust — dark background.
2. Map of the empire with borders burning inward toward Rome.

## Thumbnail Text Options

- ROME WAS ALREADY DEAD
- TOO BIG TO SURVIVE
- THE REAL COLLAPSE

## Video Description Draft

In this video, we explore the fall of Rome and uncover why the empire was
collapsing long before the barbarians arrived.

Most people think Rome fell in a single dramatic invasion.
But the real story is much more surprising.

Watch as we break down:
- Why the borders became impossible to pay for
- How the currency quietly died first
- What 476 AD actually changed (almost nothing)

Subscribe for more animated documentaries about history, money, survival, and civilization.

## Tags / Keywords Draft

roman empire, fall of rome, why rome fell, ancient history, animated documentary, ...

## Pinned Comment Draft

Which empire should we break down next? 👇

## Shorts Ideas

1. Shorts Title: Rome's Money Died First
   Clip Segment / Moment: the currency-debasement stat scene
   Hook Line: "Rome's coins lost 90% of their silver — before any invasion."
   Visual Idea: stat-card 9:16 (value: "90%", countUp)
2. Shorts Title: The Border Problem
   Clip Segment / Moment: map scene of the max-extent empire
   Hook Line: "This border was 10,000 km long. Someone had to pay for it."
   Visual Idea: map-scene 9:16 (slow-zoom-out)
3. Shorts Title: 476 AD Changed Nothing
   Clip Segment / Moment: final-thought scene
   Hook Line: "The empire didn't notice its own death."
   Visual Idea: text-emphasis 9:16 (impact)

## A/B Test Suggestions

- Title A "Why Rome Was Already Dead Before It Fell" vs Title B "Rome Didn't Fall. It Broke." — same thumbnail.
- Thumbnail: cracked bust vs burning map — keep the winning title fixed.

## CTR Angle Explanation

The angle is contrarian-correction: viewers "know" Rome fell to barbarians;
promising the real, slower cause creates a curiosity gap without clickbait.

## Script Hook Promise

Main Viewer Promise:
The fall of Rome was an inside job that took three hundred years — and the
"fall" everyone knows barely mattered.

Hook Must Establish:
- Rome did not fall in one night
- The real killer was internal and financial
- The famous 476 AD moment is not what you think

Avoid:
- Misleading angle
- Slow generic intro
- Unrelated background

# 05B — Publishing Finalization

## Final Video Description

[05A draft + final key points + Attribution Block below]

## Final Tags

[trimmed, deduplicated final list]

## Final Pinned Comment

[final text]

## Attribution Block

Map data: "Roman Empire 117 AD" by Wikimedia Commons contributors, CC BY-SA 3.0
Icons: Tabler Icons (MIT)

## Upload Checklist

- [ ] Title + thumbnail pair chosen (A/B plan noted)
- [ ] Description includes Attribution Block (if required)
- [ ] Tags, pinned comment set
- [ ] End screen / cards configured
- [ ] Shorts clips scheduled
```

Rules:

- 05B's Attribution Block lists EVERY used asset with `attributionRequired: true`, using its manifest `attributionText`. None used → write `## Attribution Block` with "None required." only if you need the heading for clarity; otherwise omit the section entirely (the gate only demands it when attribution-required assets are used).
- Titles/thumbnail text: claims with numbers must trace to a VERIFIED fact ID (note the ID in an HTML comment for the human checklist, e.g. `<!-- F007 -->`).

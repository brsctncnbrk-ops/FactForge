# Template Selection Guide

Machine truth for props is always `/templates/schemas/{template}.schema.json`; the human catalog is `/templates/template-catalog.md`. This guide only helps you pick the right template fast.

## Narration type → template

| The scene's narration is... | First choice | Alternatives |
|---|---|---|
| A place, region, border, movement, invasion | map-scene | image-spotlight |
| A sequence of dated events, "over X years" | timeline-scene | list-reveal |
| One striking number or statistic | stat-card | chart-scene, text-emphasis |
| Before/after, two sides, two eras | comparison-split | chart-scene |
| 3–5 parallel items, causes, reasons | list-reveal | icon-grid |
| A quotation or a named person's words | quote-card | text-emphasis |
| People/groups acting (armies, crowds, rulers) | silhouette-scene | icon-grid |
| A trend, growth, decline, distribution | chart-scene | stat-card |
| Quantity as repetition (soldiers, ships, population) | icon-grid | stat-card |
| One thesis sentence, a punchline, the hook | text-emphasis | quote-card |
| A concrete artifact, painting, photo, ruin | image-spotlight | silhouette-scene |
| Chapter change, tempo reset, act break | transition-break | text-emphasis |

## Selection rules

1. **Data beats decoration.** If the narration contains a number, prefer the template that shows the number (stat-card / chart-scene / icon-grid) over a mood shot. Remember: numbers on screen require a VERIFIED fact in `usedFacts` — never put a number in props that is not claimed in the narration.
2. **One idea per scene.** If a scene seems to need two templates, the script scene is too dense — flag it back to 02 for a split rather than overloading props.
3. **Variety cadence.** Avoid the same template in more than 2 consecutive scenes (exception: transition-break boundaries). If 3+ in a row emerge, swap the middle one for an alternative from the table.
4. **Motion every 5–10 seconds.** Every template has built-in animation (counter, reveal, Ken Burns, camera drift); pick props that use it — e.g. never `camera: "static"` on a map-scene longer than ~6 seconds.
5. **transition-break is punctuation**, not content: use it at act boundaries from the script structure (Hook → Problem Setup → Main Story → Turning Point → Final Thought), roughly every 60–90 seconds, never twice in a row.

## Props discipline

- Fill every required prop; add optional props only when they change what the viewer sees. Schemas use `additionalProperties: false` — inventing prop names fails validation.
- `onScreenText` (and text-emphasis `text`) should mirror the script's On-screen Text field: 2–7 words, ALL-CAPS style consistent across the video.
- Every asset id referenced inside props (`asset`, `mapAsset`, `backgroundAsset`, `icon`, `image` keys) must also be declared in that scene's `assets.fromLibrary` or `assets.newAssets` — validate.py enforces this.

## 9:16 / Shorts variants

Aspect is a prop (`aspectRatio: "9:16"`), never a schema copy. Only stat-card, text-emphasis, and map-scene are planned for vertical from the start; when packaging asks for Shorts material, build it from those three templates.

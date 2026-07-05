# Template Catalog (v2 — 16 templates)

Human-readable catalog for the scene template system. The **machine source of truth** is `/templates/schemas/{template}.schema.json` (P8) — on any conflict between this document and a schema, **the schema wins**. The top-level file contract is `/templates/schemas/scenes-file.schema.json`.

Shared conventions (all 16 templates):

- All asset-valued props (`icon`, `image`, `background`, `mapAsset`, `figures[].asset`, ...) hold **manifest asset IDs** from `/assets/library/manifest.json`, never file paths or URLs.
- Every template has an optional `aspectRatio` prop: `"16:9"` (default) or `"9:16"`. 9:16 is a prop, not a separate schema — schema count stays at 16.
- `additionalProperties: false` everywhere: a prop not listed in the schema is a validation error, not a hint to the renderer.
- Template gaps are logged in `/templates/TEMPLATE-GAPS.md` (see NEW TEMPLATE PROPOSAL rule in the brief, 03-visual-scene-skill section). Templates 13-16 below were added 2026-07-05 as a direct, explicit architectural decision (not through the emergent per-video threshold — see the TEMPLATE-GAPS.md entry for that decision's paper trail).

---

## 1. map-scene

**Purpose:** Map + region highlight + icon placement + camera movement. Geography, expansion/contraction, borders, invasion routes.

| Prop | Type | Required | Allowed values / constraints |
|---|---|---|---|
| `region` | string | yes | named region/extent on the map (e.g. `roman-empire-max-extent`) |
| `camera` | string | yes | `static`, `slow-zoom-in`, `slow-zoom-out`, `slow-pan-left`, `slow-pan-right`, `drift` |
| `mapAsset` | string | no | manifest ID of the map asset (otherwise taken from `assets.fromLibrary`) |
| `highlights` | string[] | no | region features to emphasize (e.g. `borders`) |
| `icons` | object[] | no | each: `asset` (required), `placement` (required), `label` |
| `onScreenText` | string | no | short overlay text |
| `aspectRatio` | string | no | `16:9` (default), `9:16` |

**Example props:**

```json
{
  "region": "roman-empire-max-extent",
  "highlights": ["borders"],
  "icons": [
    { "asset": "icon-warning-red", "placement": "borders" },
    { "asset": "icon-soldier", "placement": "frontier-spread" }
  ],
  "camera": "slow-zoom-out",
  "onScreenText": "TOO LARGE TO DEFEND"
}
```

**Asset needs:** 1 map asset (type `map`), 0–n icons.
**9:16 variant:** planned from the start (Shorts template). Vertical crop centers on `region`; `onScreenText` moves to the top third.

---

## 2. timeline-scene

**Purpose:** Horizontal timeline; event points appear in sequence. Chronologies, cause chains, "how we got here".

| Prop | Type | Required | Allowed values / constraints |
|---|---|---|---|
| `events` | object[] | yes | 2–6 items; each: `label` (required), `date`, `description` |
| `title` | string | no | timeline heading |
| `highlightIndex` | integer | no | ≥ 0; index of the emphasized event |
| `aspectRatio` | string | no | `16:9` (default), `9:16` |

**Example props:**

```json
{
  "title": "The Long Decline",
  "events": [
    { "label": "Crisis of the Third Century", "date": "235 CE" },
    { "label": "Empire splits in two", "date": "395 CE" },
    { "label": "Sack of Rome", "date": "410 CE" },
    { "label": "Western authority ends", "date": "476 CE" }
  ],
  "highlightIndex": 3
}
```

**Asset needs:** none (pure vector/typography).
**9:16 variant:** timeline rotates to vertical; max 4 events recommended.

---

## 3. stat-card

**Purpose:** Large number/statistic + short label + counter animation. **Data must come from VERIFIED facts only** (patch Section 6).

| Prop | Type | Required | Allowed values / constraints |
|---|---|---|---|
| `value` | string \| number | yes | display value (e.g. `"80,000"`, `25`) |
| `label` | string | yes | what the number is |
| `secondaryText` | string | no | context line under the label |
| `icon` | string | no | manifest icon ID |
| `countUp` | boolean | no | default `true`; animate counter from 0 |
| `aspectRatio` | string | no | `16:9` (default), `9:16` |

**Example props:**

```json
{
  "value": "80,000",
  "label": "soldiers on the frontier",
  "secondaryText": "paid from a shrinking treasury",
  "icon": "icon-soldier",
  "countUp": true
}
```

**Asset needs:** 0–1 icon.
**9:16 variant:** planned from the start (Shorts template). Number scales up, label wraps below.

---

## 4. comparison-split

**Purpose:** Split screen comparing two states/periods (before/after, east/west, rich/poor).

| Prop | Type | Required | Allowed values / constraints |
|---|---|---|---|
| `left` / `right` | object | yes | each: `title` (required), `items` (string[]), `image` (manifest ID), `value` (string) |
| `heading` | string | no | overall comparison heading |
| `aspectRatio` | string | no | `16:9` (default), `9:16` |

**Example props:**

```json
{
  "heading": "Two Empires, Two Fates",
  "left": { "title": "Western Empire", "items": ["Falling tax income", "Frontier pressure"] },
  "right": { "title": "Eastern Empire", "items": ["Wealthy cities", "Defensible capital"] }
}
```

**Asset needs:** 0–2 images (optional per side).
**9:16 variant:** split becomes top/bottom instead of left/right.

---

## 5. list-reveal

**Purpose:** 3–5 item list, items appear in sequence. Factor lists, "three reasons why".

| Prop | Type | Required | Allowed values / constraints |
|---|---|---|---|
| `items` | string[] | yes | **3–5 items** |
| `title` | string | no | list heading |
| `numbered` | boolean | no | default `false` |
| `aspectRatio` | string | no | `16:9` (default), `9:16` |

**Example props:**

```json
{
  "title": "What Was Breaking",
  "items": ["The army cost too much", "Taxes stopped flowing", "Borders stretched too thin"],
  "numbered": true
}
```

**Asset needs:** none.
**9:16 variant:** larger type, one item per screen-third.

---

## 6. quote-card

**Purpose:** Quote/key sentence with typographic emphasis. Primary-source quotes, striking statements.

| Prop | Type | Required | Allowed values / constraints |
|---|---|---|---|
| `quote` | string | yes | the quoted text |
| `attribution` | string | no | who said/wrote it |
| `emphasisWords` | string[] | no | words to highlight typographically |
| `background` | string | no | manifest ID (background/texture) |
| `aspectRatio` | string | no | `16:9` (default), `9:16` |

**Example props:**

```json
{
  "quote": "The city which had taken the whole world was itself taken.",
  "attribution": "Jerome, 410 CE",
  "emphasisWords": ["whole world", "taken"]
}
```

**Asset needs:** 0–1 background/texture.
**9:16 variant:** quote centered, attribution bottom.

---

## 7. silhouette-scene

**Purpose:** Character/group silhouettes + background + simple movement. Human moments, armies, migrations, crowds.

| Prop | Type | Required | Allowed values / constraints |
|---|---|---|---|
| `figures` | object[] | yes | 1–8 items; each: `asset` (required), `action` (`static`, `walk`, `march`, `fall`, `raise-arm`, `point`), `position` (`left`, `center`, `right`, `foreground`, `background`) |
| `background` | string | no | manifest ID |
| `onScreenText` | string | no | short overlay text |
| `aspectRatio` | string | no | `16:9` (default), `9:16` |

**Example props:**

```json
{
  "figures": [
    { "asset": "figure-legionary", "action": "march", "position": "center" },
    { "asset": "figure-civilian", "action": "static", "position": "background" }
  ],
  "background": "bg-dusk-gradient",
  "onScreenText": "THE LEGIONS MARCH HOME"
}
```

**Asset needs:** 1–8 figure assets, 0–1 background.
**9:16 variant:** max 3 figures; foreground figure dominates.

---

## 8. chart-scene

**Purpose:** Line/bar/pie chart drawn with data animation. **Chart data must come from VERIFIED facts only** (patch Section 6).

| Prop | Type | Required | Allowed values / constraints |
|---|---|---|---|
| `chartType` | string | yes | `line`, `bar`, `pie` |
| `data` | object | yes | `labels` (string[], required) + `series` (required; each: `name`, `values` number[]) |
| `title` | string | no | chart heading |
| `xAxisLabel` / `yAxisLabel` | string | no | axis labels |
| `highlightIndex` | integer | no | ≥ 0; data point to emphasize |
| `animationStyle` | string | no | `draw` (default), `grow`, `fade` |
| `aspectRatio` | string | no | `16:9` (default), `9:16` |

**Example props:**

```json
{
  "chartType": "line",
  "title": "Silver Content of the Denarius",
  "data": {
    "labels": ["64 CE", "180 CE", "270 CE"],
    "series": [{ "name": "% silver", "values": [93, 75, 5] }]
  },
  "highlightIndex": 2,
  "animationStyle": "draw"
}
```

**Asset needs:** none (data-driven vector).
**9:16 variant:** bar charts rotate to horizontal bars; max 5 labels.

---

## 9. icon-grid

**Purpose:** Icon array (e.g. army size, population representation). One icon = N units.

| Prop | Type | Required | Allowed values / constraints |
|---|---|---|---|
| `icon` | string | yes | manifest icon ID |
| `count` | integer | yes | 1–200 |
| `highlightCount` | integer | no | ≥ 0; subset visually distinguished (e.g. losses) |
| `label` | string | no | what the grid represents |
| `columns` | integer | no | ≥ 1; grid width override |
| `secondaryIcon` / `secondaryCount` | string / integer | no | second population for contrast |
| `aspectRatio` | string | no | `16:9` (default), `9:16` |

**Example props:**

```json
{
  "icon": "icon-soldier",
  "count": 50,
  "highlightCount": 15,
  "label": "1 icon = 10,000 soldiers",
  "columns": 10
}
```

**Asset needs:** 1–2 icons.
**9:16 variant:** fewer columns, larger icons.

---

## 10. text-emphasis

**Purpose:** Full-screen kinetic typography, one strong sentence. Hooks, turning points, section punchlines.

| Prop | Type | Required | Allowed values / constraints |
|---|---|---|---|
| `text` | string | yes | one strong sentence |
| `emphasisWords` | string[] | no | words to hit hardest |
| `animation` | string | no | `impact` (default), `typewriter`, `fade-scale` |
| `backgroundColor` | string | no | CSS color value |
| `backgroundAsset` | string | no | manifest ID (background/texture) |
| `aspectRatio` | string | no | `16:9` (default), `9:16` |

**Example props:**

```json
{
  "text": "Rome didn't fall in a day. It fell for three hundred years.",
  "emphasisWords": ["three hundred years"],
  "animation": "impact"
}
```

**Asset needs:** 0–1 background.
**9:16 variant:** planned from the start (Shorts template). Text stacks vertically, larger type.

---

## 11. image-spotlight

**Purpose:** Stock image/photo + Ken Burns (slow pan/zoom). Real artifacts, ruins, paintings. With `revealStyle: "blur-in"`, doubles as the **mystery/reveal scene**: the image starts heavily blurred and dimmed and sharpens over the first ~35% of the scene, for "what is this really?" narration beats.

| Prop | Type | Required | Allowed values / constraints |
|---|---|---|---|
| `image` | string | yes | manifest image ID |
| `kenBurns` | string | yes | `zoom-in`, `zoom-out`, `pan-left`, `pan-right`, `pan-up`, `pan-down` |
| `caption` | string | no | small descriptive caption |
| `onScreenText` | string | no | short overlay text |
| `revealStyle` | string | no | `none` (default), `blur-in` (mystery/reveal treatment) |
| `aspectRatio` | string | no | `16:9` (default), `9:16` |

**Example props:**

```json
{
  "image": "img-colosseum-ruins",
  "kenBurns": "zoom-in",
  "caption": "The Colosseum today"
}
```

**Mystery/reveal example:**

```json
{
  "image": "img-mystery-document",
  "kenBurns": "zoom-in",
  "revealStyle": "blur-in",
  "onScreenText": "WHAT WAS HIDDEN?"
}
```

**Asset needs:** 1 image (license + attribution rules apply strictly; `attributionRequired` assets feed the packaging Attribution Block).
**9:16 variant:** vertical crop; `kenBurns` pans favor up/down.

---

## 12. transition-break

**Purpose:** Chapter transition, title card, tempo change.

| Prop | Type | Required | Allowed values / constraints |
|---|---|---|---|
| `title` | string | yes | chapter/section title |
| `subtitle` | string | no | secondary line |
| `chapterNumber` | integer | no | ≥ 1 |
| `style` | string | no | `fade` (default), `wipe`, `zoom` |
| `background` | string | no | manifest ID |
| `aspectRatio` | string | no | `16:9` (default), `9:16` |

**Example props:**

```json
{
  "chapterNumber": 2,
  "title": "The Money Runs Out",
  "style": "fade"
}
```

**Asset needs:** 0–1 background.

---

## 13. flow-diagram-scene

**Purpose:** Sequential steps connected by arrows. Process flows and cause-and-effect chains — the one thing list-reveal/timeline-scene don't do (a directional arrow between each step).

| Prop | Type | Required | Allowed values / constraints |
|---|---|---|---|
| `steps` | object[] | yes | 2–6 items; each: `label` (required), `icon` (manifest ID, optional) |
| `direction` | string | no | `horizontal` (default), `vertical` |
| `title` | string | no | scene heading |
| `highlightIndex` | integer | no | ≥ 0; index of the emphasized step |
| `aspectRatio` | string | no | `16:9` (default), `9:16` |

**Example props:**

```json
{
  "title": "HOW THE FRONTIER BROKE",
  "steps": [
    { "label": "Borders overextended", "icon": "icon-warning" },
    { "label": "Army spread too thin" },
    { "label": "Frontier provinces fall" }
  ],
  "highlightIndex": 2
}
```

**Asset needs:** 0–6 icons.
**9:16 variant:** forces `direction: "vertical"` regardless of the prop value; steps stack top-to-bottom.

---

## 14. scale-comparison-scene

**Purpose:** Two or more items shown as proportionally sized bars so a magnitude difference reads at a glance (army sizes, distances, populations).

| Prop | Type | Required | Allowed values / constraints |
|---|---|---|---|
| `items` | object[] | yes | 2–5 items; each: `label` (required), `value` (number > 0, required), `displayValue` (optional override string) |
| `unit` | string | no | appended to the auto-formatted value (e.g. `"km"`) |
| `title` | string | no | scene heading |
| `aspectRatio` | string | no | `16:9` (default), `9:16` |

**Example props:**

```json
{
  "title": "ARMY SIZE, THEN VS. NOW",
  "unit": "legions",
  "items": [
    { "label": "Peak (2nd century)", "value": 33 },
    { "label": "By 476 AD", "value": 9 }
  ]
}
```

**Asset needs:** none.
**9:16 variant:** bars stack narrower; labels wrap to two lines above the bar instead of beside it.

---

## 15. evidence-board-scene

**Purpose:** Pinned document/photo cards on a board, optionally linked by string lines. Investigative/mystery framing for a cluster of related facts revealed together.

| Prop | Type | Required | Allowed values / constraints |
|---|---|---|---|
| `items` | object[] | yes | 2–6 items; each: `label` (required), `icon` (manifest ID, optional), `note` (optional) |
| `connections` | integer[][] | no | pairs of item indices to connect with a string line |
| `title` | string | no | scene heading |
| `aspectRatio` | string | no | `16:9` (default), `9:16` |

**Example props:**

```json
{
  "title": "THE PAPER TRAIL",
  "items": [
    { "label": "Tax records, 440 AD", "icon": "icon-document" },
    { "label": "Payroll dispute", "icon": "icon-coin", "note": "unpaid legions" }
  ],
  "connections": [[0, 1]]
}
```

**Asset needs:** 0–6 icons.
**9:16 variant:** cards arrange in a single vertical column instead of the fixed 6-slot board layout.

---

## 16. news-briefing-scene

**Purpose:** News-desk framing — a BREAKING-style tag, a headline, and an optional scrolling ticker. Delivers a claim as a dispatched update rather than narration-over-scene.

| Prop | Type | Required | Allowed values / constraints |
|---|---|---|---|
| `headline` | string | yes | main headline text |
| `tag` | string | no | `"BREAKING"` (default) |
| `ticker` | string | no | scrolling bottom-band text |
| `aspectRatio` | string | no | `16:9` (default), `9:16` |

**Example props:**

```json
{
  "tag": "JUST IN",
  "headline": "THE LEGIONS STOP GETTING PAID",
  "ticker": "Frontier provinces report supply shortages — treasury reserves falling"
}
```

**Asset needs:** none.
**9:16 variant:** ticker band height increases proportionally; headline font shrinks one step to keep 2-line wrap.
**9:16 variant:** title centered, chapter number above.

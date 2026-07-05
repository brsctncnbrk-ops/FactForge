# FactForge Visual Style Guide (Flat-Vector, Infographics-Show-adjacent)

Human-readable reference for the shipped render style. **Machine truth is
`render/src/lib/theme.ts`** (palette/type) **and `render/src/lib/bits.tsx`**
(shared components) — on any conflict between this document and the code,
the code wins (P8). Update both together when the style changes.

## Color palette

| Token | Value | Use |
|---|---|---|
| `bg` | `#123B6B` navy | primary flat background field |
| `bgAlt` | `#0D2C52` | deeper navy, text-on-accent contexts |
| `panel` | `rgba(255,255,255,0.10)` | translucent panel fill |
| `text` | `#FFFFFF` | primary text |
| `textDim` | `#B9CBE4` | secondary/caption-adjacent text |
| `accent` | `#FF9736` orange | primary highlight, CTAs, overlay pills |
| `accentAlt` | `#FF5C5C` coral | secondary emphasis / urgency / warning |
| `good` | `#3DD68C` green | positive figures, growth, "civilian" costume |
| `stroke` | `rgba(255,255,255,0.85)` | fine outlines on light content |

There is no color token reserved exclusively for "danger" distinct from
general urgency emphasis — `accentAlt` covers both today. Add a dedicated
token only if a video needs both on screen at once and they'd collide.

## Typography

- Family: Poppins, loaded once in `theme.ts` via `@remotion/google-fonts`.
- Weights: 800 titles (`fontWeightTitle`), 500 body (`fontWeightBody`).
- Fallback stack: `'Segoe UI', Arial, sans-serif`.
- Do not introduce a second font family — one geometric sans, used
  consistently, is part of the flat-vector identity.

## Background rule

`SceneFrame` (`bits.tsx`) always renders a flat solid field (`theme.bg`)
plus 3 fixed, non-random decorative blob circles at low opacity. **Never**
a gradient, film grain, or vignette — those were deliberately removed in
the flat-vector pivot (see TASKS.md "Flat-Vector Rollout"). Do not
reintroduce them in new templates.

## Character / figure contract (v4 recolor)

- Outline: shared dark-navy stroke (`#152A4D`, width 4) around every shape.
- Skin: fixed warm tone (`#F0B285`) on head/limb shapes.
- Costume: driven by `currentColor` / per-type `FIGURE_COLORS` in
  `SilhouetteScene.tsx` (warrior = coral, emperor = orange, civilian =
  green) — the accent color is the only thing that varies per character.
- Trim (leggings/sandals/laurel): fixed neutral or gold tones, never
  re-tinted by `color`.
- Figure height baseline: 560 (bumped from 420 in v2 to fix sparse frames).
- New figures must follow this same fill contract (skin + outline baked
  into the asset, `color` prop tints garment/costume only) — do not ship a
  new single-fill silhouette.

## Motion vocabulary (`render/src/lib/anim.ts`)

- `entrance()` — proportional fade/rise ramp, capped at 0.6s absolute.
- `staggered()` — per-item reveal across the first 60% of a scene (icon
  grids, list items).
- `popIn()` — bouncy spring (damping 11, stiffness 140), the signature
  flat "pop" entrance (text-emphasis, stat-card counters).
- All timings are fractions of scene duration (P1), never fixed frame
  counts, so timing-sync re-runs propagate automatically. New templates
  must build on these three primitives rather than inventing bespoke
  frame-counted animation.

## Overlay text / caption safety

`OverlayText` and `CaptionOverlay` never share a vertical band:
`OVERLAY_SAFE_BOTTOM_PCT` (21%) when captions are active, else 8%
(`captionLayout.ts`). Any new template with an on-screen label must read
`CaptionsActiveContext` — never hardcode a bottom offset.

## Map treatment

Grayscale the source atlas, mount it on a bordered flat white card
(accent-orange border, 28px radius); accent-colored pins/pulses/labels
carry the infographic layer on top. This is a pragmatic reuse of the
existing detailed PD atlas, not a hand-simplified flat basemap — note the
limitation if a future video needs a truly minimal continent shape.

## What NOT to do

- No gradients, film grain, or vignettes.
- No black/monochrome silhouette figures — every figure needs skin +
  costume color + outline (the v1–v3 mistake, fixed in v4).
- No second font family or off-palette colors without updating this file
  and `theme.ts` in the same change.

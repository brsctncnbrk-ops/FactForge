import { interpolate } from "remotion";
import type { SilhouetteSceneProps } from "../types/generated";
import { easeOut, staggered, useScene } from "../lib/anim";
import { OverlayText, SceneFrame } from "../lib/bits";
import { theme } from "../lib/theme";
import { InlineSvg } from "../lib/InlineSvg";
import { resolveAsset } from "../lib/assets";

type Fig = SilhouetteSceneProps["figures"][number];

// position -> base x (%), bottom (%), scale. Same-position figures fan out by
// index so they never stack exactly.
const POSITIONS: Record<string, { x: number; bottom: number; scale: number }> = {
  left: { x: 25, bottom: 14, scale: 1 },
  center: { x: 50, bottom: 14, scale: 1 },
  right: { x: 75, bottom: 14, scale: 1 },
  foreground: { x: 50, bottom: 6, scale: 1.45 },
  background: { x: 50, bottom: 22, scale: 0.62 },
};

// Flat "costume" colors per figure type — the Infographics-Show look uses
// colorful flat character icons, not black cutouts. Falls back to white for
// any asset id not in this table (new figures still render, just neutral).
const FIGURE_COLORS: Record<string, string> = {
  "figure-warrior": theme.accentAlt,
  "figure-emperor": theme.accent,
  "figure-civilian": theme.good,
};

const figureMotion = (
  fig: Fig,
  frame: number,
  durationInFrames: number,
  progress: number
): React.CSSProperties => {
  const action = fig.action ?? "static";
  const bob = Math.sin((frame / 8) * Math.PI) * 4;
  switch (action) {
    case "walk":
      return {
        transform: `translateX(${interpolate(progress, [0, 1], [-40, 40])}px) translateY(${bob * 0.6}px)`,
      };
    case "march":
      return {
        transform: `translateX(${interpolate(progress, [0, 1], [-70, 70])}px) translateY(${bob}px)`,
      };
    case "fall": {
      // upright for the first half, then tips over
      const tip = easeOut(
        interpolate(frame, [durationInFrames * 0.45, durationInFrames * 0.85], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        })
      );
      return {
        transform: `rotate(${tip * 78}deg) translateY(${tip * 20}px)`,
        transformOrigin: "bottom center",
        opacity: 1 - tip * 0.25,
      };
    }
    case "raise-arm":
    case "point":
      return {
        transform: `translateY(${-Math.abs(bob) * 0.5}px) rotate(${
          action === "point" ? -3 : 0
        }deg)`,
      };
    default:
      return {};
  }
};

// The schema still allows an optional `background` image, but the flat
// template intentionally never draws it: a photographic/painted backdrop
// behind flat vector figures reads as a mismatch, not depth (confirmed in the
// Stage-1 visual POC). Flat figures stay on the flat ground only.
export const SilhouetteScene: React.FC<{ p: SilhouetteSceneProps }> = ({ p }) => {
  const { frame, durationInFrames, progress } = useScene();

  return (
    <SceneFrame>
      {/* flat ground bar — a solid baseline instead of a photographic horizon */}
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          bottom: 0,
          height: "9%",
          background: theme.bgAlt,
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          bottom: "9%",
          height: 6,
          background: theme.accent,
        }}
      />
      {p.figures.map((fig, i) => {
        const base = POSITIONS[fig.position ?? "center"] ?? POSITIONS.center;
        const same = p.figures.filter(
          (f, j) => j < i && (f.position ?? "center") === (fig.position ?? "center")
        ).length;
        const x = base.x + same * 9 * (same % 2 === 0 ? 1 : -1);
        const t = easeOut(staggered(frame, durationInFrames, i, p.figures.length, 0.4));
        const motion = figureMotion(fig, frame, durationInFrames, progress);
        // bigger than the old silhouettes — flat pictograms read as sparse in
        // a large empty flat frame if kept at the old (documentary-scale) size
        const height = 560 * base.scale;
        const color = FIGURE_COLORS[fig.asset] ?? theme.text;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: `${x}%`,
              bottom: `${base.bottom}%`,
              transform: "translateX(-50%)",
              opacity: t * (fig.position === "background" ? 0.7 : 1),
            }}
          >
            <div style={{ position: "relative", ...motion }}>
              {/* flat contact ellipse grounds the figure — solid, no blur */}
              <div
                style={{
                  position: "absolute",
                  left: "50%",
                  bottom: -6,
                  width: height * 0.4,
                  height: 14,
                  transform: "translateX(-50%)",
                  borderRadius: "50%",
                  background: "rgba(0,0,0,0.18)",
                }}
              />
              <InlineSvg
                src={resolveAsset(fig.asset)}
                color={color}
                style={{ height, width: height * 0.5 }}
              />
            </div>
          </div>
        );
      })}
      {p.onScreenText ? <OverlayText text={p.onScreenText} /> : null}
    </SceneFrame>
  );
};

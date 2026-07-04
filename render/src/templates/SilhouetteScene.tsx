import { Img, interpolate } from "remotion";
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
  left: { x: 25, bottom: 12, scale: 1 },
  center: { x: 50, bottom: 12, scale: 1 },
  right: { x: 75, bottom: 12, scale: 1 },
  foreground: { x: 50, bottom: 4, scale: 1.45 },
  // distant figures stand near the horizon line (hills top out ~27%), not
  // floating mid-sky — 34% read fine on the old bare gradient, not anymore
  background: { x: 50, bottom: 19, scale: 0.62 },
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

export const SilhouetteScene: React.FC<{ p: SilhouetteSceneProps }> = ({ p }) => {
  const { frame, durationInFrames, progress } = useScene();

  return (
    <SceneFrame
      // dusk sky: bright warm band at the horizon so dark figures read as
      // silhouettes against it
      background={
        "linear-gradient(180deg, #0d1120 0%, #232b45 45%, #6b4a3a 72%, #c2703f 88%, #1a1410 89%, #0a0c12 100%)"
      }
    >
      {p.background ? (
        <Img
          src={resolveAsset(p.background)}
          style={{
            position: "absolute",
            inset: 0,
            width: "100%",
            height: "100%",
            objectFit: "cover",
            opacity: 0.35,
          }}
        />
      ) : null}
      {/* low sun glow on the horizon */}
      <div
        style={{
          position: "absolute",
          left: "30%",
          right: "30%",
          bottom: "6%",
          height: "30%",
          background:
            "radial-gradient(50% 60% at 50% 88%, rgba(226,150,80,0.5) 0%, rgba(226,150,80,0.15) 55%, rgba(0,0,0,0) 80%)",
        }}
      />
      {/* distant hill layers, drifting apart very slowly (parallax) */}
      <div
        style={{
          position: "absolute",
          left: "-4%",
          right: "-4%",
          bottom: "11%",
          height: "16%",
          background: "#141724",
          opacity: 0.85,
          clipPath:
            "polygon(0% 100%, 0% 62%, 9% 44%, 18% 58%, 27% 30%, 38% 55%, 47% 38%, 57% 60%, 66% 34%, 76% 56%, 85% 42%, 94% 60%, 100% 48%, 100% 100%)",
          transform: `translateX(${-6 * progress}px)`,
        }}
      />
      <div
        style={{
          position: "absolute",
          left: "-4%",
          right: "-4%",
          bottom: "10%",
          height: "10%",
          background: "#0e1019",
          clipPath:
            "polygon(0% 100%, 0% 55%, 12% 70%, 22% 40%, 34% 66%, 45% 48%, 58% 72%, 70% 44%, 82% 64%, 92% 50%, 100% 66%, 100% 100%)",
          transform: `translateX(${6 * progress}px)`,
        }}
      />
      {/* ground: dark band with a lit edge instead of a bare 2px line */}
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          bottom: 0,
          height: "10.2%",
          background:
            "linear-gradient(180deg, rgba(26,20,16,0.95) 0%, #0a0c12 60%)",
          boxShadow: "0 -1px 0 rgba(226,150,80,0.35)",
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
        const height = 420 * base.scale;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: `${x}%`,
              bottom: `${base.bottom}%`,
              transform: "translateX(-50%)",
              opacity: t * (fig.position === "background" ? 0.55 : 0.92),
            }}
          >
            <div style={{ position: "relative", ...motion }}>
              <InlineSvg
                src={resolveAsset(fig.asset)}
                color="#0b0d14"
                style={{
                  height,
                  width: height * 0.5,
                  filter: "drop-shadow(0 6px 18px rgba(0,0,0,0.7))",
                }}
              />
              {/* contact shadow grounds the figure */}
              <div
                style={{
                  position: "absolute",
                  left: "50%",
                  bottom: -8,
                  width: height * 0.46,
                  height: 16,
                  transform: "translateX(-50%)",
                  borderRadius: "50%",
                  background:
                    "radial-gradient(50% 50% at 50% 50%, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0) 75%)",
                }}
              />
            </div>
          </div>
        );
      })}
      {p.onScreenText ? <OverlayText text={p.onScreenText} /> : null}
    </SceneFrame>
  );
};

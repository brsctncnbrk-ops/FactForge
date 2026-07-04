import { Img, interpolate } from "remotion";
import type { ImageSpotlightProps } from "../types/generated";
import { useScene } from "../lib/anim";
import { OverlayText, SceneFrame } from "../lib/bits";
import { theme } from "../lib/theme";
import { resolveAsset } from "../lib/assets";

const kenBurnsTransform = (kind: string, p: number): string => {
  switch (kind) {
    case "zoom-in":
      return `scale(${1 + 0.14 * p})`;
    case "zoom-out":
      return `scale(${1.14 - 0.14 * p})`;
    case "pan-left":
      return `scale(1.15) translateX(${interpolate(p, [0, 1], [4, -4])}%)`;
    case "pan-right":
      return `scale(1.15) translateX(${interpolate(p, [0, 1], [-4, 4])}%)`;
    case "pan-up":
      return `scale(1.15) translateY(${interpolate(p, [0, 1], [4, -4])}%)`;
    case "pan-down":
      return `scale(1.15) translateY(${interpolate(p, [0, 1], [-4, 4])}%)`;
    default:
      return "none";
  }
};

export const ImageSpotlight: React.FC<{ p: ImageSpotlightProps }> = ({ p }) => {
  const { progress } = useScene();

  return (
    <SceneFrame>
      <Img
        src={resolveAsset(p.image)}
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: kenBurnsTransform(p.kenBurns, progress),
        }}
      />
      {/* vignette for text legibility */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(100% 100% at 50% 40%, transparent 55%, rgba(6,8,16,0.55) 100%)",
        }}
      />
      {p.caption ? (
        <div
          style={{
            position: "absolute",
            left: "3%",
            bottom: "3%",
            fontSize: 28,
            color: theme.textDim,
            background: "rgba(16,20,32,0.7)",
            padding: "6px 16px",
          }}
        >
          {p.caption}
        </div>
      ) : null}
      {p.onScreenText ? <OverlayText text={p.onScreenText} /> : null}
    </SceneFrame>
  );
};

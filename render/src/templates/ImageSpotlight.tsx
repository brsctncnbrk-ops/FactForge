import { useContext } from "react";
import { Img, interpolate } from "remotion";
import type { ImageSpotlightProps } from "../types/generated";
import { entrance, useScene } from "../lib/anim";
import { OverlayText, SceneFrame } from "../lib/bits";
import { CaptionsActiveContext } from "../lib/captionLayout";
import { theme } from "../lib/theme";
import { resolveAsset } from "../lib/assets";

// Mystery/reveal treatment: starts heavily blurred + dimmed, sharpens over
// the first ~35% of the scene. `t` is the entrance ramp (0..1).
const revealFilter = (t: number): string =>
  `blur(${(1 - t) * 22}px) brightness(${0.55 + 0.45 * t})`;

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
  const { frame, durationInFrames, fps, progress } = useScene();
  const captionsActive = useContext(CaptionsActiveContext);
  const revealT =
    p.revealStyle === "blur-in"
      ? entrance(frame, durationInFrames, fps, 0.35, 1.4)
      : 1;

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
          filter: p.revealStyle === "blur-in" ? revealFilter(revealT) : "none",
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
            // Burned-in subtitles own the bottom strip; move the source credit
            // to the top-left corner so it never sits under a caption.
            ...(captionsActive ? { top: "3%" } : { bottom: "3%" }),
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

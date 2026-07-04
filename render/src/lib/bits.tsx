// Small shared UI pieces used by several templates.
import { useContext } from "react";
import { AbsoluteFill } from "remotion";
import { bgGradient, theme } from "./theme";
import { entrance, useScene } from "./anim";
import { CaptionsActiveContext, OVERLAY_SAFE_BOTTOM_PCT } from "./captionLayout";

// Procedural film grain: an feTurbulence tile as a data URI — deterministic
// (fixed seed), no external asset, tiles seamlessly (stitchTiles).
const GRAIN_URI = `data:image/svg+xml;utf8,${encodeURIComponent(
  '<svg xmlns="http://www.w3.org/2000/svg" width="280" height="280">' +
    '<filter id="n"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch" seed="7"/>' +
    '<feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0.5 0 0 0 0"/></filter>' +
    '<rect width="100%" height="100%" filter="url(#n)"/></svg>'
)}`;

// Every template renders inside this frame: base gradient, a slowly drifting
// warm glow (depth), film grain, and an edge vignette — so even text-only
// scenes have atmosphere. Children render above all backdrop layers.
export const SceneFrame: React.FC<{
  children: React.ReactNode;
  background?: string;
}> = ({ children, background }) => {
  const { progress } = useScene();
  return (
    <AbsoluteFill
      style={{
        background: background ?? bgGradient,
        color: theme.text,
        fontFamily: theme.fontBody,
        overflow: "hidden",
      }}
    >
      <AbsoluteFill
        style={{
          background: `radial-gradient(60% 50% at ${44 + 12 * progress}% ${30 + 8 * progress}%, rgba(212,162,78,0.10) 0%, rgba(212,162,78,0.0) 70%)`,
        }}
      />
      <AbsoluteFill
        style={{
          backgroundImage: `url("${GRAIN_URI}")`,
          backgroundRepeat: "repeat",
          opacity: 0.05,
          mixBlendMode: "overlay",
        }}
      />
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(115% 100% at 50% 45%, rgba(0,0,0,0) 55%, rgba(3,5,9,0.45) 100%)",
        }}
      />
      <AbsoluteFill>{children}</AbsoluteFill>
    </AbsoluteFill>
  );
};

// Text with emphasisWords highlighted in the accent color (case-insensitive
// substring match, longest first so overlapping phrases win). Optional
// `underline` (0..1) draws a kinetic left-to-right rule under highlighted
// words — omitted by templates that don't animate it.
export const Emphasized: React.FC<{
  text: string;
  words?: string[];
  color?: string;
  underline?: number;
}> = ({ text, words, color = theme.accent, underline }) => {
  if (!words || words.length === 0) {
    return <>{text}</>;
  }
  const sorted = [...words].sort((a, b) => b.length - a.length);
  const pattern = sorted
    .map((w) => w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"))
    .join("|");
  const parts = text.split(new RegExp(`(${pattern})`, "gi"));
  const underlineStyle: React.CSSProperties =
    underline === undefined
      ? {}
      : {
          backgroundImage: `linear-gradient(${color}, ${color})`,
          backgroundSize: `${Math.max(0, Math.min(1, underline)) * 100}% 0.06em`,
          backgroundPosition: "0 96%",
          backgroundRepeat: "no-repeat",
        };
  return (
    <>
      {parts.map((part, i) =>
        sorted.some((w) => w.toLowerCase() === part.toLowerCase()) ? (
          <span key={i} style={{ color, ...underlineStyle }}>
            {part}
          </span>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </>
  );
};

// Bottom-centered short overlay text (map/silhouette/image templates). When
// subtitles are burned in it rises above the reserved caption band so the
// scene label and the subtitle never stack on top of each other.
export const OverlayText: React.FC<{ text: string }> = ({ text }) => {
  const { frame, durationInFrames, fps } = useScene();
  const captionsActive = useContext(CaptionsActiveContext);
  const t = entrance(frame, durationInFrames, fps, 0.2, 0.7);
  return (
    <div
      style={{
        position: "absolute",
        bottom: captionsActive ? `${OVERLAY_SAFE_BOTTOM_PCT}%` : "8%",
        left: 0,
        right: 0,
        display: "flex",
        justifyContent: "center",
        opacity: t,
        transform: `translateY(${(1 - t) * 20}px)`,
      }}
    >
      <div
        style={{
          fontFamily: theme.fontTitle,
          fontSize: 44,
          letterSpacing: "0.12em",
          textTransform: "uppercase",
          color: theme.text,
          background: "rgba(16,20,32,0.75)",
          border: `1px solid ${theme.stroke}`,
          borderTop: `3px solid ${theme.accent}`,
          padding: "14px 36px",
          textAlign: "center",
          maxWidth: "80%",
        }}
      >
        {text}
      </div>
    </div>
  );
};

export const SceneTitle: React.FC<{ text: string }> = ({ text }) => {
  const { frame, durationInFrames, fps } = useScene();
  const t = entrance(frame, durationInFrames, fps);
  return (
    <div
      style={{
        fontFamily: theme.fontTitle,
        fontSize: 54,
        color: theme.textDim,
        letterSpacing: "0.08em",
        textTransform: "uppercase",
        marginBottom: 48,
        opacity: t,
      }}
    >
      {text}
    </div>
  );
};

// Small shared UI pieces used by several templates.
import { useContext } from "react";
import { AbsoluteFill } from "remotion";
import { theme } from "./theme";
import { entrance, useScene } from "./anim";
import { CaptionsActiveContext, OVERLAY_SAFE_BOTTOM_PCT } from "./captionLayout";

// Fixed (non-random) flat decorative shapes — a hallmark of the flat
// infographic look. Positions/sizes are hard-coded, not derived from
// Math.random(), so every render worker draws the identical frame.
const BLOBS: { x: number; y: number; size: number; color: string; opacity: number }[] = [
  { x: -8, y: -10, size: 46, color: theme.accent, opacity: 0.12 },
  { x: 104, y: 88, size: 58, color: theme.good, opacity: 0.1 },
  { x: 96, y: 6, size: 30, color: theme.accentAlt, opacity: 0.1 },
];

// Every template renders inside this frame: a flat solid field with a couple
// of soft flat-color blobs drifting very slowly (visual interest without any
// gradient/grain/vignette texture). Children render above the backdrop.
export const SceneFrame: React.FC<{
  children: React.ReactNode;
  background?: string;
}> = ({ children, background }) => {
  const { progress } = useScene();
  return (
    <AbsoluteFill
      style={{
        background: background ?? theme.bg,
        color: theme.text,
        fontFamily: theme.fontBody,
        overflow: "hidden",
      }}
    >
      {BLOBS.map((b, i) => (
        <div
          key={i}
          style={{
            position: "absolute",
            left: `${b.x + (i % 2 === 0 ? 1 : -1) * 3 * progress}%`,
            top: `${b.y}%`,
            width: `${b.size}%`,
            height: `${b.size}%`,
            borderRadius: "50%",
            background: b.color,
            opacity: b.opacity,
          }}
        />
      ))}
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
          backgroundSize: `${Math.max(0, Math.min(1, underline)) * 100}% 0.1em`,
          backgroundPosition: "0 100%",
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

// Flat colored circle behind an icon — the signature Infographics-Show
// "icon chip" look. size is the outer circle diameter in px.
export const IconBadge: React.FC<{
  children: React.ReactNode;
  size?: number;
  color?: string;
  style?: React.CSSProperties;
}> = ({ children, size = 150, color = theme.accent, style }) => (
  <div
    style={{
      width: size,
      height: size,
      borderRadius: "50%",
      background: color,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      flexShrink: 0,
      ...style,
    }}
  >
    {children}
  </div>
);

// Bottom-centered short overlay text (map/silhouette/image templates), styled
// as a flat solid pill. When subtitles are burned in it rises above the
// reserved caption band so the scene label and the subtitle never stack.
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
        transform: `translateY(${(1 - t) * 20}px) scale(${0.9 + 0.1 * t})`,
      }}
    >
      <div
        style={{
          fontFamily: theme.fontTitle,
          fontWeight: theme.fontWeightTitle,
          fontSize: 40,
          letterSpacing: "0.02em",
          color: theme.bg,
          background: theme.accent,
          borderRadius: 999,
          padding: "14px 40px",
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
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        marginBottom: 48,
        opacity: t,
        transform: `translateY(${(1 - t) * -14}px)`,
      }}
    >
      <div
        style={{
          fontFamily: theme.fontTitle,
          fontWeight: theme.fontWeightTitle,
          fontSize: 50,
          color: theme.text,
          letterSpacing: "0.01em",
          textAlign: "center",
        }}
      >
        {text}
      </div>
      <div
        style={{
          width: 90,
          height: 8,
          borderRadius: 4,
          background: theme.accent,
          marginTop: 14,
          transform: `scaleX(${t})`,
        }}
      />
    </div>
  );
};

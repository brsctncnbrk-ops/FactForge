// Small shared UI pieces used by several templates.
import { AbsoluteFill } from "remotion";
import { bgGradient, theme } from "./theme";
import { entrance, useScene } from "./anim";

export const SceneFrame: React.FC<{
  children: React.ReactNode;
  background?: string;
}> = ({ children, background }) => (
  <AbsoluteFill
    style={{
      background: background ?? bgGradient,
      color: theme.text,
      fontFamily: theme.fontBody,
      overflow: "hidden",
    }}
  >
    {children}
  </AbsoluteFill>
);

// Text with emphasisWords highlighted in the accent color (case-insensitive
// substring match, longest first so overlapping phrases win).
export const Emphasized: React.FC<{
  text: string;
  words?: string[];
  color?: string;
}> = ({ text, words, color = theme.accent }) => {
  if (!words || words.length === 0) {
    return <>{text}</>;
  }
  const sorted = [...words].sort((a, b) => b.length - a.length);
  const pattern = sorted
    .map((w) => w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"))
    .join("|");
  const parts = text.split(new RegExp(`(${pattern})`, "gi"));
  return (
    <>
      {parts.map((part, i) =>
        sorted.some((w) => w.toLowerCase() === part.toLowerCase()) ? (
          <span key={i} style={{ color }}>
            {part}
          </span>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </>
  );
};

// Bottom-centered short overlay text (map/silhouette/image templates).
export const OverlayText: React.FC<{ text: string }> = ({ text }) => {
  const { frame, durationInFrames, fps } = useScene();
  const t = entrance(frame, durationInFrames, fps, 0.2, 0.7);
  return (
    <div
      style={{
        position: "absolute",
        bottom: "8%",
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

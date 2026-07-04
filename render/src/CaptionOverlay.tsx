// Burned-in subtitle overlay for the "video-captioned" composition. Renders
// the cue active at the current frame in the bottom safe area; a short opacity
// ramp softens cue changes. Timing comes exclusively from 05-captions.json
// (see lib/captions.ts) — no cue math happens here.
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import type { CaptionsFile } from "./types/generated";
import { theme } from "./lib/theme";

const FADE_SEC = 0.12;

export const CaptionOverlay: React.FC<{ captions: CaptionsFile }> = ({
  captions,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  const cue = captions.cues.find((c) => t >= c.startTime && t < c.endTime);
  if (!cue) {
    return null;
  }

  const opacity = interpolate(
    t,
    [
      cue.startTime,
      Math.min(cue.startTime + FADE_SEC, cue.endTime),
      Math.max(cue.endTime - FADE_SEC, cue.startTime),
      cue.endTime,
    ],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          bottom: "6.5%",
          display: "flex",
          justifyContent: "center",
          opacity,
        }}
      >
        <div
          style={{
            maxWidth: "78%",
            padding: "10px 26px",
            borderRadius: 10,
            background: "rgba(8, 10, 16, 0.72)",
            color: theme.text,
            fontFamily: theme.fontBody,
            fontSize: 40,
            lineHeight: 1.3,
            fontWeight: 500,
            textAlign: "center",
            textShadow: "0 2px 6px rgba(0,0,0,0.6)",
            whiteSpace: "pre-line",
          }}
        >
          {cue.lines.join("\n")}
        </div>
      </div>
    </AbsoluteFill>
  );
};

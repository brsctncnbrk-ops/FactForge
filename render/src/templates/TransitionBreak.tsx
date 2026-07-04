import { Img } from "remotion";
import type { TransitionBreakProps } from "../types/generated";
import { easeOut, entrance, useScene } from "../lib/anim";
import { SceneFrame } from "../lib/bits";
import { centerColumn, theme } from "../lib/theme";
import { resolveAsset } from "../lib/assets";

export const TransitionBreak: React.FC<{ p: TransitionBreakProps }> = ({ p }) => {
  const { frame, durationInFrames, fps } = useScene();
  const style = p.style ?? "fade";
  const t = easeOut(entrance(frame, durationInFrames, fps, 0.25, 1.0));
  const sub = easeOut(entrance(frame, durationInFrames, fps, 0.45, 1.6));

  const titleStyle: React.CSSProperties =
    style === "zoom"
      ? { opacity: t, transform: `scale(${0.8 + 0.2 * t})` }
      : style === "wipe"
        ? {
            clipPath: `inset(0 ${(1 - t) * 100}% 0 0)`,
          }
        : { opacity: t };

  return (
    <SceneFrame>
      {p.background ? (
        <Img
          src={resolveAsset(p.background)}
          style={{
            position: "absolute",
            inset: 0,
            width: "100%",
            height: "100%",
            objectFit: "cover",
            opacity: 0.25,
          }}
        />
      ) : null}
      <div style={centerColumn}>
        {p.chapterNumber ? (
          <div
            style={{
              fontSize: 38,
              letterSpacing: "0.5em",
              textTransform: "uppercase",
              color: theme.accent,
              marginBottom: 34,
              opacity: t,
            }}
          >
            Chapter {p.chapterNumber}
          </div>
        ) : null}
        <div
          style={{
            width: 120,
            height: 4,
            background: theme.accent,
            marginBottom: 40,
            transform: `scaleX(${t})`,
          }}
        />
        <div
          style={{
            fontFamily: theme.fontTitle,
            fontSize: 110,
            fontWeight: 700,
            textAlign: "center",
            letterSpacing: "0.04em",
            maxWidth: "84%",
            lineHeight: 1.12,
            ...titleStyle,
          }}
        >
          {p.title}
        </div>
        {p.subtitle ? (
          <div
            style={{
              marginTop: 34,
              fontSize: 42,
              color: theme.textDim,
              opacity: sub,
              textAlign: "center",
            }}
          >
            {p.subtitle}
          </div>
        ) : null}
      </div>
    </SceneFrame>
  );
};

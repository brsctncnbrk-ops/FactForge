import { interpolate } from "remotion";
import type { TextEmphasisProps } from "../types/generated";
import { easeOut, entrance, useScene } from "../lib/anim";
import { Emphasized, SceneFrame } from "../lib/bits";
import { centerColumn, theme } from "../lib/theme";
import { resolveAsset } from "../lib/assets";
import { Img } from "remotion";

export const TextEmphasis: React.FC<{ p: TextEmphasisProps }> = ({ p }) => {
  const { frame, durationInFrames, fps } = useScene();
  const animation = p.animation ?? "impact";
  const t = easeOut(entrance(frame, durationInFrames, fps, 0.18, 0.8));

  let style: React.CSSProperties = {};
  let text: React.ReactNode = <Emphasized text={p.text} words={p.emphasisWords} />;

  if (animation === "impact") {
    style = {
      opacity: t,
      transform: `scale(${1.18 - 0.18 * t})`,
      filter: `blur(${(1 - t) * 6}px)`,
    };
  } else if (animation === "fade-scale") {
    style = { opacity: t, transform: `scale(${0.92 + 0.08 * t})` };
  } else if (animation === "typewriter") {
    const chars = Math.round(
      interpolate(frame, [0, durationInFrames * 0.55], [0, p.text.length], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    );
    text = <Emphasized text={p.text.slice(0, chars)} words={p.emphasisWords} />;
  }

  return (
    <SceneFrame background={p.backgroundColor}>
      {p.backgroundAsset ? (
        <Img
          src={resolveAsset(p.backgroundAsset)}
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
      <div style={{ ...centerColumn, padding: "0 8%" }}>
        <div
          style={{
            fontFamily: theme.fontTitle,
            fontSize: 108,
            fontWeight: 700,
            lineHeight: 1.15,
            textAlign: "center",
            letterSpacing: "0.02em",
            ...style,
          }}
        >
          {text}
        </div>
      </div>
    </SceneFrame>
  );
};

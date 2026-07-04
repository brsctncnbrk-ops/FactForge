import { interpolate } from "remotion";
import type { TextEmphasisProps } from "../types/generated";
import { easeOut, entrance, popIn, useScene } from "../lib/anim";
import { Emphasized, SceneFrame } from "../lib/bits";
import { centerColumn, theme } from "../lib/theme";
import { resolveAsset } from "../lib/assets";
import { Img } from "remotion";

// Flat accent-colored rule under the text (replaces the documentary-style
// laurel ornament): a thick rounded bar that pops in a beat after the text.
const AccentDivider: React.FC<{ t: number }> = ({ t }) => (
  <div
    style={{
      width: 140,
      height: 10,
      borderRadius: 5,
      background: theme.accent,
      marginTop: 46,
      opacity: t,
      transform: `scaleX(${t})`,
    }}
  />
);

export const TextEmphasis: React.FC<{ p: TextEmphasisProps }> = ({ p }) => {
  const { frame, durationInFrames, fps } = useScene();
  const animation = p.animation ?? "impact";
  const pop = popIn(frame, fps, 0);
  // divider pops in a beat after the text lands
  const divider = easeOut(entrance(frame - Math.round(fps * 0.5), durationInFrames, fps, 0.2, 0.5));

  let style: React.CSSProperties = {};
  let text: React.ReactNode = (
    <Emphasized text={p.text} words={p.emphasisWords} />
  );

  if (animation === "impact") {
    // bouncy pop-scale, no blur — flat graphics read crisp at every frame
    style = { opacity: Math.min(1, pop * 1.4), transform: `scale(${pop})` };
  } else if (animation === "fade-scale") {
    const t = easeOut(entrance(frame, durationInFrames, fps, 0.18, 0.7));
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
            opacity: 0.2,
          }}
        />
      ) : null}
      <div style={{ ...centerColumn, padding: "0 8%" }}>
        <div
          style={{
            fontFamily: theme.fontTitle,
            fontWeight: theme.fontWeightTitle,
            fontSize: 108,
            lineHeight: 1.12,
            textAlign: "center",
            letterSpacing: "0.005em",
            ...style,
          }}
        >
          {text}
        </div>
        <AccentDivider t={divider} />
      </div>
    </SceneFrame>
  );
};

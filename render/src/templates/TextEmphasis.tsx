import { interpolate } from "remotion";
import type { TextEmphasisProps } from "../types/generated";
import { easeOut, entrance, useScene } from "../lib/anim";
import { Emphasized, SceneFrame } from "../lib/bits";
import { centerColumn, theme } from "../lib/theme";
import { resolveAsset } from "../lib/assets";
import { InlineSvg } from "../lib/InlineSvg";
import { Img } from "remotion";

// Laurel divider under the text: two mirrored branches around a gold rule,
// revealed by a scaleX sweep slightly after the text lands.
const LaurelDivider: React.FC<{ t: number }> = ({ t }) => (
  <div
    style={{
      display: "flex",
      alignItems: "center",
      gap: 22,
      marginTop: 54,
      opacity: t,
      transform: `scaleX(${0.6 + 0.4 * t})`,
      color: theme.accent,
    }}
  >
    <InlineSvg
      src={resolveAsset("decor-laurel")}
      color={theme.accent}
      style={{ width: 132, height: 44, transform: "scaleX(-1)", opacity: 0.9 }}
    />
    <div style={{ width: 10, height: 10, transform: "rotate(45deg)", background: theme.accent, opacity: 0.85 }} />
    <InlineSvg
      src={resolveAsset("decor-laurel")}
      color={theme.accent}
      style={{ width: 132, height: 44, opacity: 0.9 }}
    />
  </div>
);

export const TextEmphasis: React.FC<{ p: TextEmphasisProps }> = ({ p }) => {
  const { frame, durationInFrames, fps } = useScene();
  const animation = p.animation ?? "impact";
  const t = easeOut(entrance(frame, durationInFrames, fps, 0.18, 0.8));
  // kinetic underline sweeps in after the text has landed
  const underline = easeOut(
    entrance(frame - Math.round(fps * 0.55), durationInFrames, fps, 0.2, 0.5)
  );
  // divider follows the underline
  const divider = easeOut(
    entrance(frame - Math.round(fps * 0.8), durationInFrames, fps, 0.2, 0.6)
  );

  let style: React.CSSProperties = {};
  let text: React.ReactNode = (
    <Emphasized text={p.text} words={p.emphasisWords} underline={underline} />
  );

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
    text = (
      <Emphasized
        text={p.text.slice(0, chars)}
        words={p.emphasisWords}
        underline={underline}
      />
    );
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
        <LaurelDivider t={divider} />
      </div>
    </SceneFrame>
  );
};

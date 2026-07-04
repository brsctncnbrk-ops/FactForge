import { Img } from "remotion";
import type { QuoteCardProps } from "../types/generated";
import { easeOut, entrance, useScene } from "../lib/anim";
import { Emphasized, SceneFrame } from "../lib/bits";
import { centerColumn, theme } from "../lib/theme";
import { resolveAsset } from "../lib/assets";

export const QuoteCard: React.FC<{ p: QuoteCardProps }> = ({ p }) => {
  const { frame, durationInFrames, fps } = useScene();
  const t = easeOut(entrance(frame, durationInFrames, fps, 0.2, 0.9));
  const attr = easeOut(entrance(frame, durationInFrames, fps, 0.45, 1.6));

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
            opacity: 0.2,
          }}
        />
      ) : null}
      <div style={{ ...centerColumn, padding: "0 12%" }}>
        <div
          style={{
            fontFamily: theme.fontTitle,
            fontSize: 140,
            color: theme.accent,
            lineHeight: 0.5,
            opacity: t,
          }}
        >
          “
        </div>
        <div
          style={{
            fontFamily: theme.fontTitle,
            fontSize: 68,
            fontStyle: "italic",
            lineHeight: 1.35,
            textAlign: "center",
            marginTop: 30,
            opacity: t,
            transform: `translateY(${(1 - t) * 24}px)`,
          }}
        >
          <Emphasized text={p.quote} words={p.emphasisWords} />
        </div>
        {p.attribution ? (
          <div
            style={{
              marginTop: 44,
              fontSize: 40,
              color: theme.textDim,
              letterSpacing: "0.08em",
              opacity: attr,
            }}
          >
            — {p.attribution}
          </div>
        ) : null}
      </div>
    </SceneFrame>
  );
};

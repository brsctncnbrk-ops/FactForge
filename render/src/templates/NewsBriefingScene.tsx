import type { NewsBriefingSceneProps } from "../types/generated";
import { easeOut, entrance, useScene } from "../lib/anim";
import { SceneFrame } from "../lib/bits";
import { centerColumn, theme } from "../lib/theme";

export const NewsBriefingScene: React.FC<{ p: NewsBriefingSceneProps }> = ({
  p,
}) => {
  const { frame, durationInFrames, fps, width } = useScene();
  const tagT = easeOut(entrance(frame, durationInFrames, fps, 0.1, 0.4));
  const headlineT = easeOut(entrance(frame, durationInFrames, fps, 0.25, 0.7));
  // ticker crawls right-to-left across the full scene duration
  const tickerX = p.ticker
    ? width - ((frame / Math.max(durationInFrames, 1)) * (width + 1600))
    : 0;

  return (
    <SceneFrame>
      <div style={centerColumn}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 16,
            opacity: tagT,
            transform: `translateY(${(1 - tagT) * -16}px)`,
            marginBottom: 30,
          }}
        >
          <div
            style={{
              width: 16,
              height: 16,
              borderRadius: "50%",
              background: theme.accentAlt,
            }}
          />
          <div
            style={{
              fontFamily: theme.fontTitle,
              fontWeight: theme.fontWeightTitle,
              fontSize: 34,
              letterSpacing: "0.12em",
              color: theme.bg,
              background: theme.accentAlt,
              padding: "8px 28px",
              borderRadius: 8,
            }}
          >
            {p.tag ?? "BREAKING"}
          </div>
        </div>
        <div
          style={{
            fontFamily: theme.fontTitle,
            fontWeight: theme.fontWeightTitle,
            fontSize: 74,
            textAlign: "center",
            maxWidth: "82%",
            lineHeight: 1.15,
            opacity: headlineT,
            transform: `translateY(${(1 - headlineT) * 24}px)`,
          }}
        >
          {p.headline}
        </div>
      </div>
      {p.ticker ? (
        <div
          style={{
            position: "absolute",
            bottom: 0,
            left: 0,
            right: 0,
            height: 96,
            background: theme.bgAlt,
            borderTop: `4px solid ${theme.accent}`,
            display: "flex",
            alignItems: "center",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              position: "absolute",
              left: tickerX,
              whiteSpace: "nowrap",
              fontFamily: theme.fontTitle,
              fontWeight: theme.fontWeightBody,
              fontSize: 36,
              color: theme.text,
            }}
          >
            {p.ticker}
          </div>
        </div>
      ) : null}
    </SceneFrame>
  );
};

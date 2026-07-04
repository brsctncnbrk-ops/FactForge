import type { TimelineSceneProps } from "../types/generated";
import { easeOut, entrance, staggered, useScene } from "../lib/anim";
import { SceneFrame, SceneTitle } from "../lib/bits";
import { theme } from "../lib/theme";

export const TimelineScene: React.FC<{ p: TimelineSceneProps }> = ({ p }) => {
  const { frame, durationInFrames, fps } = useScene();
  const line = easeOut(entrance(frame, durationInFrames, fps, 0.4, 1.4));
  const n = p.events.length;

  return (
    <SceneFrame>
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        {p.title ? <SceneTitle text={p.title} /> : null}
        <div style={{ position: "relative", width: "80%", height: 320 }}>
          <div
            style={{
              position: "absolute",
              top: 150,
              left: 0,
              height: 4,
              width: `${line * 100}%`,
              background: theme.stroke,
            }}
          />
          {p.events.map((ev, i) => {
            const t = easeOut(staggered(frame, durationInFrames, i, n, 0.65));
            const x = (i / Math.max(n - 1, 1)) * 100;
            const hot = p.highlightIndex === i;
            return (
              <div
                key={i}
                style={{
                  position: "absolute",
                  left: `${x}%`,
                  top: 0,
                  transform: "translateX(-50%)",
                  width: 300,
                  textAlign: "center",
                  opacity: t,
                }}
              >
                <div
                  style={{
                    fontFamily: theme.fontTitle,
                    fontSize: hot ? 46 : 38,
                    color: hot ? theme.accent : theme.text,
                    height: 120,
                    display: "flex",
                    alignItems: "flex-end",
                    justifyContent: "center",
                  }}
                >
                  {ev.date ?? ""}
                </div>
                <div
                  style={{
                    width: hot ? 30 : 20,
                    height: hot ? 30 : 20,
                    borderRadius: "50%",
                    background: hot ? theme.accentAlt : theme.accent,
                    margin: "0 auto",
                    marginTop: hot ? 12 : 18,
                    transform: `scale(${0.4 + 0.6 * t})`,
                    boxShadow: hot ? `0 0 24px ${theme.accentAlt}` : "none",
                  }}
                />
                <div
                  style={{
                    marginTop: 24,
                    fontSize: hot ? 36 : 30,
                    color: hot ? theme.text : theme.textDim,
                    lineHeight: 1.25,
                  }}
                >
                  {ev.label}
                </div>
                {ev.description ? (
                  <div style={{ marginTop: 8, fontSize: 24, color: theme.textDim }}>
                    {ev.description}
                  </div>
                ) : null}
              </div>
            );
          })}
        </div>
      </div>
    </SceneFrame>
  );
};

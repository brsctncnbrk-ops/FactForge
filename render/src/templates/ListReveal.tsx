import type { ListRevealProps } from "../types/generated";
import { easeOut, staggered, useScene } from "../lib/anim";
import { SceneFrame, SceneTitle } from "../lib/bits";
import { theme } from "../lib/theme";

export const ListReveal: React.FC<{ p: ListRevealProps }> = ({ p }) => {
  const { frame, durationInFrames } = useScene();
  const n = p.items.length;

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
          padding: "0 12%",
        }}
      >
        {p.title ? <SceneTitle text={p.title} /> : null}
        <div style={{ display: "flex", flexDirection: "column", gap: 36, width: "100%" }}>
          {p.items.map((item, i) => {
            const t = easeOut(staggered(frame, durationInFrames, i, n, 0.7));
            return (
              <div
                key={i}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 32,
                  opacity: t,
                  transform: `translateX(${(1 - t) * -60}px)`,
                }}
              >
                <div
                  style={{
                    minWidth: 64,
                    height: 64,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontFamily: theme.fontTitle,
                    fontSize: 40,
                    color: theme.bg,
                    background: theme.accent,
                    borderRadius: p.numbered ? 8 : "50%",
                  }}
                >
                  {p.numbered ? i + 1 : "•"}
                </div>
                <div style={{ fontSize: 52, lineHeight: 1.25 }}>{item}</div>
              </div>
            );
          })}
        </div>
      </div>
    </SceneFrame>
  );
};

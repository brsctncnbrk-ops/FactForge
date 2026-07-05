import type { ScaleComparisonSceneProps } from "../types/generated";
import { easeOut, staggered, useScene } from "../lib/anim";
import { SceneFrame, SceneTitle } from "../lib/bits";
import { theme } from "../lib/theme";

const formatValue = (value: number, unit?: string) => {
  const n = value >= 1000 ? value.toLocaleString("en-US") : String(value);
  return unit ? `${n} ${unit}` : n;
};

export const ScaleComparisonScene: React.FC<{
  p: ScaleComparisonSceneProps;
}> = ({ p }) => {
  const { frame, durationInFrames } = useScene();
  const n = p.items.length;
  const max = Math.max(...p.items.map((it) => it.value));
  const barMaxWidth = 1400;

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
          padding: "0 6%",
        }}
      >
        {p.title ? <SceneTitle text={p.title} /> : null}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 34,
            width: "100%",
          }}
        >
          {p.items.map((item, i) => {
            const t = easeOut(staggered(frame, durationInFrames, i, n, 0.75));
            const widthPct = (item.value / max) * 100;
            return (
              <div
                key={i}
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: 10,
                  opacity: Math.min(1, t * 1.4),
                }}
              >
                <div
                  style={{
                    fontFamily: theme.fontTitle,
                    fontWeight: theme.fontWeightBody,
                    fontSize: 34,
                  }}
                >
                  {item.label}
                </div>
                <div
                  style={{
                    height: 64,
                    borderRadius: 14,
                    background: theme.panel,
                    width: barMaxWidth,
                    maxWidth: "100%",
                    display: "flex",
                    alignItems: "center",
                  }}
                >
                  <div
                    style={{
                      height: "100%",
                      width: `${widthPct * t}%`,
                      minWidth: 6,
                      borderRadius: 14,
                      background: i === 0 ? theme.accent : theme.accentAlt,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "flex-end",
                      padding: "0 18px",
                    }}
                  >
                    {t > 0.3 ? (
                      <div
                        style={{
                          fontFamily: theme.fontTitle,
                          fontWeight: theme.fontWeightTitle,
                          fontSize: 30,
                          color: theme.bg,
                          whiteSpace: "nowrap",
                        }}
                      >
                        {item.displayValue ?? formatValue(item.value, p.unit)}
                      </div>
                    ) : null}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </SceneFrame>
  );
};

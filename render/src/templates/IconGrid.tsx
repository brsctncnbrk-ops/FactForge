import type { IconGridProps } from "../types/generated";
import { staggered, useScene } from "../lib/anim";
import { SceneFrame } from "../lib/bits";
import { theme } from "../lib/theme";
import { InlineSvg } from "../lib/InlineSvg";
import { resolveAsset } from "../lib/assets";

export const IconGrid: React.FC<{ p: IconGridProps }> = ({ p }) => {
  const { frame, durationInFrames } = useScene();
  const count = Math.min(p.count, 200);
  const columns = p.columns ?? Math.ceil(Math.sqrt(count * (16 / 9)));
  const rows = Math.ceil(count / columns);
  const cell = Math.min(120, 760 / rows, 1500 / columns);
  const highlight = p.highlightCount ?? 0;

  const iconSrc = resolveAsset(p.icon);
  const secondarySrc = p.secondaryIcon ? resolveAsset(p.secondaryIcon) : null;

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
          gap: 40,
        }}
      >
        <div
          style={{
            display: "grid",
            gridTemplateColumns: `repeat(${columns}, ${cell}px)`,
            gap: Math.max(6, cell * 0.12),
          }}
        >
          {Array.from({ length: count }, (_, i) => {
            const t = staggered(frame, durationInFrames, i, count, 0.55);
            // highlighted subset = the LAST highlightCount icons (losses etc.)
            const hot = i >= count - highlight;
            return (
              <InlineSvg
                key={i}
                src={iconSrc}
                color={hot ? theme.accentAlt : theme.accent}
                style={{
                  width: cell,
                  height: cell,
                  opacity: t * (hot ? 1 : 0.9),
                  transform: `scale(${0.5 + 0.5 * t})`,
                }}
              />
            );
          })}
        </div>
        {secondarySrc && p.secondaryCount ? (
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            {Array.from({ length: Math.min(p.secondaryCount, 50) }, (_, i) => {
              const t = staggered(frame, durationInFrames, i, p.secondaryCount!, 0.8);
              return (
                <InlineSvg
                  key={i}
                  src={secondarySrc}
                  color={theme.textDim}
                  style={{ width: 60, height: 60, opacity: t }}
                />
              );
            })}
          </div>
        ) : null}
        {p.label ? (
          <div
            style={{
              fontSize: 40,
              color: theme.textDim,
              letterSpacing: "0.06em",
            }}
          >
            {p.label}
          </div>
        ) : null}
      </div>
    </SceneFrame>
  );
};

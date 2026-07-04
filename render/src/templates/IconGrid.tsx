import type { IconGridProps } from "../types/generated";
import { popIn, staggered, useScene } from "../lib/anim";
import { SceneFrame } from "../lib/bits";
import { theme } from "../lib/theme";
import { InlineSvg } from "../lib/InlineSvg";
import { resolveAsset } from "../lib/assets";

export const IconGrid: React.FC<{ p: IconGridProps }> = ({ p }) => {
  const { frame, durationInFrames, fps } = useScene();
  const count = Math.min(p.count, 200);
  const columns = p.columns ?? Math.ceil(Math.sqrt(count * (16 / 9)));
  const rows = Math.ceil(count / columns);
  const cell = Math.min(110, 700 / rows, 1360 / columns);
  const chip = cell * 0.84;
  const highlight = p.highlightCount ?? 0;

  const iconSrc = resolveAsset(p.icon);
  const secondarySrc = p.secondaryIcon ? resolveAsset(p.secondaryIcon) : null;
  // stagger the pop-in delay per cell, capped so late cells don't lag past the scene
  const maxDelayFrames = Math.min(durationInFrames * 0.4, fps * 1.2);

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
            gap: Math.max(6, cell * 0.14),
          }}
        >
          {Array.from({ length: count }, (_, i) => {
            const delay = (i / Math.max(count - 1, 1)) * maxDelayFrames;
            const t = popIn(frame, fps, delay);
            // highlighted subset = the LAST highlightCount icons (losses etc.)
            const hot = i >= count - highlight;
            return (
              <div
                key={i}
                style={{
                  width: cell,
                  height: cell,
                  borderRadius: cell * 0.22,
                  background: hot ? theme.accentAlt : theme.panel,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  opacity: Math.min(1, t * 1.3),
                  transform: `scale(${t})`,
                }}
              >
                <InlineSvg
                  src={iconSrc}
                  color={hot ? theme.text : theme.accent}
                  style={{ width: chip, height: chip }}
                />
              </div>
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
              fontFamily: theme.fontTitle,
              fontWeight: theme.fontWeightBody,
              fontSize: 40,
              color: theme.textDim,
              letterSpacing: "0.02em",
            }}
          >
            {p.label}
          </div>
        ) : null}
      </div>
    </SceneFrame>
  );
};

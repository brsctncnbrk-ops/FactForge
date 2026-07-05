import type { EvidenceBoardSceneProps } from "../types/generated";
import { popIn, useScene } from "../lib/anim";
import { SceneFrame, SceneTitle } from "../lib/bits";
import { theme } from "../lib/theme";
import { InlineSvg } from "../lib/InlineSvg";
import { resolveAsset } from "../lib/assets";

// Fixed (non-random) layout slots for up to 6 cards — deterministic across
// render workers, same rule as SceneFrame's decorative blobs.
const SLOTS: { x: number; y: number; rotate: number }[] = [
  { x: 12, y: 18, rotate: -4 },
  { x: 38, y: 10, rotate: 3 },
  { x: 64, y: 20, rotate: -2 },
  { x: 20, y: 58, rotate: 2 },
  { x: 48, y: 62, rotate: -3 },
  { x: 74, y: 56, rotate: 4 },
];

const CARD_W = 300;
const CARD_H = 220;

export const EvidenceBoardScene: React.FC<{ p: EvidenceBoardSceneProps }> = ({
  p,
}) => {
  const { frame, fps } = useScene();
  const items = p.items.slice(0, SLOTS.length);
  const centers = items.map((_, i) => {
    const slot = SLOTS[i];
    return { x: slot.x + (CARD_W / 2 / 19.2), y: slot.y + (CARD_H / 2 / 10.8) };
  });

  return (
    <SceneFrame>
      <div style={{ position: "absolute", inset: 0 }}>
        {p.title ? (
          <div style={{ position: "absolute", top: 40, left: 0, right: 0 }}>
            <SceneTitle text={p.title} />
          </div>
        ) : null}
        <svg
          style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}
        >
          {(p.connections ?? []).map(([from, to], i) => {
            if (!centers[from] || !centers[to]) return null;
            const t = popIn(frame, fps, fps * (0.6 + i * 0.15));
            return (
              <line
                key={i}
                x1={`${centers[from].x}%`}
                y1={`${centers[from].y}%`}
                x2={`${centers[from].x + (centers[to].x - centers[from].x) * Math.min(1, t)}%`}
                y2={`${centers[from].y + (centers[to].y - centers[from].y) * Math.min(1, t)}%`}
                stroke={theme.accentAlt}
                strokeWidth={3}
                strokeDasharray="2 10"
                strokeLinecap="round"
              />
            );
          })}
        </svg>
        {items.map((item, i) => {
          const slot = SLOTS[i];
          const t = popIn(frame, fps, fps * (0.15 * i));
          return (
            <div
              key={i}
              style={{
                position: "absolute",
                left: `${slot.x}%`,
                top: `${slot.y}%`,
                width: CARD_W,
                opacity: Math.min(1, t * 1.4),
                transform: `scale(${t}) rotate(${slot.rotate}deg)`,
              }}
            >
              <div
                style={{
                  width: "100%",
                  minHeight: CARD_H,
                  background: theme.text,
                  color: theme.bg,
                  borderRadius: 10,
                  boxShadow: "0 12px 24px rgba(0,0,0,0.35)",
                  padding: 20,
                  display: "flex",
                  flexDirection: "column",
                  gap: 10,
                }}
              >
                {item.icon ? (
                  <InlineSvg
                    src={resolveAsset(item.icon)}
                    color={theme.accent}
                    style={{ width: 44, height: 44 }}
                  />
                ) : null}
                <div
                  style={{
                    fontFamily: theme.fontTitle,
                    fontWeight: theme.fontWeightTitle,
                    fontSize: 26,
                    lineHeight: 1.2,
                  }}
                >
                  {item.label}
                </div>
                {item.note ? (
                  <div style={{ fontSize: 18, color: theme.bgAlt }}>
                    {item.note}
                  </div>
                ) : null}
              </div>
              {/* pin */}
              <div
                style={{
                  position: "absolute",
                  top: -10,
                  left: "50%",
                  transform: "translateX(-50%)",
                  width: 18,
                  height: 18,
                  borderRadius: "50%",
                  background: theme.accentAlt,
                  boxShadow: "0 3px 6px rgba(0,0,0,0.4)",
                }}
              />
            </div>
          );
        })}
      </div>
    </SceneFrame>
  );
};

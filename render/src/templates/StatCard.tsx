import type { StatCardProps } from "../types/generated";
import { easeOut, entrance, useScene } from "../lib/anim";
import { SceneFrame } from "../lib/bits";
import { centerColumn, theme } from "../lib/theme";
import { InlineSvg } from "../lib/InlineSvg";
import { resolveAsset } from "../lib/assets";

// "80,000" -> {num: 80000, format} so the counter animates but keeps grouping.
const parseValue = (value: string | number) => {
  if (typeof value === "number") {
    return { num: value, render: (n: number) => String(Math.round(n)) };
  }
  const cleaned = value.replace(/,/g, "");
  if (/^\d+(\.\d+)?%?$/.test(cleaned)) {
    const pct = cleaned.endsWith("%");
    const num = parseFloat(cleaned);
    const grouped = /,/.test(value);
    return {
      num,
      render: (n: number) => {
        const s = grouped
          ? Math.round(n).toLocaleString("en-US")
          : String(Math.round(n));
        return pct ? `${s}%` : s;
      },
    };
  }
  return null; // non-numeric display value: no counter
};

export const StatCard: React.FC<{ p: StatCardProps }> = ({ p }) => {
  const { frame, durationInFrames, fps } = useScene();
  const t = easeOut(entrance(frame, durationInFrames, fps, 0.45, 1.6));
  const appear = easeOut(entrance(frame, durationInFrames, fps, 0.15, 0.6));
  const parsed = parseValue(p.value);
  const countUp = p.countUp ?? true;
  const display =
    parsed && countUp ? parsed.render(parsed.num * t) : String(p.value);

  return (
    <SceneFrame>
      <div style={centerColumn}>
        {p.icon ? (
          <InlineSvg
            src={resolveAsset(p.icon)}
            color={theme.accent}
            style={{ width: 130, height: 130, opacity: appear, marginBottom: 24 }}
          />
        ) : null}
        <div
          style={{
            fontFamily: theme.fontTitle,
            // long ranges like "400,000–600,000" shrink to stay on one line
            fontSize: display.length > 12 ? 130 : display.length > 8 ? 160 : 200,
            fontWeight: 700,
            color: theme.accent,
            lineHeight: 1.05,
            opacity: appear,
            transform: `translateY(${(1 - appear) * 30}px)`,
            textAlign: "center",
            maxWidth: "90%",
          }}
        >
          {display}
        </div>
        <div
          style={{
            fontSize: 58,
            marginTop: 28,
            opacity: appear,
            textAlign: "center",
            maxWidth: "75%",
          }}
        >
          {p.label}
        </div>
        {p.secondaryText ? (
          <div
            style={{
              fontSize: 38,
              color: theme.textDim,
              marginTop: 18,
              opacity: appear,
              textAlign: "center",
              maxWidth: "70%",
            }}
          >
            {p.secondaryText}
          </div>
        ) : null}
      </div>
    </SceneFrame>
  );
};

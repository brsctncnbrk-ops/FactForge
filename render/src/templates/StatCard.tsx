import type { StatCardProps } from "../types/generated";
import { popIn, useScene } from "../lib/anim";
import { IconBadge, SceneFrame } from "../lib/bits";
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
  const { frame, fps } = useScene();
  const pop = popIn(frame, fps, 0);
  const appear = Math.min(1, popIn(frame, fps, 6) * 1.2);
  const parsed = parseValue(p.value);
  const countUp = p.countUp ?? true;
  const display =
    parsed && countUp
      ? parsed.render(parsed.num * Math.min(1, pop))
      : String(p.value);

  return (
    <SceneFrame>
      <div style={centerColumn}>
        {p.icon ? (
          <IconBadge
            size={150}
            color={theme.accentAlt}
            style={{
              marginBottom: 28,
              opacity: appear,
              transform: `scale(${pop})`,
            }}
          >
            <InlineSvg
              src={resolveAsset(p.icon)}
              color={theme.text}
              style={{ width: 84, height: 84 }}
            />
          </IconBadge>
        ) : null}
        <div
          style={{
            fontFamily: theme.fontTitle,
            fontWeight: theme.fontWeightTitle,
            // long ranges like "400,000–600,000" shrink to stay on one line
            fontSize: display.length > 12 ? 130 : display.length > 8 ? 160 : 200,
            color: theme.accent,
            lineHeight: 1.05,
            opacity: appear,
            transform: `scale(${pop})`,
            textAlign: "center",
            maxWidth: "90%",
          }}
        >
          {display}
        </div>
        <div
          style={{
            fontFamily: theme.fontTitle,
            fontWeight: theme.fontWeightBody,
            fontSize: 58,
            marginTop: 20,
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
              marginTop: 16,
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

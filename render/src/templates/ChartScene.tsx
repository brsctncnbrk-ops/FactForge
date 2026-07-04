import { interpolate } from "remotion";
import type { ChartSceneProps } from "../types/generated";
import { easeOut, entrance, useScene } from "../lib/anim";
import { SceneFrame, SceneTitle } from "../lib/bits";
import { theme } from "../lib/theme";

const W = 1200;
const H = 560;
const PAD = 90;

const seriesColors = [theme.accent, theme.accentAlt, theme.good];

export const ChartScene: React.FC<{ p: ChartSceneProps }> = ({ p }) => {
  const { frame, durationInFrames, fps } = useScene();
  // draw/grow: sweep across the first ~65% of the scene; fade: quick opacity.
  const style = p.animationStyle ?? "draw";
  const sweep =
    style === "fade"
      ? 1
      : easeOut(
          interpolate(frame, [0, durationInFrames * 0.65], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          })
        );
  const fade = easeOut(entrance(frame, durationInFrames, fps, 0.2, 0.8));

  const labels = p.data.labels;
  const allValues = p.data.series.flatMap((s) => s.values ?? []);
  const maxV = Math.max(...allValues, 1);

  const x = (i: number) =>
    PAD + (labels.length === 1 ? 0.5 : i / (labels.length - 1)) * (W - 2 * PAD);
  const y = (v: number) => H - PAD - (v / maxV) * (H - 2 * PAD);

  let body: React.ReactNode = null;

  if (p.chartType === "line") {
    body = p.data.series.map((s, si) => {
      const pts = (s.values ?? []).map((v, i) => `${x(i)},${y(v)}`).join(" ");
      const len = 3000;
      return (
        <g key={si}>
          <polyline
            points={pts}
            fill="none"
            stroke={seriesColors[si % seriesColors.length]}
            strokeWidth={7}
            strokeDasharray={len}
            strokeDashoffset={len * (1 - sweep)}
          />
          {(s.values ?? []).map((v, i) => {
            const visible = sweep >= (labels.length === 1 ? 0 : i / (labels.length - 1));
            const hot = p.highlightIndex === i;
            return visible ? (
              <circle
                key={i}
                cx={x(i)}
                cy={y(v)}
                r={hot ? 16 : 9}
                fill={hot ? theme.accentAlt : seriesColors[si % seriesColors.length]}
              />
            ) : null;
          })}
        </g>
      );
    });
  } else if (p.chartType === "bar") {
    const groups = labels.length;
    const bw = ((W - 2 * PAD) / groups) * 0.5;
    body = p.data.series.map((s, si) =>
      (s.values ?? []).map((v, i) => {
        const grow = style === "grow" || style === "draw" ? sweep : 1;
        const h = (v / maxV) * (H - 2 * PAD) * grow;
        const hot = p.highlightIndex === i;
        return (
          <rect
            key={`${si}-${i}`}
            x={x(i) - bw / 2}
            y={H - PAD - h}
            width={bw}
            height={h}
            fill={hot ? theme.accentAlt : seriesColors[si % seriesColors.length]}
            opacity={style === "fade" ? fade : 1}
          />
        );
      })
    );
  } else {
    // pie: progressive sweep of the first series
    const values = p.data.series[0]?.values ?? [];
    const total = values.reduce((a, b) => a + b, 0) || 1;
    const cx = W / 2;
    const cy = H / 2 + 10;
    const r = Math.min(W, H) / 2 - PAD / 2;
    let acc = 0;
    body = values.map((v, i) => {
      const start = (acc / total) * 2 * Math.PI * sweep;
      acc += v;
      const end = (acc / total) * 2 * Math.PI * sweep;
      const large = end - start > Math.PI ? 1 : 0;
      const p1 = [cx + r * Math.sin(start), cy - r * Math.cos(start)];
      const p2 = [cx + r * Math.sin(end), cy - r * Math.cos(end)];
      const hot = p.highlightIndex === i;
      return (
        <path
          key={i}
          d={`M ${cx} ${cy} L ${p1[0]} ${p1[1]} A ${r} ${r} 0 ${large} 1 ${p2[0]} ${p2[1]} Z`}
          fill={hot ? theme.accentAlt : seriesColors[i % seriesColors.length]}
          opacity={0.5 + 0.5 * ((i % 3) / 2)}
          stroke={theme.bg}
          strokeWidth={4}
        />
      );
    });
  }

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
        <svg width={W} height={H} style={{ opacity: style === "fade" ? fade : 1 }}>
          {p.chartType !== "pie" ? (
            <>
              <line x1={PAD} y1={H - PAD} x2={W - PAD} y2={H - PAD} stroke={theme.stroke} strokeWidth={3} />
              <line x1={PAD} y1={PAD / 2} x2={PAD} y2={H - PAD} stroke={theme.stroke} strokeWidth={3} />
            </>
          ) : null}
          {body}
          {p.chartType !== "pie"
            ? labels.map((l, i) => (
                <text
                  key={i}
                  x={x(i)}
                  y={H - PAD + 52}
                  textAnchor="middle"
                  fill={p.highlightIndex === i ? theme.accent : theme.textDim}
                  fontSize={p.highlightIndex === i ? 36 : 30}
                  fontFamily={theme.fontBody}
                >
                  {l}
                </text>
              ))
            : null}
        </svg>
        <div style={{ display: "flex", gap: 60, marginTop: 8 }}>
          {p.chartType === "pie"
            ? labels.map((l, i) => (
                <div key={i} style={{ display: "flex", alignItems: "center", gap: 12, fontSize: 30, color: theme.textDim }}>
                  <div style={{ width: 22, height: 22, background: seriesColors[i % seriesColors.length] }} />
                  {l}
                </div>
              ))
            : p.data.series.length > 1
              ? p.data.series.map((s, si) => (
                  <div key={si} style={{ display: "flex", alignItems: "center", gap: 12, fontSize: 30, color: theme.textDim }}>
                    <div style={{ width: 22, height: 22, background: seriesColors[si % seriesColors.length] }} />
                    {s.name ?? `Series ${si + 1}`}
                  </div>
                ))
              : null}
        </div>
        {p.xAxisLabel || p.yAxisLabel ? (
          <div style={{ marginTop: 10, fontSize: 28, color: theme.textDim }}>
            {[p.yAxisLabel, p.xAxisLabel].filter(Boolean).join(" · ")}
          </div>
        ) : null}
      </div>
    </SceneFrame>
  );
};

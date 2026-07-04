import { Img } from "remotion";
import type { ComparisonSplitProps, Side } from "../types/generated";
import { easeOut, entrance, staggered, useScene } from "../lib/anim";
import { SceneFrame, SceneTitle } from "../lib/bits";
import { theme } from "../lib/theme";
import { resolveAsset } from "../lib/assets";

const Panel: React.FC<{ side: Side; index: 0 | 1 }> = ({ side, index }) => {
  const { frame, durationInFrames, fps } = useScene();
  const t = easeOut(entrance(frame, durationInFrames, fps, 0.22, 0.9));
  const dir = index === 0 ? -1 : 1;

  return (
    <div
      style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        padding: "0 4%",
        opacity: t,
        transform: `translateX(${(1 - t) * 60 * dir}px)`,
      }}
    >
      <div
        style={{
          fontFamily: theme.fontTitle,
          fontSize: 56,
          color: index === 0 ? theme.accentAlt : theme.accent,
          marginBottom: 12,
          textAlign: "center",
        }}
      >
        {side.title}
      </div>
      {side.value ? (
        <div style={{ fontFamily: theme.fontTitle, fontSize: 96, marginBottom: 16 }}>
          {side.value}
        </div>
      ) : null}
      {side.image ? (
        <Img
          src={resolveAsset(side.image)}
          style={{ width: "70%", maxHeight: 300, objectFit: "contain", marginBottom: 24 }}
        />
      ) : null}
      <div style={{ display: "flex", flexDirection: "column", gap: 24, marginTop: 12 }}>
        {(side.items ?? []).map((item, i) => {
          const it = easeOut(
            staggered(frame, durationInFrames, i, side.items?.length ?? 1, 0.6)
          );
          return (
            <div
              key={i}
              style={{
                fontSize: 42,
                lineHeight: 1.3,
                opacity: it,
                textAlign: "center",
              }}
            >
              {item}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export const ComparisonSplit: React.FC<{ p: ComparisonSplitProps }> = ({ p }) => {
  const { frame, durationInFrames, fps } = useScene();
  const divider = easeOut(entrance(frame, durationInFrames, fps, 0.3, 1.2));

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
          padding: "4% 3%",
        }}
      >
        {p.heading ? <SceneTitle text={p.heading} /> : null}
        <div
          style={{
            display: "flex",
            width: "100%",
            flex: 1,
            maxHeight: 640,
            alignItems: "stretch",
          }}
        >
          <Panel side={p.left} index={0} />
          <div
            style={{
              width: 3,
              background: theme.stroke,
              transform: `scaleY(${divider})`,
            }}
          />
          <Panel side={p.right} index={1} />
        </div>
      </div>
    </SceneFrame>
  );
};

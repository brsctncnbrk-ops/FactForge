import type { FlowDiagramSceneProps } from "../types/generated";
import { easeOut, staggered, useScene } from "../lib/anim";
import { SceneFrame, SceneTitle } from "../lib/bits";
import { theme } from "../lib/theme";
import { InlineSvg } from "../lib/InlineSvg";
import { resolveAsset } from "../lib/assets";

// Step chip + the arrow that follows it (arrows draw in just after their
// step pops, so the eye reads left-to-right / top-to-bottom in order).
const Step: React.FC<{
  label: string;
  icon?: string;
  index: number;
  count: number;
  vertical: boolean;
  hot: boolean;
}> = ({ label, icon, index, count, vertical, hot }) => {
  const { frame, durationInFrames } = useScene();
  const t = easeOut(staggered(frame, durationInFrames, index, count, 0.75));
  const arrowT = easeOut(
    staggered(frame, durationInFrames, index + 0.5, count, 0.75)
  );
  const isLast = index === count - 1;

  return (
    <div
      style={{
        display: "flex",
        flexDirection: vertical ? "column" : "row",
        alignItems: "center",
        gap: vertical ? 10 : 18,
      }}
    >
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 14,
          opacity: t,
          transform: `scale(${0.85 + 0.15 * t})`,
        }}
      >
        <div
          style={{
            width: 130,
            height: 130,
            borderRadius: 24,
            background: hot ? theme.accentAlt : theme.accent,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {icon ? (
            <InlineSvg
              src={resolveAsset(icon)}
              color={theme.bg}
              style={{ width: 66, height: 66 }}
            />
          ) : (
            <div
              style={{
                fontFamily: theme.fontTitle,
                fontWeight: theme.fontWeightTitle,
                fontSize: 56,
                color: theme.bg,
              }}
            >
              {index + 1}
            </div>
          )}
        </div>
        <div
          style={{
            fontFamily: theme.fontTitle,
            fontWeight: theme.fontWeightBody,
            fontSize: 34,
            textAlign: "center",
            maxWidth: 220,
            lineHeight: 1.2,
          }}
        >
          {label}
        </div>
      </div>
      {!isLast ? (
        <div
          style={{
            flexShrink: 0,
            opacity: arrowT,
            transform: vertical
              ? `scaleY(${arrowT})`
              : `scaleX(${arrowT})`,
            transformOrigin: vertical ? "top" : "left",
          }}
        >
          {vertical ? (
            <svg width="24" height="56" viewBox="0 0 24 56">
              <path
                d="M12 0 V44 M4 36 L12 48 L20 36"
                fill="none"
                stroke={theme.textDim}
                strokeWidth="5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          ) : (
            <svg width="56" height="24" viewBox="0 0 56 24">
              <path
                d="M0 12 H44 M36 4 L48 12 L36 20"
                fill="none"
                stroke={theme.textDim}
                strokeWidth="5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          )}
        </div>
      ) : null}
    </div>
  );
};

export const FlowDiagramScene: React.FC<{ p: FlowDiagramSceneProps }> = ({
  p,
}) => {
  const vertical = p.direction === "vertical";
  const n = p.steps.length;

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
            flexDirection: vertical ? "column" : "row",
            alignItems: "center",
            justifyContent: "center",
            gap: vertical ? 4 : 10,
          }}
        >
          {p.steps.map((step, i) => (
            <Step
              key={i}
              label={step.label}
              icon={step.icon}
              index={i}
              count={n}
              vertical={vertical}
              hot={p.highlightIndex === i}
            />
          ))}
        </div>
      </div>
    </SceneFrame>
  );
};

import { Img, interpolate } from "remotion";
import type { MapSceneProps } from "../types/generated";
import { easeOut, staggered, useScene } from "../lib/anim";
import { OverlayText, SceneFrame } from "../lib/bits";
import { theme } from "../lib/theme";
import { InlineSvg } from "../lib/InlineSvg";
import { firstOfType, resolveAsset } from "../lib/assets";

// Named placements -> screen positions (% of frame). Placement strings are
// free-form in the schema; unknown ones fall back to deterministic spread
// slots so a new placement never crashes a render.
const PLACEMENTS: Record<string, { x: number; y: number }[]> = {
  center: [{ x: 50, y: 50 }],
  rome: [{ x: 47, y: 58 }],
  borders: [
    { x: 18, y: 22 },
    { x: 82, y: 24 },
    { x: 86, y: 62 },
    { x: 22, y: 74 },
  ],
  "frontier-spread": [
    { x: 30, y: 18 },
    { x: 62, y: 16 },
    { x: 84, y: 40 },
    { x: 74, y: 74 },
    { x: 28, y: 70 },
  ],
  north: [{ x: 50, y: 16 }],
  south: [{ x: 50, y: 82 }],
  east: [{ x: 84, y: 50 }],
  west: [{ x: 16, y: 50 }],
};

const FALLBACK_SLOTS = [
  { x: 35, y: 35 },
  { x: 65, y: 35 },
  { x: 65, y: 65 },
  { x: 35, y: 65 },
  { x: 50, y: 25 },
  { x: 50, y: 75 },
];

const hashString = (s: string): number => {
  let h = 0;
  for (let i = 0; i < s.length; i++) {
    h = (h * 31 + s.charCodeAt(i)) | 0;
  }
  return Math.abs(h);
};

const positionsFor = (placement: string): { x: number; y: number }[] =>
  PLACEMENTS[placement] ?? [
    FALLBACK_SLOTS[hashString(placement) % FALLBACK_SLOTS.length],
  ];

const cameraTransform = (camera: string, progress: number): string => {
  const p = progress;
  switch (camera) {
    case "slow-zoom-in":
      return `scale(${1 + 0.16 * p})`;
    case "slow-zoom-out":
      return `scale(${1.16 - 0.16 * p})`;
    case "slow-pan-left":
      return `scale(1.12) translateX(${interpolate(p, [0, 1], [3, -3])}%)`;
    case "slow-pan-right":
      return `scale(1.12) translateX(${interpolate(p, [0, 1], [-3, 3])}%)`;
    case "drift":
      return `scale(${1.08 + 0.05 * p}) translate(${-1.5 * p}%, ${1.2 * p}%)`;
    default:
      // no scene is ever a frozen frame: gentle Ken Burns as the baseline
      return `scale(${1.03 + 0.04 * p})`;
  }
};

// Expanding pulse rings behind a map marker (two rings, phase-offset). Ring
// phase derives from scene progress, so re-timed scenes stay in sync.
const PulseRings: React.FC<{ progress: number }> = ({ progress }) => (
  <>
    {[0, 0.5].map((offset) => {
      const ph = (progress * 3 + offset) % 1;
      return (
        <div
          key={offset}
          style={{
            position: "absolute",
            left: "50%",
            top: "50%",
            width: 84,
            height: 84,
            borderRadius: "50%",
            border: `3px solid ${theme.accentAlt}`,
            transform: `translate(-50%, -50%) scale(${0.6 + ph * 1.5})`,
            opacity: (1 - ph) * 0.55,
          }}
        />
      );
    })}
  </>
);

export const MapScene: React.FC<{ p: MapSceneProps; fromLibrary: string[] }> = ({
  p,
  fromLibrary,
}) => {
  const { frame, durationInFrames, progress } = useScene();
  const mapId = p.mapAsset ?? firstOfType(fromLibrary, "map");
  if (!mapId) {
    throw new Error(
      `map-scene (region "${p.region}"): no mapAsset prop and no map-type asset in fromLibrary`
    );
  }

  const icons = p.icons ?? [];
  return (
    <SceneFrame>
      <div
        style={{
          position: "absolute",
          inset: 0,
          transform: cameraTransform(p.camera, progress),
        }}
      >
        {/* flat "card" treatment: the source map is a fine multi-color/labeled
            historical atlas — recoloring its detail (duotone tint) read as a
            vintage parchment wash, not flat. Neutralizing it to grayscale and
            mounting it on a bordered flat card instead lets the ACCENT-colored
            pins/pulses/labels be the infographic layer on top. */}
        <div
          style={{
            position: "absolute",
            inset: "3%",
            background: theme.text,
            borderRadius: 28,
            border: `10px solid ${theme.accent}`,
          }}
        />
        <Img
          src={resolveAsset(mapId)}
          style={{
            position: "absolute",
            inset: "3%",
            width: "94%",
            height: "94%",
            objectFit: "contain",
            padding: "3%",
            filter: "grayscale(1) brightness(1.05) contrast(1.05)",
          }}
        />
        {icons.map((icon, i) => {
          const positions = positionsFor(icon.placement);
          const t = easeOut(staggered(frame, durationInFrames, i, icons.length, 0.5));
          return positions.map((pos, j) => (
            <div
              key={`${i}-${j}`}
              style={{
                position: "absolute",
                left: `${pos.x}%`,
                top: `${pos.y}%`,
                transform: `translate(-50%, -50%) scale(${0.4 + 0.6 * t})`,
                opacity: t,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: 6,
              }}
            >
              <div style={{ position: "relative", width: 84, height: 84 }}>
                <PulseRings progress={progress} />
                <InlineSvg
                  src={resolveAsset(icon.asset)}
                  color={theme.accentAlt}
                  style={{
                    width: 84,
                    height: 84,
                    filter: "drop-shadow(0 2px 10px rgba(0,0,0,0.6))",
                  }}
                />
              </div>
              {icon.label && j === 0 ? (
                <div
                  style={{
                    fontFamily: theme.fontTitle,
                    fontWeight: theme.fontWeightBody,
                    fontSize: 26,
                    color: theme.bg,
                    background: theme.text,
                    borderRadius: 999,
                    padding: "4px 16px",
                  }}
                >
                  {icon.label}
                </div>
              ) : null}
            </div>
          ));
        })}
      </div>
      {p.highlights && p.highlights.length > 0 ? (
        <div
          style={{
            position: "absolute",
            inset: 0,
            boxShadow: `inset 0 0 ${140 + 40 * Math.sin(progress * Math.PI * 3)}px ${theme.accentAlt}59`,
          }}
        />
      ) : null}
      {p.onScreenText ? <OverlayText text={p.onScreenText} /> : null}
    </SceneFrame>
  );
};

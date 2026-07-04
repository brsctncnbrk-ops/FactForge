// Duration-proportional animation helpers (brief §06 Temel Karar 3): all
// timings are fractions of the enclosing Sequence, so when timing-sync changes
// real scene durations, animations re-align automatically. Micro-entrances are
// capped in absolute frames so a 7s scene doesn't get a 2s fade.
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";

export const useScene = () => {
  const frame = useCurrentFrame();
  const { durationInFrames, fps, width, height } = useVideoConfig();
  const progress = durationInFrames <= 1 ? 1 : frame / (durationInFrames - 1);
  return { frame, durationInFrames, fps, width, height, progress };
};

// Entrance ramp: proportional (fraction of scene) but capped at maxFrames.
export const entrance = (
  frame: number,
  durationInFrames: number,
  fps: number,
  fraction = 0.15,
  maxSeconds = 0.6
): number => {
  const ramp = Math.max(
    1,
    Math.min(durationInFrames * fraction, maxSeconds * fps)
  );
  return interpolate(frame, [0, ramp], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
};

// Staggered entrance for item i of n: items reveal across the first `span`
// fraction of the scene, each with its own short ramp.
export const staggered = (
  frame: number,
  durationInFrames: number,
  i: number,
  n: number,
  span = 0.6
): number => {
  const window = durationInFrames * span;
  const start = n <= 1 ? 0 : (window * i) / n;
  const ramp = Math.max(1, Math.min(window / Math.max(n, 1), durationInFrames * 0.12));
  return interpolate(frame, [start, start + ramp], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
};

export const easeOut = (t: number): number => 1 - Math.pow(1 - t, 3);

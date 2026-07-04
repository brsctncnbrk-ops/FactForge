// Loads a scenes file from the staged public dir and enforces the voiced-render
// guard (brief §06 Temel Karar 4): audio may only be mounted for
// 04-scenes-final.json with an alignment-based timingMode. The guard lives in
// code so it cannot be bypassed by CLI flags.
import { staticFile } from "remotion";
import type { ScenesFile } from "../types/generated";

export type LoadedVideo = {
  data: ScenesFile;
  voiced: boolean;
  width: number;
  height: number;
};

const VOICED_TIMING_MODES = new Set([
  "forced-alignment",
  "transcript-guided-alignment",
]);

export const FINAL_FILE = "04-scenes-final.json";
export const ESTIMATED_FILE = "04-scenes-final-estimated.json";

export const loadScenesFile = async (
  slug: string,
  file: string,
  mode: "voiced" | "draft"
): Promise<LoadedVideo> => {
  const url = staticFile(`outputs/${slug}/${file}`);
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(
      `Cannot load ${file} for "${slug}" (${res.status}). Did you run: npm run stage -- ${slug} ?`
    );
  }
  const data = (await res.json()) as ScenesFile;

  if (mode === "voiced") {
    if (file !== FINAL_FILE) {
      throw new Error(
        `VOICED RENDER BLOCKED: input must be ${FINAL_FILE}, got ${file}. ` +
          "Estimated timing files are draft/silent-preview only."
      );
    }
    if (!data.timingMode || !VOICED_TIMING_MODES.has(data.timingMode)) {
      throw new Error(
        `VOICED RENDER BLOCKED: timingMode "${data.timingMode}" is not alignment-based. ` +
          "Re-run align.py Mode A against the real voiceover first."
      );
    }
    if (!data.audio?.file || !data.audio?.duration) {
      throw new Error("VOICED RENDER BLOCKED: audio metadata missing in scenes file.");
    }
  }

  const m = /^(\d{3,4})x(\d{3,4})$/.exec(data.resolution);
  if (!m) {
    throw new Error(`Bad resolution "${data.resolution}"`);
  }
  return {
    data,
    voiced: mode === "voiced",
    width: Number(m[1]),
    height: Number(m[2]),
  };
};

// Frame boundaries: scene i starts at round(startTime*fps) and runs until the
// next scene's start frame (so inter-scene narration gaps hold the current
// visual — no black frames, no overlap). The last scene runs to the end of the
// composition.
export const sceneFrameRanges = (
  data: ScenesFile,
  totalDurationInFrames: number
): { from: number; durationInFrames: number }[] => {
  const starts = data.scenes.map((s) => Math.round((s.startTime ?? 0) * data.fps));
  return data.scenes.map((_, i) => {
    const from = starts[i];
    const until = i + 1 < starts.length ? starts[i + 1] : totalDurationInFrames;
    return { from, durationInFrames: Math.max(1, until - from) };
  });
};

export const totalFrames = (loaded: LoadedVideo): number => {
  const { data } = loaded;
  if (loaded.voiced && data.audio) {
    return Math.ceil(data.audio.duration * data.fps);
  }
  const lastEnd = Math.max(
    ...data.scenes.map((s) => s.endTime ?? (s.startTime ?? 0) + (s.duration ?? 1))
  );
  return Math.ceil(lastEnd * data.fps);
};

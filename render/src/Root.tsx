// Two compositions per the voiced-render rule (brief §06 Temel Karar 4):
//   "video" — voiced final render; loads 04-scenes-final.json and REFUSES to
//             resolve unless timingMode is alignment-based (guard in lib/data).
//   "draft" — silent preview; prefers 04-scenes-final.json, falls back to the
//             estimated file. Audio is never mounted here.
// Slug comes from input props: npx remotion render video --props='{"slug":"..."}'
import { Composition, staticFile } from "remotion";
import type { CalculateMetadataFunction } from "remotion";
import { VideoComposition } from "./VideoComposition";
import type { ScenesFile } from "./types/generated";
import {
  ESTIMATED_FILE,
  FINAL_FILE,
  loadScenesFile,
  totalFrames,
} from "./lib/data";

const DEFAULT_SLUG = "why-the-roman-empire-really-collapsed";

type CompProps = {
  slug: string;
  data: ScenesFile | null;
  voiced: boolean;
};

const makeMetadata =
  (mode: "voiced" | "draft"): CalculateMetadataFunction<CompProps> =>
  async ({ props }) => {
    let file = FINAL_FILE;
    if (mode === "draft") {
      // draft falls back to the estimated file when no final exists yet
      const probe = await fetch(staticFile(`outputs/${props.slug}/${FINAL_FILE}`));
      file = probe.ok ? FINAL_FILE : ESTIMATED_FILE;
    }
    const loaded = await loadScenesFile(props.slug, file, mode);
    return {
      durationInFrames: totalFrames(loaded),
      fps: loaded.data.fps,
      width: loaded.width,
      height: loaded.height,
      props: { ...props, data: loaded.data, voiced: loaded.voiced },
    };
  };

export const Root: React.FC = () => (
  <>
    <Composition
      id="video"
      component={VideoComposition}
      durationInFrames={1}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{ slug: DEFAULT_SLUG, data: null, voiced: false }}
      calculateMetadata={makeMetadata("voiced")}
    />
    <Composition
      id="draft"
      component={VideoComposition}
      durationInFrames={1}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{ slug: DEFAULT_SLUG, data: null, voiced: false }}
      calculateMetadata={makeMetadata("draft")}
    />
  </>
);

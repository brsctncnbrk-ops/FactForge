// Compositions per the voiced-render rule (brief §06 Temel Karar 4):
//   "video"           — voiced final render; loads 04-scenes-final.json and
//                       REFUSES to resolve unless timingMode is alignment-based
//                       (guard in lib/data).
//   "video-captioned" — same guard + burned-in subtitles; additionally REFUSES
//                       unless 05-captions.json exists (build_captions.py).
//   "draft"           — silent preview; prefers 04-scenes-final.json, falls
//                       back to the estimated file. Audio is never mounted.
// Slug comes from input props: npx remotion render video --props='{"slug":"..."}'
import { Composition, staticFile } from "remotion";
import type { CalculateMetadataFunction } from "remotion";
import { VideoComposition } from "./VideoComposition";
import type { CaptionsFile, ScenesFile } from "./types/generated";
import {
  ESTIMATED_FILE,
  FINAL_FILE,
  loadScenesFile,
  totalFrames,
} from "./lib/data";
import { loadCaptions } from "./lib/captions";

const DEFAULT_SLUG = "why-the-roman-empire-really-collapsed";

type CompProps = {
  slug: string;
  data: ScenesFile | null;
  voiced: boolean;
  captions: CaptionsFile | null;
};

const makeMetadata =
  (
    mode: "voiced" | "draft",
    withCaptions = false
  ): CalculateMetadataFunction<CompProps> =>
  async ({ props }) => {
    let file = FINAL_FILE;
    if (mode === "draft") {
      // draft falls back to the estimated file when no final exists yet
      const probe = await fetch(staticFile(`outputs/${props.slug}/${FINAL_FILE}`));
      file = probe.ok ? FINAL_FILE : ESTIMATED_FILE;
    }
    const loaded = await loadScenesFile(props.slug, file, mode);
    const captions = withCaptions ? await loadCaptions(props.slug, true) : null;
    return {
      durationInFrames: totalFrames(loaded),
      fps: loaded.data.fps,
      width: loaded.width,
      height: loaded.height,
      props: { ...props, data: loaded.data, voiced: loaded.voiced, captions },
    };
  };

const defaultProps: CompProps = {
  slug: DEFAULT_SLUG,
  data: null,
  voiced: false,
  captions: null,
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
      defaultProps={defaultProps}
      calculateMetadata={makeMetadata("voiced")}
    />
    <Composition
      id="video-captioned"
      component={VideoComposition}
      durationInFrames={1}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={defaultProps}
      calculateMetadata={makeMetadata("voiced", true)}
    />
    <Composition
      id="draft"
      component={VideoComposition}
      durationInFrames={1}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={defaultProps}
      calculateMetadata={makeMetadata("draft")}
    />
  </>
);

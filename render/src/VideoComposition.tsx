// Lays the scenes on the timeline. Frame boundaries come from
// lib/data.sceneFrameRanges: each scene holds through any narration gap until
// the next scene starts (no black frames). Audio is mounted ONLY when `voiced`
// — the draft composition never passes voiced=true.
import { AbsoluteFill, Audio, Sequence, staticFile, useVideoConfig } from "remotion";
import type { CaptionsFile, ScenesFile } from "./types/generated";
import { sceneFrameRanges } from "./lib/data";
import { renderScene } from "./templates";
import { theme } from "./lib/theme";
import { CaptionOverlay } from "./CaptionOverlay";
import { CaptionsActiveContext } from "./lib/captionLayout";

export const VideoComposition: React.FC<{
  slug: string; // used by calculateMetadata to pick the scenes file
  data: ScenesFile | null;
  voiced: boolean;
  captions: CaptionsFile | null; // only set by the video-captioned composition
}> = ({ data, voiced, captions }) => {
  const { durationInFrames } = useVideoConfig();
  if (!data) {
    // defaultProps state before calculateMetadata resolves
    return <AbsoluteFill style={{ background: theme.bg }} />;
  }
  const ranges = sceneFrameRanges(data, durationInFrames);

  return (
    <AbsoluteFill style={{ background: theme.bg }}>
      {/* Scenes learn whether subtitles are burned in so their own lower-third
          text can lift clear of the caption band (video-captioned only). */}
      <CaptionsActiveContext.Provider value={captions !== null}>
        {data.scenes.map((scene, i) => (
          <Sequence
            key={scene.sceneNumber}
            name={`${String(scene.sceneNumber).padStart(2, "0")}-${scene.template}`}
            from={ranges[i].from}
            durationInFrames={ranges[i].durationInFrames}
          >
            {renderScene(scene)}
          </Sequence>
        ))}
      </CaptionsActiveContext.Provider>
      {voiced && data.audio ? (
        <Audio src={staticFile(data.audio.file.replace(/^\//, ""))} />
      ) : null}
      {captions ? <CaptionOverlay captions={captions} /> : null}
    </AbsoluteFill>
  );
};

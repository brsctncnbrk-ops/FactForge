// Loads 05-captions.json for the burned-in caption overlay. The cue list is
// produced ONLY by scripts/build_captions.py from alignment-based timing (P7);
// the renderer never computes cue timing itself — one source of truth shared
// with the SRT/VTT sidecars.
import { staticFile } from "remotion";
import type { CaptionsFile } from "../types/generated";

export const CAPTIONS_FILE = "05-captions.json";

export const loadCaptions = async (
  slug: string,
  required: boolean
): Promise<CaptionsFile | null> => {
  const res = await fetch(staticFile(`outputs/${slug}/${CAPTIONS_FILE}`));
  if (!res.ok) {
    if (required) {
      throw new Error(
        `CAPTIONED RENDER BLOCKED: ${CAPTIONS_FILE} missing for "${slug}". ` +
          `Run: python scripts/build_captions.py ${slug}  (then npm run stage -- ${slug})`
      );
    }
    return null;
  }
  const data = (await res.json()) as CaptionsFile;
  if (data.videoSlug !== slug) {
    throw new Error(
      `CAPTIONED RENDER BLOCKED: ${CAPTIONS_FILE} belongs to "${data.videoSlug}", expected "${slug}".`
    );
  }
  return data;
};

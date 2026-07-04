// FactForge render layer — Remotion project config.
// Render inputs are staged into ./public by `npm run stage -- <video-slug>`
// (deterministic script, P7). Do not put hand-made files in ./public.
import { Config } from "@remotion/cli/config";

Config.setEntryPoint("./src/index.ts");
// PNG intermediate frames: lossless before x264, so serif text stays crisp and
// dark gradients don't band (JPEG intermediates caused ringing on text edges).
Config.setVideoImageFormat("png");
// CRF 18 ≈ visually lossless for this flat-color/text content; YouTube
// re-encodes anyway, so feeding it a cleaner master is what matters.
Config.setCrf(18);
Config.setOverwriteOutput(true);

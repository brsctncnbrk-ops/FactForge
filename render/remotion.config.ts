// FactForge render layer — Remotion project config.
// Render inputs are staged into ./public by `npm run stage -- <video-slug>`
// (deterministic script, P7). Do not put hand-made files in ./public.
import { Config } from "@remotion/cli/config";

Config.setEntryPoint("./src/index.ts");
Config.setVideoImageFormat("jpeg");
// CRF default for final renders; YouTube re-encodes anyway (brief §06: 20–23).
Config.setCrf(22);
Config.setOverwriteOutput(true);

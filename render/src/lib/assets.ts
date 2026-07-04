// Manifest asset ID -> staticFile path resolution. The manifest is imported
// straight from /assets/library (single source of truth, no copy); the files
// themselves are served from render/public after `npm run stage`.
import { staticFile } from "remotion";
import manifest from "../../../assets/library/manifest.json";

type ManifestAsset = (typeof manifest)["assets"][number];

const byId = new Map<string, ManifestAsset>(
  manifest.assets.map((a) => [a.id, a])
);

// map-scene's mapAsset is optional: "otherwise taken from assets.fromLibrary"
// (template catalog) — this finds the first library id of the wanted type.
export const firstOfType = (
  ids: string[] | undefined,
  type: string
): string | undefined => ids?.find((id) => byId.get(id)?.type === type);

// Content-integrity rule: BLOCKED or Unknown-license assets never render.
export const resolveAsset = (id: string): string => {
  const asset = byId.get(id);
  if (!asset) {
    throw new Error(`Asset "${id}" is not in /assets/library/manifest.json`);
  }
  if (asset.status === "BLOCKED") {
    throw new Error(`Asset "${id}" is BLOCKED and must not be rendered`);
  }
  if (!asset.license || /unknown/i.test(asset.license)) {
    throw new Error(`Asset "${id}" has an unknown license and must not be rendered`);
  }
  return staticFile(asset.filePath.replace(/^\//, ""));
};

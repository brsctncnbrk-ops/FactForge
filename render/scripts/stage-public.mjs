// Stages render inputs into render/public (Remotion's static dir) so that
// staticFile() paths mirror repo paths 1:1. Deterministic copy script (P7);
// the repo files remain the single source of truth — ./public is gitignored
// and fully rebuilt on every run.
//
// Usage: npm run stage -- <video-slug>
// Copies:
//   /assets/library/**            -> public/assets/library/**
//   /outputs/<slug>/04-*.json     -> public/outputs/<slug>/
//   /outputs/<slug>/audio/*.mp3   -> public/outputs/<slug>/audio/   (if present)
import { cpSync, rmSync, mkdirSync, existsSync, readdirSync, copyFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const slug = process.argv[2];
if (!slug || !/^[a-z0-9]+(-[a-z0-9]+)*$/.test(slug)) {
  console.error("Usage: npm run stage -- <video-slug>   (kebab-case)");
  process.exit(1);
}

const here = dirname(fileURLToPath(import.meta.url));
const repo = join(here, "..", "..");
const pub = join(here, "..", "public");
const outDir = join(repo, "outputs", slug);

if (!existsSync(outDir)) {
  console.error(`No such output: ${outDir}`);
  process.exit(1);
}

rmSync(pub, { recursive: true, force: true });
mkdirSync(join(pub, "outputs", slug), { recursive: true });

cpSync(join(repo, "assets", "library"), join(pub, "assets", "library"), {
  recursive: true,
});

let staged = 0;
for (const f of readdirSync(outDir)) {
  if (/^04-scenes-final(-estimated)?\.json$/.test(f)) {
    copyFileSync(join(outDir, f), join(pub, "outputs", slug, f));
    console.log(`staged outputs/${slug}/${f}`);
    staged++;
  }
}
if (staged === 0) {
  console.error("No 04-scenes-final*.json found — nothing to render.");
  process.exit(1);
}

const audioDir = join(outDir, "audio");
if (existsSync(audioDir)) {
  cpSync(audioDir, join(pub, "outputs", slug, "audio"), { recursive: true });
  console.log(`staged outputs/${slug}/audio/`);
} else {
  console.log("no audio/ dir — voiced render will not be possible (draft only)");
}
console.log("stage complete -> render/public");

#!/usr/bin/env python3
"""sync_manifest_usage.py — rebuild manifest usedInVideos from scenes files (P7).

usedInVideos is NEVER hand-edited (patch Section 9). This script scans every
/outputs/*/03-scenes.json, collects each video's fromLibrary declarations,
and rewrites every manifest asset's usedInVideos as the sorted list of video
slugs that use it.

Modes:
    (default)  rewrite /assets/library/manifest.json; the top-level updatedAt
               is bumped only when content actually changed
    --check    dry mode (used by quality-gate.py): report stale entries,
               write nothing; exit 1 if stale, 0 if fresh

Exit codes: 0 fresh/synced, 1 stale (--check only), 2 setup error.

Usage:
    python scripts/sync_manifest_usage.py [--check]
    python scripts/sync_manifest_usage.py --self-test
"""

import argparse
import datetime
import json
import sys
import tempfile
from pathlib import Path


class SetupError(Exception):
    """Broken environment — no verdict possible (exit 2)."""


def find_repo_root(start):
    for p in [start] + list(start.parents):
        if (p / "templates" / "schemas" / "scenes-file.schema.json").is_file():
            return p
    raise SetupError(f"repo root not found above {start}")


def load_json(path, what):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as e:
        raise SetupError(f"{what} not readable: {path} ({e})")
    except json.JSONDecodeError as e:
        raise SetupError(f"{what} is not valid JSON: {path} ({e})")


def collect_usage(root):
    """{asset_id: sorted [video slugs]} from every /outputs/*/03-scenes.json."""
    usage = {}
    for scenes_path in sorted((root / "outputs").glob("*/03-scenes.json")):
        doc = load_json(scenes_path, "scenes file")
        slug = doc.get("videoSlug") or scenes_path.parent.name
        for scene in doc.get("scenes") or []:
            if not isinstance(scene, dict):
                continue
            assets = scene.get("assets") or {}
            for asset_id in assets.get("fromLibrary") or []:
                if isinstance(asset_id, str):
                    usage.setdefault(asset_id, set()).add(slug)
    return {k: sorted(v) for k, v in usage.items()}


def diff_manifest(manifest, usage):
    """[(asset_id, current, expected)] for every stale asset entry."""
    stale = []
    for asset in manifest.get("assets") or []:
        if not isinstance(asset, dict):
            continue
        current = asset.get("usedInVideos") or []
        expected = usage.get(asset.get("id"), [])
        if sorted(current) != expected:
            stale.append((asset.get("id"), sorted(current), expected))
    return stale


def unknown_assets(manifest, usage):
    known = {a.get("id") for a in manifest.get("assets") or [] if isinstance(a, dict)}
    return sorted(set(usage) - known)


def run(root, check):
    manifest_path = root / "assets" / "library" / "manifest.json"
    manifest = load_json(manifest_path, "asset manifest")
    usage = collect_usage(root)

    for asset_id in unknown_assets(manifest, usage):
        print(f"WARN  scenes use asset {asset_id!r} that is not in the manifest "
              "(validate.py / quality-gate.py will FAIL this)")

    stale = diff_manifest(manifest, usage)
    if check:
        for asset_id, current, expected in stale:
            print(f"STALE {asset_id}: usedInVideos {current} -> {expected}")
        if stale:
            print(f"CHECK: STALE ({len(stale)} asset(s)) — "
                  "run: python scripts/sync_manifest_usage.py")
            return 1
        print("CHECK: FRESH")
        return 0

    if not stale:
        print("SYNC: already fresh — manifest not rewritten")
        return 0
    for asset in manifest.get("assets") or []:
        if isinstance(asset, dict):
            asset["usedInVideos"] = usage.get(asset.get("id"), [])
    manifest["updatedAt"] = datetime.date.today().isoformat()
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n")
    for asset_id, current, expected in stale:
        print(f"SYNCED {asset_id}: usedInVideos {current} -> {expected}")
    print(f"SYNC: rewrote {manifest_path} ({len(stale)} asset(s) updated)")
    return 0


# --- self-test ---------------------------------------------------------------

def _asset(asset_id, used):
    return {"id": asset_id, "type": "icon", "source": "x", "sourceUrl": "",
            "license": "MIT", "attributionRequired": False,
            "attributionText": "", "filePath": f"/assets/library/icons/{asset_id}.svg",
            "tags": [], "createdAt": "2026-07-03", "updatedAt": "2026-07-03",
            "status": "ACTIVE", "reusable": True, "usedInVideos": used,
            "notes": ""}


def _scenes(slug, from_library):
    return {"videoSlug": slug, "fps": 30, "resolution": "1920x1080",
            "scenes": [{"sceneNumber": 1, "narration": "Test.", "wordCount": 1,
                        "template": "text-emphasis", "props": {"text": "T"},
                        "assets": {"fromLibrary": from_library, "newAssets": []}}]}


def self_test():
    failures = []

    def check(name, cond):
        print(f"  {'PASS' if cond else 'FAIL'}  {name}")
        if not cond:
            failures.append(name)

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "templates" / "schemas").mkdir(parents=True)
        (root / "templates" / "schemas" / "scenes-file.schema.json").write_text(
            "{}", encoding="utf-8")
        lib = root / "assets" / "library"
        lib.mkdir(parents=True)
        manifest_path = lib / "manifest.json"
        manifest_path.write_text(json.dumps({
            "version": "2.1.1", "updatedAt": "2026-01-01",
            "assets": [_asset("icon-a", []),
                       _asset("icon-b", ["stale-video-slug"]),
                       _asset("icon-unused", ["ghost-video"])],
        }, indent=2) + "\n", encoding="utf-8")
        for slug, assets in (("video-a", ["icon-a", "icon-b"]),
                             ("video-b", ["icon-b", "icon-ghost"])):
            d = root / "outputs" / slug
            d.mkdir(parents=True)
            (d / "03-scenes.json").write_text(
                json.dumps(_scenes(slug, assets)), encoding="utf-8")

        usage = collect_usage(root)
        check("usage collected across videos",
              usage == {"icon-a": ["video-a"], "icon-b": ["video-a", "video-b"],
                        "icon-ghost": ["video-b"]})
        check("deterministic", collect_usage(root) == usage)

        manifest = load_json(manifest_path, "m")
        stale = diff_manifest(manifest, usage)
        check("stale entries detected (incl. ghost-video removal)",
              sorted(s[0] for s in stale) == ["icon-a", "icon-b", "icon-unused"])
        check("unknown used asset reported",
              unknown_assets(manifest, usage) == ["icon-ghost"])
        check("--check is dry and exits 1 on stale",
              run(root, check=True) == 1
              and load_json(manifest_path, "m") == manifest)

        check("write mode exits 0", run(root, check=False) == 0)
        after = load_json(manifest_path, "m")
        by_id = {a["id"]: a for a in after["assets"]}
        check("usedInVideos rebuilt",
              by_id["icon-a"]["usedInVideos"] == ["video-a"]
              and by_id["icon-b"]["usedInVideos"] == ["video-a", "video-b"]
              and by_id["icon-unused"]["usedInVideos"] == [])
        check("updatedAt bumped on change", after["updatedAt"] != "2026-01-01")
        check("check now fresh (exit 0)", run(root, check=True) == 0)

        before_bytes = manifest_path.read_bytes()
        check("second write is a no-op (file untouched)",
              run(root, check=False) == 0
              and manifest_path.read_bytes() == before_bytes)

    print()
    if failures:
        print(f"SELF-TEST: {len(failures)} FAILURE(S): {failures}")
        return 1
    print("SELF-TEST: ALL CHECKS PASSED")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="dry mode: report staleness, write nothing, exit 1 if stale")
    ap.add_argument("--root", help="repo root override (tests)")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        sys.exit(self_test())
    try:
        root = Path(args.root) if args.root else find_repo_root(
            Path(__file__).resolve().parent)
        sys.exit(run(root, args.check))
    except SetupError as e:
        print(f"SETUP ERROR: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()

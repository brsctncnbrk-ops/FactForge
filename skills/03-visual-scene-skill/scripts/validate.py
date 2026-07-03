#!/usr/bin/env python3
"""validate.py — validate a scenes JSON file (03-scenes.json / 04-scenes-final*.json).

Check set = STABILIZATION-PATCH-v2.1.1.md Section 11 Scene Checks + Asset
Checks (1:1), plus the usedFacts -> 01-facts.json existence check pulled in
by WORKFLOW Phase 1C, plus three approved consistency extras (E1-E3).

  S1  scenes file validates against /templates/schemas/scenes-file.schema.json
  S2/S4  per-scene props validate against /templates/schemas/{template}.schema.json
         (missing required prop, enum/allowed-values violation, type errors)
  S3  unknown template name (no schema file for it)
  S5  scene narration differs from 02-script-annotated.md (parser imported
      from derive_vo.py — single patch-Section-14 parse contract; comparison
      after its canonical multi-line join; scene missing on either side = FAIL)
  F1  every usedFacts ID exists in sibling 01-facts.json
  A1  every fromLibrary id exists in manifest.json; every asset-reference
      prop value is declared in that scene's fromLibrary or newAssets
  A2  used asset with status BLOCKED or license Unknown (never relaxed)
  A3  attributionRequired asset used: 05-packaging.md exists without an
      Attribution Block = FAIL; 05-packaging.md absent = WARN (gate enforces)
  A4  distinct newAssets ids > 5 = FAIL (no flag) / WARN (--bootstrap)
  A5  manifest usedInVideos stale vs this file = WARN + sync command
  E1  duplicate sceneNumber = FAIL
  E2  same id in both fromLibrary and newAssets = FAIL
  E3  newAssets id already present in manifest = WARN

Other Section 11 groups (fact status, literal tags, VO diff, timing,
packaging) belong to quality-gate.py — the single enforcement point.

Exit codes: 0 = pass (warnings allowed), 1 = at least one FAIL,
2 = cannot validate (missing input/schema/manifest/annotated script,
unparseable JSON, jsonschema not installed) — fails closed, no verdict.

Usage:
    python validate.py <scenes.json> [--bootstrap]
    python validate.py --self-test
"""

import argparse
import copy
import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

try:
    import jsonschema
except ImportError:  # surfaced as SetupError (exit 2) in validate()
    jsonschema = None

# Asset-reference prop keys across the 12 template schemas. Extend this set
# when a new template schema introduces a differently-named asset prop.
ASSET_REF_KEYS = {"asset", "mapAsset", "backgroundAsset", "icon", "image"}

SYNC_HINT = "run: python scripts/sync_manifest_usage.py"


class SetupError(Exception):
    """Environment/input broken — no validation verdict possible (exit 2)."""


def find_repo_root(start):
    for p in [start] + list(start.parents):
        if (p / "templates" / "schemas" / "scenes-file.schema.json").is_file():
            return p
    raise SetupError(
        "repo root not found (no templates/schemas/scenes-file.schema.json "
        f"above {start})"
    )


REAL_ROOT = None  # resolved lazily; validate.py always lives inside the repo


def real_root():
    global REAL_ROOT
    if REAL_ROOT is None:
        REAL_ROOT = find_repo_root(Path(__file__).resolve().parent)
    return REAL_ROOT


def load_derive_vo():
    """Import the canonical Section 14 parser — no second parser to drift."""
    path = real_root() / "skills" / "02-script-skill" / "scripts" / "derive_vo.py"
    if not path.is_file():
        raise SetupError(f"derive_vo.py not found at {path}")
    spec = importlib.util.spec_from_file_location("derive_vo", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_json(path, what):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as e:
        raise SetupError(f"{what} not readable: {path} ({e})")
    except json.JSONDecodeError as e:
        raise SetupError(f"{what} is not valid JSON: {path} ({e})")


def collect_asset_refs(node):
    """Recursively collect prop values under asset-reference keys."""
    refs = []
    if isinstance(node, dict):
        for key in sorted(node):
            value = node[key]
            if key in ASSET_REF_KEYS and isinstance(value, str):
                refs.append(value)
            else:
                refs.extend(collect_asset_refs(value))
    elif isinstance(node, list):
        for item in node:
            refs.extend(collect_asset_refs(item))
    return refs


def schema_errors(schema, doc):
    validator = jsonschema.Draft7Validator(schema)
    return sorted(validator.iter_errors(doc), key=lambda e: e.json_path)


def validate(scenes_path, repo_root=None, bootstrap=False):
    """Return (fails, warns) for one scenes JSON file. Raises SetupError."""
    if jsonschema is None:
        raise SetupError("jsonschema library not installed (pip install jsonschema)")
    scenes_path = Path(scenes_path)
    root = Path(repo_root) if repo_root else real_root()
    schemas_dir = root / "templates" / "schemas"
    doc = load_json(scenes_path, "scenes file")
    scenes_schema = load_json(schemas_dir / "scenes-file.schema.json", "scenes-file schema")

    fails, warns = [], []

    def fail(code, msg):
        fails.append(f"{code} {msg}")

    def warn(code, msg):
        warns.append(f"{code} {msg}")

    # S1 — top-level schema validation
    for e in schema_errors(scenes_schema, doc):
        fail("S1", f"schema: {e.json_path}: {e.message}")

    scenes = doc.get("scenes") if isinstance(doc, dict) else None
    if not isinstance(scenes, list) or not all(isinstance(s, dict) for s in scenes):
        fail("S1", "scenes is not a list of objects — remaining checks skipped")
        return fails, warns

    # E1 — duplicate sceneNumber
    numbers = [s.get("sceneNumber") for s in scenes]
    for n in sorted({n for n in numbers if n is not None and numbers.count(n) > 1}):
        fail("E1", f"duplicate sceneNumber {n}")

    # S5 — narration must match the annotated script (fail closed if absent)
    annotated_path = scenes_path.parent / "02-script-annotated.md"
    if not annotated_path.is_file():
        raise SetupError(
            f"02-script-annotated.md not found next to {scenes_path.name} — "
            "narration check impossible (fail closed)"
        )
    derive_vo = load_derive_vo()
    script_scenes = derive_vo.parse_scenes(
        annotated_path.read_text(encoding="utf-8")
    )
    script_map = {s["number"]: " ".join(s["narration"]) for s in script_scenes}

    schema_cache = {}
    json_numbers = set()
    for i, scene in enumerate(scenes):
        n = scene.get("sceneNumber")
        label = f"scene {n}" if n is not None else f"scenes[{i}]"
        if n is not None:
            json_numbers.add(n)

        # S3 — unknown template / S2+S4 — props vs template schema
        template = scene.get("template")
        tpl_schema_path = schemas_dir / f"{template}.schema.json"
        if not isinstance(template, str) or not tpl_schema_path.is_file():
            fail("S3", f"{label}: unknown template {template!r}")
        else:
            if template not in schema_cache:
                schema_cache[template] = load_json(
                    tpl_schema_path, f"{template} schema"
                )
            for e in schema_errors(schema_cache[template], scene.get("props", {})):
                where = e.json_path.lstrip("$.") or "(root)"
                fail("S2/S4", f"{label}: props {where}: {e.message}")

        # S5 — narration comparison (byte-exact against the canonical join)
        narration = scene.get("narration")
        if n not in script_map:
            fail("S5", f"{label}: no '## Scene {n}' in annotated script")
        elif narration != script_map[n]:
            fail(
                "S5",
                f"{label}: narration differs from annotated script\n"
                f"       scenes file : {narration!r}\n"
                f"       script      : {script_map[n]!r}",
            )
    for n in sorted(set(script_map) - json_numbers):
        fail("S5", f"annotated script Scene {n} missing from scenes file")

    # F1 — usedFacts IDs exist in 01-facts.json
    scenes_facts = [
        (s, f)
        for s in scenes
        for f in (s.get("usedFacts") or [])
    ]
    if scenes_facts:
        facts_path = scenes_path.parent / "01-facts.json"
        try:
            facts_doc = load_json(facts_path, "01-facts.json")
            known = {
                f.get("id")
                for f in facts_doc.get("facts", [])
                if isinstance(f, dict)
            }
            for scene, fid in scenes_facts:
                if fid not in known:
                    fail(
                        "F1",
                        f"scene {scene.get('sceneNumber')}: usedFacts id "
                        f"{fid!r} not in 01-facts.json",
                    )
        except SetupError as e:
            fail("F1", f"scenes declare usedFacts but {e}")

    # Asset checks — manifest is repo-level infrastructure (fail closed)
    manifest = load_json(
        root / "assets" / "library" / "manifest.json", "asset manifest"
    )
    manifest_assets = [
        a for a in manifest.get("assets", []) if isinstance(a, dict)
    ]
    by_id = {a.get("id"): a for a in manifest_assets}

    used_lib, new_ids = set(), set()
    for i, scene in enumerate(scenes):
        n = scene.get("sceneNumber")
        label = f"scene {n}" if n is not None else f"scenes[{i}]"
        assets = scene.get("assets") or {}
        lib = [x for x in assets.get("fromLibrary") or [] if isinstance(x, str)]
        news = [
            d.get("id")
            for d in assets.get("newAssets") or []
            if isinstance(d, dict) and isinstance(d.get("id"), str)
        ]
        used_lib.update(lib)
        new_ids.update(news)

        # A1 — props refs declared in this scene; fromLibrary ids in manifest
        declared = set(lib) | set(news)
        for ref in collect_asset_refs(scene.get("props", {})):
            if ref not in declared:
                fail(
                    "A1",
                    f"{label}: props reference asset {ref!r} not declared in "
                    "the scene's fromLibrary/newAssets",
                )
        for asset_id in lib:
            if asset_id not in by_id:
                fail("A1", f"{label}: fromLibrary asset {asset_id!r} not in manifest")

        # E2 — contradiction within the scene's declarations
        for asset_id in sorted(set(lib) & set(news)):
            fail("E2", f"{label}: {asset_id!r} listed in both fromLibrary and newAssets")

    # E2 — cross-scene contradiction (library asset re-declared as new)
    for asset_id in sorted(used_lib & new_ids):
        fail("E2", f"{asset_id!r} is fromLibrary in one scene and newAssets in another")

    # E3 — "new" asset that already exists in the library
    for asset_id in sorted(new_ids & set(by_id)):
        warn("E3", f"newAssets id {asset_id!r} already in manifest — use fromLibrary")

    # A2 — BLOCKED / Unknown-license assets (never relaxed, bootstrap or not)
    for asset_id in sorted(used_lib):
        a = by_id.get(asset_id)
        if a and (a.get("status") == "BLOCKED" or a.get("license") == "Unknown"):
            fail(
                "A2",
                f"asset {asset_id!r} unusable (status={a.get('status')!r}, "
                f"license={a.get('license')!r})",
            )

    # A3 — attribution
    attribution = sorted(
        asset_id
        for asset_id in used_lib
        if by_id.get(asset_id, {}).get("attributionRequired") is True
    )
    if attribution:
        pkg_path = scenes_path.parent / "05-packaging.md"
        if pkg_path.is_file():
            if "Attribution Block" not in pkg_path.read_text(encoding="utf-8"):
                fail(
                    "A3",
                    f"attributionRequired assets {attribution} used but "
                    "05-packaging.md has no Attribution Block",
                )
        else:
            warn(
                "A3",
                f"attributionRequired assets {attribution} used; "
                "05-packaging.md not written yet — attribution pending, "
                "enforced finally by quality-gate.py",
            )

    # A4 — newAssets cap (the only check --bootstrap softens)
    if len(new_ids) > 5:
        msg = f"{len(new_ids)} distinct new assets exceeds the 5-per-video cap"
        if bootstrap:
            warn("A4", msg + " (allowed by --bootstrap; every new asset must be "
                             "reusable, licensed, and added to the manifest)")
        else:
            fail("A4", msg + " (use --bootstrap only during library bootstrap)")

    # A5 — usedInVideos staleness (WARN + sync command)
    slug = doc.get("videoSlug")
    if isinstance(slug, str):
        missing = sorted(
            asset_id
            for asset_id in used_lib
            if asset_id in by_id
            and slug not in (by_id[asset_id].get("usedInVideos") or [])
        )
        extra = sorted(
            a.get("id")
            for a in manifest_assets
            if slug in (a.get("usedInVideos") or []) and a.get("id") not in used_lib
        )
        if missing:
            warn("A5", f"usedInVideos stale — {missing} used here but do not "
                       f"list {slug!r}; {SYNC_HINT}")
        if extra:
            warn("A5", f"usedInVideos stale — {extra} list {slug!r} but are not "
                       f"used in this file; {SYNC_HINT}")

    return fails, warns


def run(scenes_path, bootstrap):
    try:
        fails, warns = validate(scenes_path, bootstrap=bootstrap)
    except SetupError as e:
        print(f"SETUP ERROR: {e}", file=sys.stderr)
        print("No validation verdict (fail closed).", file=sys.stderr)
        return 2
    for f in fails:
        print(f"FAIL  {f}")
    for w in warns:
        print(f"WARN  {w}")
    if fails:
        print(f"VALIDATE: FAIL ({len(fails)} failure(s), {len(warns)} warning(s))")
        return 1
    print(f"VALIDATE: PASS ({len(warns)} warning(s))")
    return 0


# --- self-test ---------------------------------------------------------------

ANNOTATED = """# Annotated Video Script — Sample

## Scene 1

Word Count: 8
Estimated Duration: ~3 seconds

Narration:
Rome did not fall in a single night.

Used Facts:
- F001

Visual Intent:
Map of the Roman Empire beginning to crack.

On-screen Text:
ROME DIDN'T FALL IN ONE DAY

Emotional Tone:
Serious.

## Scene 2

Word Count: 7
Estimated Duration: ~3 seconds

Narration:
It took three hundred years to break.

Used Facts:
- F002

Visual Intent:
One strong sentence on screen.

On-screen Text:
A 300-YEAR COLLAPSE

Emotional Tone:
Ominous.
"""

FACTS = {
    "videoSlug": "sample-video",
    "searchesUsed": 2,
    "searchBudget": 15,
    "sources": [
        {"id": "S001", "title": "Sample source", "url": "https://example.org",
         "type": "encyclopedia", "reliability": "high"}
    ],
    "facts": [
        {"id": "F001", "claim": "Rome did not fall in a single night.",
         "sources": ["S001"], "status": "VERIFIED",
         "scriptCritical": True, "isNumber": False},
        {"id": "F002", "claim": "The decline lasted about three hundred years.",
         "sources": ["S001"], "status": "VERIFIED",
         "scriptCritical": True, "isNumber": False},
    ],
}

MANIFEST = {
    "version": "2.1.1",
    "updatedAt": "2026-07-03",
    "assets": [
        {"id": "map-roman-empire", "type": "map", "source": "Wikimedia Commons",
         "sourceUrl": "https://commons.wikimedia.org", "license": "CC0",
         "attributionRequired": False, "attributionText": "",
         "filePath": "/assets/library/maps/map-roman-empire.svg",
         "tags": ["rome", "map"], "createdAt": "2026-07-03",
         "updatedAt": "2026-07-03", "status": "ACTIVE", "reusable": True,
         "usedInVideos": ["sample-video"], "notes": ""},
        {"id": "icon-warning-red", "type": "icon", "source": "Tabler Icons",
         "sourceUrl": "https://tabler.io/icons", "license": "MIT",
         "attributionRequired": False, "attributionText": "",
         "filePath": "/assets/library/icons/icon-warning-red.svg",
         "tags": ["warning"], "createdAt": "2026-07-03",
         "updatedAt": "2026-07-03", "status": "ACTIVE", "reusable": True,
         "usedInVideos": ["sample-video"], "notes": ""},
        {"id": "texture-old-paper", "type": "texture", "source": "Example Art",
         "sourceUrl": "https://example.org/paper", "license": "CC BY-SA",
         "attributionRequired": True, "attributionText": "Paper by Example Art",
         "filePath": "/assets/library/textures/texture-old-paper.png",
         "tags": ["paper"], "createdAt": "2026-07-03",
         "updatedAt": "2026-07-03", "status": "ACTIVE", "reusable": True,
         "usedInVideos": [], "notes": ""},
        {"id": "img-broken", "type": "image", "source": "unknown forum",
         "sourceUrl": "", "license": "Unknown",
         "attributionRequired": False, "attributionText": "",
         "filePath": "/assets/library/images/img-broken.jpg",
         "tags": [], "createdAt": "2026-07-03",
         "updatedAt": "2026-07-03", "status": "BLOCKED", "reusable": False,
         "usedInVideos": [], "notes": "license unresolved"},
    ],
}

VALID_SCENES = {
    "videoSlug": "sample-video",
    "fps": 30,
    "resolution": "1920x1080",
    "scenes": [
        {
            "sceneNumber": 1,
            "narration": "Rome did not fall in a single night.",
            "usedFacts": ["F001"],
            "wordCount": 8,
            "estimatedDuration": 3.2,
            "template": "map-scene",
            "props": {
                "region": "roman-empire-max-extent",
                "camera": "slow-zoom-out",
                "mapAsset": "map-roman-empire",
                "highlights": ["borders"],
                "icons": [{"asset": "icon-warning-red", "placement": "borders"}],
                "onScreenText": "ROME DIDN'T FALL IN ONE DAY",
            },
            "assets": {
                "fromLibrary": ["map-roman-empire", "icon-warning-red"],
                "newAssets": [],
            },
            "emotionalTone": "serious",
            "styleNotes": "Keep the map simple and readable.",
        },
        {
            "sceneNumber": 2,
            "narration": "It took three hundred years to break.",
            "usedFacts": ["F002"],
            "wordCount": 7,
            "estimatedDuration": 2.8,
            "template": "text-emphasis",
            "props": {
                "text": "A 300-YEAR COLLAPSE",
                "emphasisWords": ["300-YEAR"],
                "animation": "impact",
            },
            "assets": {"fromLibrary": [], "newAssets": []},
            "emotionalTone": "ominous",
        },
    ],
}


def self_test():
    failures = []

    def check(name, cond):
        print(f"  {'PASS' if cond else 'FAIL'}  {name}")
        if not cond:
            failures.append(name)

    def has(lines, code, fragment=""):
        return any(l.startswith(code) and fragment in l for l in lines)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        root = tmp / "repo"
        shutil.copytree(
            real_root() / "templates" / "schemas",
            root / "templates" / "schemas",
        )
        (root / "assets" / "library").mkdir(parents=True)
        case_counter = [0]

        def run_case(scenes_doc, manifest=MANIFEST, facts=FACTS,
                     annotated=ANNOTATED, packaging=None, bootstrap=False):
            case_counter[0] += 1
            out = tmp / f"case-{case_counter[0]}"
            out.mkdir()
            (root / "assets" / "library" / "manifest.json").write_text(
                json.dumps(manifest), encoding="utf-8")
            if annotated is not None:
                (out / "02-script-annotated.md").write_text(
                    annotated, encoding="utf-8")
            if facts is not None:
                (out / "01-facts.json").write_text(
                    json.dumps(facts), encoding="utf-8")
            if packaging is not None:
                (out / "05-packaging.md").write_text(packaging, encoding="utf-8")
            scenes_path = out / "03-scenes.json"
            scenes_path.write_text(json.dumps(scenes_doc), encoding="utf-8")
            return validate(scenes_path, repo_root=root, bootstrap=bootstrap)

        def variant(**scene1_updates):
            doc = copy.deepcopy(VALID_SCENES)
            doc["scenes"][0].update(scene1_updates)
            return doc

        # clean pass
        fails, warns = run_case(VALID_SCENES)
        check("valid file: no FAILs, no WARNs", fails == [] and warns == [])
        check("deterministic (second run identical)",
              run_case(VALID_SCENES) == (fails, warns))

        # S1/S3 — unknown template
        fails, _ = run_case(variant(template="hologram-scene"))
        check("unknown template -> S1 (enum) + S3 FAIL",
              has(fails, "S1") and has(fails, "S3", "hologram-scene"))

        # S2/S4 — missing required prop, enum violation
        doc = copy.deepcopy(VALID_SCENES)
        del doc["scenes"][0]["props"]["camera"]
        fails, _ = run_case(doc)
        check("missing required prop -> S2/S4 FAIL",
              has(fails, "S2/S4", "'camera' is a required property"))
        doc = copy.deepcopy(VALID_SCENES)
        doc["scenes"][0]["props"]["camera"] = "spin"
        fails, _ = run_case(doc)
        check("allowed-values violation -> S2/S4 FAIL", has(fails, "S2/S4", "spin"))

        # S5 — narration mismatch / scene missing on either side
        fails, _ = run_case(variant(narration="Rome fell overnight, actually."))
        check("narration mismatch -> S5 FAIL", has(fails, "S5", "differs"))
        doc = copy.deepcopy(VALID_SCENES)
        doc["scenes"] = doc["scenes"][:1]
        fails, _ = run_case(doc)
        check("script scene absent from JSON -> S5 FAIL",
              has(fails, "S5", "Scene 2 missing from scenes file"))
        doc = copy.deepcopy(VALID_SCENES)
        doc["scenes"][1]["sceneNumber"] = 3
        fails, _ = run_case(doc)
        check("JSON scene absent from script -> S5 FAIL",
              has(fails, "S5", "no '## Scene 3'"))

        # missing annotated script — fail closed
        try:
            run_case(VALID_SCENES, annotated=None)
            check("missing 02-script-annotated.md -> SetupError (exit 2)", False)
        except SetupError:
            check("missing 02-script-annotated.md -> SetupError (exit 2)", True)

        # F1 — usedFacts
        fails, _ = run_case(variant(usedFacts=["F001", "F999"]))
        check("unknown usedFacts id -> F1 FAIL", has(fails, "F1", "F999"))
        fails, _ = run_case(VALID_SCENES, facts=None)
        check("usedFacts without 01-facts.json -> F1 FAIL",
              has(fails, "F1", "not readable"))

        # A1 — undeclared props ref / fromLibrary not in manifest
        doc = copy.deepcopy(VALID_SCENES)
        doc["scenes"][0]["assets"]["fromLibrary"] = ["map-roman-empire"]
        fails, _ = run_case(doc)
        check("props ref not declared in scene assets -> A1 FAIL",
              has(fails, "A1", "icon-warning-red"))
        doc = copy.deepcopy(VALID_SCENES)
        doc["scenes"][0]["assets"]["fromLibrary"].append("ghost-asset")
        fails, _ = run_case(doc)
        check("fromLibrary asset not in manifest -> A1 FAIL",
              has(fails, "A1", "ghost-asset"))

        # A2 — BLOCKED / Unknown license
        doc = copy.deepcopy(VALID_SCENES)
        doc["scenes"][1]["assets"]["fromLibrary"] = ["img-broken"]
        fails, _ = run_case(doc)
        check("BLOCKED/Unknown-license asset -> A2 FAIL",
              has(fails, "A2", "img-broken"))

        # A3 — attribution pending (WARN) vs missing block (FAIL) vs present
        attributed = copy.deepcopy(VALID_SCENES)
        attributed["scenes"][1]["assets"]["fromLibrary"] = ["texture-old-paper"]
        fails, warns = run_case(attributed)
        check("attribution, no 05-packaging.md -> A3 WARN not FAIL",
              has(warns, "A3", "pending") and not has(fails, "A3"))
        fails, _ = run_case(attributed, packaging="# Packaging\nNo credits here.\n")
        check("attribution, packaging without block -> A3 FAIL",
              has(fails, "A3", "no Attribution Block"))
        fails, _ = run_case(
            attributed,
            packaging="# Packaging\n\n## Attribution Block\nPaper by Example Art\n")
        check("attribution, block present -> no A3 FAIL", not has(fails, "A3"))

        # A4 — newAssets cap; --bootstrap softens ONLY this check
        many = copy.deepcopy(VALID_SCENES)
        many["scenes"][0]["assets"]["newAssets"] = [
            {"id": f"new-asset-{i}", "description": "x", "suggestedSource": "y"}
            for i in range(1, 7)
        ]
        fails, warns = run_case(many)
        check("6 new assets without flag -> A4 FAIL", has(fails, "A4"))
        fails, warns = run_case(many, bootstrap=True)
        check("6 new assets with --bootstrap -> A4 WARN not FAIL",
              has(warns, "A4") and not has(fails, "A4"))
        blocked_boot = copy.deepcopy(many)
        blocked_boot["scenes"][1]["assets"]["fromLibrary"] = ["img-broken"]
        fails, _ = run_case(blocked_boot, bootstrap=True)
        check("--bootstrap does NOT relax A2", has(fails, "A2", "img-broken"))

        # A5 — usedInVideos staleness, both directions
        fails, warns = run_case(attributed)  # texture used but lists no videos
        check("used asset not listing slug -> A5 WARN",
              has(warns, "A5", "texture-old-paper") and not has(fails, "A5"))
        doc = copy.deepcopy(VALID_SCENES)
        doc["scenes"][0]["assets"]["fromLibrary"] = ["map-roman-empire"]
        doc["scenes"][0]["props"]["icons"] = []
        _, warns = run_case(doc)  # icon-warning-red lists slug but is unused
        check("manifest lists slug for unused asset -> A5 WARN",
              has(warns, "A5", "icon-warning-red"))

        # E1 / E2 / E3
        doc = copy.deepcopy(VALID_SCENES)
        doc["scenes"][1]["sceneNumber"] = 1
        fails, _ = run_case(doc)
        check("duplicate sceneNumber -> E1 FAIL", has(fails, "E1"))
        doc = copy.deepcopy(VALID_SCENES)
        doc["scenes"][0]["assets"]["newAssets"] = [{"id": "icon-warning-red"}]
        fails, _ = run_case(doc)
        check("id in both fromLibrary and newAssets -> E2 FAIL",
              has(fails, "E2", "icon-warning-red"))
        doc = copy.deepcopy(VALID_SCENES)
        doc["scenes"][1]["assets"]["newAssets"] = [{"id": "texture-old-paper"}]
        fails, warns = run_case(doc)
        check("newAssets id already in manifest -> E3 WARN not FAIL",
              has(warns, "E3", "texture-old-paper") and not has(fails, "E3"))

        # broken input — fail closed
        out = tmp / "broken"
        out.mkdir()
        (out / "02-script-annotated.md").write_text(ANNOTATED, encoding="utf-8")
        bad = out / "03-scenes.json"
        bad.write_text("{not json", encoding="utf-8")
        try:
            validate(bad, repo_root=root)
            check("unparseable scenes JSON -> SetupError (exit 2)", False)
        except SetupError:
            check("unparseable scenes JSON -> SetupError (exit 2)", True)

    print()
    if failures:
        print(f"SELF-TEST: {len(failures)} FAILURE(S): {failures}")
        return 1
    print("SELF-TEST: ALL CHECKS PASSED")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("scenes", nargs="?",
                    help="path to 03-scenes.json or 04-scenes-final*.json")
    ap.add_argument("--bootstrap", action="store_true",
                    help="library bootstrap period: newAssets>5 warns instead "
                         "of failing (nothing else is relaxed)")
    ap.add_argument("--self-test", action="store_true",
                    help="run the embedded self-test and exit")
    args = ap.parse_args()

    if args.self_test:
        sys.exit(self_test())
    if not args.scenes:
        ap.error("scenes file required (or use --self-test)")
    sys.exit(run(args.scenes, args.bootstrap))


if __name__ == "__main__":
    main()

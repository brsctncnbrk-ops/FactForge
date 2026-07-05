#!/usr/bin/env python3
"""quality-gate.py — Layer 1 mechanical quality gate (patch Section 11, zero token).

Check groups (all mechanical; fact checks read 01-facts.json ONLY, never
markdown):
  FP  expected pipeline files present (research, facts, script, VO, scenes,
      packaging, a 04 timing file)
  FC  facts-file schema; used fact IDs exist; used fact status VERIFY = FAIL;
      used scriptCritical/isNumber facts must be VERIFIED; literal
      VERIFY/SINGLE-SOURCE bracket-tags outside 01-research.md/01-facts.json
      = FAIL; digit-in-narration with empty usedFacts = WARN (human checklist)
  VC  derive_vo.py re-run (imported); diff vs 02-script-voiceover.txt != 0
      = FAIL; derive warnings surfaced as gate WARNs
  SC  Scene + Asset checks delegated to imported validate.py (single
      implementation) on 03-scenes.json and every 04-scenes-final*.json
  TC  04 file: timingMode + audio metadata present; 04-scenes-final.json with
      an estimate timingMode = FAIL (voiced-final-render rule); scene > 12s /
      < 2s WARN; alignment-mode confidence < 0.80 WARN, < 0.60 FAIL
  PC  Script Hook Promise section missing = FAIL; Hook Promise Audit
      PENDING = WARN
  DV  Scene diversity (mechanical only — see /templates/VISUAL-QC-CHECKLIST.md
      for the judgmental half): same `template` in 3+ consecutive scenes =
      WARN; a single library asset used in > half the scenes (5+ scene
      videos) = WARN
  +   sync_manifest_usage staleness = WARN with command

NO judgmental checks: title/thumbnail/description claim support, and
whether a scene "looks amateur/boring", belong to the Layer 2 human
checklist (patch Section 12 / /templates/VISUAL-QC-CHECKLIST.md), never to
this script.

STATUS.md: this script rewrites ONLY the block between the QG markers (see
patch Section 10); Video Info, Session Notes, Quota Notes and everything
else belong to the human/skills. Missing STATUS.md is created from
/templates/STATUS-template.md.

Exit codes: 0 PASS (warnings allowed), 1 FAIL, 2 cannot run (fail closed).

Usage:
    python scripts/quality-gate.py <video-slug | output-dir> [--bootstrap]
    python scripts/quality-gate.py --self-test
"""

import argparse
import copy
import datetime
import importlib.util
import json
import re
import shutil
import sys
import tempfile
from collections import Counter
from pathlib import Path

try:
    import jsonschema
except ImportError:
    jsonschema = None

QG_BEGIN = "<!-- QG:BEGIN — bu blok quality-gate.py tarafından üretilir, elle düzenleme -->"
QG_END = "<!-- QG:END -->"
# built via concat so this file never contains the banned literals itself
TAG_VERIFY = "[" + "VERIFY" + "]"
TAG_SINGLE = "[" + "SINGLE-SOURCE" + "]"
ALIGNMENT_MODES = ("forced-alignment", "transcript-guided-alignment")
ESTIMATE_MODES = ("proportional-estimate", "word-count-estimate")
CONF_WARN = 0.80
CONF_FAIL = 0.60
LONG_SCENE_S = 12.0
SHORT_SCENE_S = 2.0
DIVERSITY_RUN_WARN = 3       # same template N+ scenes running -> WARN
DIVERSITY_MIN_SCENES = 5     # asset-share check only applies past this size
DIVERSITY_ASSET_SHARE = 0.5  # single asset in > this share of scenes -> WARN


class SetupError(Exception):
    """Gate cannot run at all (exit 2)."""


def find_repo_root(start):
    for p in [start] + list(start.parents):
        if (p / "templates" / "schemas" / "scenes-file.schema.json").is_file():
            return p
    raise SetupError(f"repo root not found above {start}")


def load_module(name, path):
    if not Path(path).is_file():
        raise SetupError(f"required module missing: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def real_root():
    return find_repo_root(Path(__file__).resolve().parent)


def modules():
    root = real_root()
    return (
        load_module("derive_vo", root / "skills" / "02-script-skill" / "scripts"
                    / "derive_vo.py"),
        load_module("validate_scenes", root / "skills" / "03-visual-scene-skill"
                    / "scripts" / "validate.py"),
        load_module("sync_usage", Path(__file__).resolve().parent
                    / "sync_manifest_usage.py"),
    )


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def scene_duration(scene):
    if isinstance(scene.get("duration"), (int, float)):
        return scene["duration"]
    if isinstance(scene.get("startTime"), (int, float)) and \
            isinstance(scene.get("endTime"), (int, float)):
        return scene["endTime"] - scene["startTime"]
    return scene.get("estimatedDuration")


def gate(out_dir, root=None, bootstrap=False):
    """Return (fails, warns, info). info feeds the QG block."""
    if jsonschema is None:
        raise SetupError("jsonschema library not installed")
    out_dir = Path(out_dir)
    root = Path(root) if root else real_root()
    derive_vo, validate_mod, sync_mod = modules()
    fails, warns = [], []
    info = {}

    def fail(code, msg):
        fails.append(f"{code} {msg}")

    def warn(code, msg):
        warns.append(f"{code} {msg}")

    # FP — expected files
    required = ["01-research.md", "01-facts.json", "02-script-annotated.md",
                "02-script-voiceover.txt", "03-scenes.json", "05-packaging.md"]
    for name in required:
        if not (out_dir / name).is_file():
            fail("FP", f"expected file missing: {name}")
    final_path = out_dir / "04-scenes-final.json"
    est_path = out_dir / "04-scenes-final-estimated.json"
    if not final_path.is_file() and not est_path.is_file():
        fail("FP", "no timing output (04-scenes-final.json or "
                   "04-scenes-final-estimated.json)")

    # load what exists (guarded)
    def safe_json(path):
        try:
            return load_json(path)
        except (OSError, json.JSONDecodeError):
            return None

    scenes_doc = safe_json(out_dir / "03-scenes.json")
    facts_doc = safe_json(out_dir / "01-facts.json")
    scenes = (scenes_doc or {}).get("scenes") or []
    scenes = [s for s in scenes if isinstance(s, dict)]

    # FC — facts (01-facts.json ONLY; markdown is never parsed)
    if facts_doc is not None:
        schema = safe_json(root / "templates" / "schemas" / "facts-file.schema.json")
        if schema is None:
            raise SetupError("facts-file.schema.json missing/unreadable")
        for e in sorted(jsonschema.Draft7Validator(schema).iter_errors(facts_doc),
                        key=lambda e: e.json_path):
            fail("FC1", f"01-facts.json schema: {e.json_path}: {e.message}")
    facts_by_id = {
        f.get("id"): f
        for f in (facts_doc or {}).get("facts") or []
        if isinstance(f, dict)
    }
    used_ids = []
    for s in scenes:
        for fid in s.get("usedFacts") or []:
            if fid not in used_ids:
                used_ids.append(fid)
    verify_violations = 0
    critical_ok = True
    for fid in used_ids:
        f = facts_by_id.get(fid)
        if f is None:
            fail("FC2", f"used fact {fid} not in 01-facts.json")
            continue
        status = f.get("status")
        if status == "VERIFY":
            verify_violations += 1
            fail("FC3", f"used fact {fid} has VERIFY status")
        if f.get("scriptCritical") is True and status != "VERIFIED":
            critical_ok = False
            fail("FC4", f"used scriptCritical fact {fid} is {status}, not VERIFIED")
        if f.get("isNumber") is True and status != "VERIFIED":
            fail("FC5", f"used isNumber fact {fid} is {status}, not VERIFIED")
    info["facts"] = (f"{len(used_ids)} fact(s) used | VERIFY-status violations: "
                     f"{verify_violations} | scriptCritical all VERIFIED: "
                     f"{'yes' if critical_ok else 'NO'}")

    # FC6 — literal tags outside 01-research.md / 01-facts.json
    allowed = {"01-research.md", "01-facts.json"}
    if out_dir.is_dir():
        for path in sorted(out_dir.rglob("*")):
            if (path.suffix not in (".md", ".txt", ".json") or not path.is_file()
                    or path.name in allowed):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for tag in (TAG_VERIFY, TAG_SINGLE):
                if tag in text:
                    fail("FC6", f"literal {tag} tag in "
                                f"{path.relative_to(out_dir).as_posix()}")

    # FC7 — digit in narration but no usedFacts (heuristic, human checklist)
    number_warns = 0
    for s in scenes:
        if re.search(r"\d", s.get("narration") or "") and not s.get("usedFacts"):
            number_warns += 1
            warn("FC7", f"scene {s.get('sceneNumber')}: narration contains a "
                        "digit but usedFacts is empty — review in the human "
                        "checklist")
    info["facts"] += f" | number-without-fact warnings: {number_warns}"

    # VC — VO re-derivation diff (P4)
    annotated_path = out_dir / "02-script-annotated.md"
    vo_path = out_dir / "02-script-voiceover.txt"
    vo_ok = "n/a"
    if annotated_path.is_file() and vo_path.is_file():
        try:
            vo_text, _, dwarns = derive_vo.derive(
                annotated_path.read_text(encoding="utf-8"))
            if vo_text != vo_path.read_text(encoding="utf-8"):
                vo_ok = "FAIL"
                fail("VC1", "02-script-voiceover.txt differs from re-derived VO "
                            "(hand-edited or stale — re-run derive_vo.py)")
            else:
                vo_ok = "OK"
            for w in dwarns:
                warn("VC", f"derive_vo: {w}")
        except derive_vo.ParseError as e:
            vo_ok = "FAIL"
            fail("VC1", f"derive_vo parse error: {e}")
    info["vo"] = vo_ok

    # SC — Scene + Asset checks, delegated to validate.py (one implementation)
    validated = []
    for path in [out_dir / "03-scenes.json", final_path, est_path]:
        if not path.is_file():
            continue
        try:
            vf, vw = validate_mod.validate(path, repo_root=root, bootstrap=bootstrap)
            for line in vf:
                fail("SC", f"{path.name}: {line}")
            for line in vw:
                warn("SC", f"{path.name}: {line}")
            validated.append(f"{path.name}: {'OK' if not vf else 'FAIL'}")
        except validate_mod.SetupError as e:
            fail("SC", f"{path.name}: cannot validate: {e}")
            validated.append(f"{path.name}: FAIL")
    info["validated"] = " | ".join(validated) if validated else "n/a"

    # DV — scene diversity (mechanical only; "does it look boring/amateur"
    # stays in the human VISUAL-QC-CHECKLIST.md, never here)
    dv_scenes = sorted(scenes, key=lambda s: s.get("sceneNumber", 0))
    run_template, run_len, flagged_templates = None, 0, set()
    for s in dv_scenes:
        t = s.get("template")
        run_len = run_len + 1 if t is not None and t == run_template else 1
        run_template = t
        if run_len == DIVERSITY_RUN_WARN and t not in flagged_templates:
            flagged_templates.add(t)
            warn("DV1", f"template {t!r} used in {run_len}+ consecutive "
                        f"scenes (through scene {s.get('sceneNumber')}) — "
                        "low scene-type diversity, vary the template")
    asset_counts = Counter()
    for s in dv_scenes:
        for a in (s.get("assets") or {}).get("fromLibrary") or []:
            if isinstance(a, str):
                asset_counts[a] += 1
    total_scenes = len(dv_scenes)
    overused = sorted(
        a for a, c in asset_counts.items()
        if total_scenes >= DIVERSITY_MIN_SCENES
        and c / total_scenes > DIVERSITY_ASSET_SHARE)
    for a in overused:
        c = asset_counts[a]
        warn("DV2", f"asset {a!r} used in {c}/{total_scenes} scenes "
                    f"({c / total_scenes:.0%}) — consider more asset variety")
    info["diversity"] = (
        f"consecutive-template warnings: {len(flagged_templates)} | "
        f"overused assets: {', '.join(overused) if overused else 'none'}")

    # asset summary for the QG block
    used_lib, new_ids = set(), set()
    for s in scenes:
        assets = s.get("assets") or {}
        used_lib.update(x for x in assets.get("fromLibrary") or []
                        if isinstance(x, str))
        new_ids.update(d.get("id") for d in assets.get("newAssets") or []
                       if isinstance(d, dict) and isinstance(d.get("id"), str))
    manifest = safe_json(root / "assets" / "library" / "manifest.json") or {}
    by_id = {a.get("id"): a for a in manifest.get("assets") or []
             if isinstance(a, dict)}
    blocked = sorted(a for a in used_lib
                     if by_id.get(a, {}).get("status") == "BLOCKED"
                     or by_id.get(a, {}).get("license") == "Unknown")
    attribution = sorted(a for a in used_lib
                         if by_id.get(a, {}).get("attributionRequired") is True)
    if attribution:
        pkg = out_dir / "05-packaging.md"
        attr_state = ("present" if pkg.is_file()
                      and "Attribution Block" in pkg.read_text(encoding="utf-8")
                      else "MISSING/pending")
    else:
        attr_state = "not needed"

    # sync staleness (patch Section 9) — WARN + command
    try:
        usage = sync_mod.collect_usage(root)
        stale = sync_mod.diff_manifest(manifest, usage)
    except sync_mod.SetupError:
        stale = []
    sync_state = "fresh" if not stale else "STALE"
    if stale:
        warn("SY", f"manifest usedInVideos stale for "
                   f"{sorted(s[0] for s in stale)} — "
                   "run: python scripts/sync_manifest_usage.py")
    info["assets"] = (f"{len(used_lib)} library asset(s), {len(new_ids)} new | "
                      f"BLOCKED/Unknown violations: {len(blocked)} | "
                      f"attribution: {attr_state} | usedInVideos sync: {sync_state}")

    # TC — timing
    timing_mode, audio_present, min_conf = "n/a", "no", None
    render_input = final_path.is_file()
    timing_doc = safe_json(final_path) if final_path.is_file() else (
        safe_json(est_path) if est_path.is_file() else None)
    if timing_doc is not None:
        name = final_path.name if final_path.is_file() else est_path.name
        timing_mode = timing_doc.get("timingMode")
        if not timing_mode:
            timing_mode = "MISSING"
            fail("TC1", f"{name}: timingMode missing")
        if not isinstance(timing_doc.get("audio"), dict):
            fail("TC1", f"{name}: audio metadata block missing")
        else:
            audio_file = timing_doc["audio"].get("file") or ""
            audio_disk = root / audio_file.lstrip("/")
            audio_present = "yes" if audio_disk.is_file() else "no"
        if render_input and timing_mode in ESTIMATE_MODES:
            fail("TC2", f"04-scenes-final.json carries estimate timingMode "
                        f"{timing_mode!r} — not a valid voiced-final-render input")
        if not render_input:
            warn("TC2", "only estimated timing exists — voiced final render "
                        "not allowed yet (run align.py Mode A when audio is ready)")
        confs = []
        for s in sorted((timing_doc.get("scenes") or []),
                        key=lambda s: s.get("sceneNumber", 0)):
            if not isinstance(s, dict):
                continue
            n = s.get("sceneNumber")
            d = scene_duration(s)
            if isinstance(d, (int, float)):
                if d > LONG_SCENE_S:
                    warn("TC3", f"LONG SCENE {n}: {round(d, 2)}s > {LONG_SCENE_S}s")
                if d < SHORT_SCENE_S:
                    warn("TC3", f"SHORT SCENE {n}: {round(d, 2)}s < {SHORT_SCENE_S}s")
            if timing_mode in ALIGNMENT_MODES:
                c = s.get("confidence")
                if not isinstance(c, (int, float)):
                    warn("TC4", f"scene {n}: no confidence recorded")
                elif c < CONF_FAIL:
                    confs.append(c)
                    fail("TC4", f"scene {n}: confidence {c} < {CONF_FAIL}")
                elif c < CONF_WARN:
                    confs.append(c)
                    warn("TC4", f"scene {n}: confidence {c} < {CONF_WARN}")
                else:
                    confs.append(c)
        if timing_mode in ALIGNMENT_MODES and audio_present == "no":
            warn("TC1", "alignment timingMode but audio file not found on disk")
        min_conf = min(confs) if confs else None
    info["timing_mode"] = timing_mode
    info["audio_present"] = audio_present
    info["min_conf"] = min_conf

    # PC — packaging
    pkg_path = out_dir / "05-packaging.md"
    if pkg_path.is_file():
        pkg_text = pkg_path.read_text(encoding="utf-8")
        if "## Script Hook Promise" not in pkg_text:
            fail("PC1", "05-packaging.md has no '## Script Hook Promise' section")
    if annotated_path.is_file():
        ann_text = annotated_path.read_text(encoding="utf-8")
        if "## Hook Promise Audit" not in ann_text:
            warn("PC2", "02-script-annotated.md has no Hook Promise Audit section")
        elif "PENDING" in ann_text.split("## Hook Promise Audit", 1)[1]:
            warn("PC2", "Hook Promise Audit is PENDING — re-check once 05A exists")

    return fails, warns, info


def build_qg_block(fails, warns, info, bootstrap):
    verdict = ("PASS" if not fails else "FAIL")
    render_ok = (not fails and info.get("timing_mode") in ALIGNMENT_MODES)
    conf = info.get("min_conf")
    lines = [
        f"Gate Result        : {verdict} ({len(fails)} failure(s), "
        f"{len(warns)} warning(s))",
        f"Gate Run           : "
        f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} | "
        f"bootstrap: {'yes' if bootstrap else 'no'}",
        f"Validation Status  : derive_vo diff: {info.get('vo')} | "
        f"{info.get('validated')}",
        f"Fact Status        : {info.get('facts')}",
        f"Asset Status       : {info.get('assets')}",
        f"Diversity Status   : {info.get('diversity')}",
        f"Timing Status      : timingMode: {info.get('timing_mode')} | "
        f"audio file present: {info.get('audio_present')} | "
        f"min scene confidence: "
        f"{conf if conf is not None else 'n/a'} | "
        f"voiced final render allowed: {'yes' if render_ok else 'NO'}",
        "",
        "Failures:",
    ]
    lines += [f"- {f}" for f in fails] or []
    if not fails:
        lines.append("- none")
    lines.append("Warnings:")
    lines += [f"- {w}" for w in warns]
    if not warns:
        lines.append("- none")
    return "\n".join(lines)


def write_qg_block(status_path, block, root):
    status_path = Path(status_path)
    if not status_path.is_file():
        template = root / "templates" / "STATUS-template.md"
        if template.is_file():
            shutil.copyfile(template, status_path)
        else:
            status_path.write_text(f"# Production Status\n\n{QG_BEGIN}\n{QG_END}\n",
                                   encoding="utf-8", newline="\n")
    text = status_path.read_text(encoding="utf-8")
    replacement = f"{QG_BEGIN}\n{block}\n{QG_END}"
    if QG_BEGIN in text and QG_END in text:
        pre = text.split(QG_BEGIN, 1)[0]
        post = text.split(QG_END, 1)[1]
        text = pre + replacement + post
    else:
        text = text.rstrip("\n") + f"\n\n## Quality Gate\n\n{replacement}\n"
    status_path.write_text(text, encoding="utf-8", newline="\n")


def run(target, bootstrap):
    root = real_root()
    out_dir = Path(target)
    if not out_dir.is_dir():
        out_dir = root / "outputs" / str(target)
    if not out_dir.is_dir():
        raise SetupError(f"output folder not found: {target}")
    fails, warns, info = gate(out_dir, root=root, bootstrap=bootstrap)
    block = build_qg_block(fails, warns, info, bootstrap)
    write_qg_block(out_dir / "STATUS.md", block, root)
    print(block)
    print()
    print(f"QG block written to {out_dir / 'STATUS.md'}")
    if fails:
        print("QUALITY GATE: FAIL — render must not be triggered")
        return 1
    print("QUALITY GATE: PASS")
    return 0


# --- self-test ---------------------------------------------------------------

ANNOTATED_TMPL = """# Annotated Video Script — Sample

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

Word Count: {wc2}
Estimated Duration: ~3 seconds

Narration:
{narr2}

Used Facts:
{used2}

Visual Intent:
One strong sentence on screen.

On-screen Text:
A 300-YEAR COLLAPSE

Emotional Tone:
Ominous.

## Hook Promise Audit

Hook Match:
{audit}

Reason:
Sample.
"""

FACTS = {
    "videoSlug": "sample-video",
    "searchesUsed": 2,
    "searchBudget": 15,
    "sources": [
        {"id": "S001", "title": "Source One", "url": "https://example.org/1",
         "type": "encyclopedic", "reliability": "high"},
        {"id": "S002", "title": "Source Two", "url": "https://example.org/2",
         "type": "academic", "reliability": "high"},
    ],
    "facts": [
        {"id": "F001", "claim": "Rome did not fall in a single night.",
         "sources": ["S001", "S002"], "status": "VERIFIED",
         "scriptCritical": True, "isNumber": False},
        {"id": "F002", "claim": "The decline lasted about three hundred years.",
         "sources": ["S001", "S002"], "status": "VERIFIED",
         "scriptCritical": True, "isNumber": True},
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
         "tags": ["rome"], "createdAt": "2026-07-03", "updatedAt": "2026-07-03",
         "status": "ACTIVE", "reusable": True,
         "usedInVideos": ["sample-video"], "notes": ""},
        {"id": "icon-warning-red", "type": "icon", "source": "Tabler Icons",
         "sourceUrl": "https://tabler.io/icons", "license": "MIT",
         "attributionRequired": False, "attributionText": "",
         "filePath": "/assets/library/icons/icon-warning-red.svg",
         "tags": ["warning"], "createdAt": "2026-07-03",
         "updatedAt": "2026-07-03", "status": "ACTIVE", "reusable": True,
         "usedInVideos": ["sample-video"], "notes": ""},
    ],
}

PACKAGING = """# 05A — Packaging Core

## Main YouTube Title

Why Rome Was Already Dead Before It Fell

## Script Hook Promise

Main Viewer Promise:
The fall of Rome was an inside job that took three centuries.

Hook Must Establish:
- Rome did not fall in one night
- The decline was already old news by 476

Avoid:
- Misleading angle
- Slow generic intro
"""


def _scenes_doc(narr2, used2):
    return {
        "videoSlug": "sample-video",
        "fps": 30,
        "resolution": "1920x1080",
        "scenes": [
            {"sceneNumber": 1,
             "narration": "Rome did not fall in a single night.",
             "usedFacts": ["F001"], "wordCount": 8, "estimatedDuration": 3.2,
             "template": "map-scene",
             "props": {"region": "roman-empire-max-extent",
                       "camera": "slow-zoom-out",
                       "mapAsset": "map-roman-empire",
                       "icons": [{"asset": "icon-warning-red",
                                  "placement": "borders"}],
                       "onScreenText": "ROME DIDN'T FALL IN ONE DAY"},
             "assets": {"fromLibrary": ["map-roman-empire", "icon-warning-red"],
                        "newAssets": []},
             "emotionalTone": "serious"},
            {"sceneNumber": 2, "narration": narr2,
             "usedFacts": used2, "wordCount": len(narr2.split()),
             "estimatedDuration": len(narr2.split()) / 2.5,
             "template": "text-emphasis",
             "props": {"text": "A 300-YEAR COLLAPSE", "animation": "impact"},
             "assets": {"fromLibrary": [], "newAssets": []},
             "emotionalTone": "ominous"},
        ],
    }


def _timing_doc(base, mode, confidences=None):
    doc = copy.deepcopy(base)
    doc["timingMode"] = mode
    doc["audio"] = {
        "file": "/outputs/sample-video/audio/voiceover.mp3",
        "duration": 6.0, "sampleRate": 44100, "timingSource": mode,
        "alignmentTool": ("faster-whisper" if mode in ALIGNMENT_MODES else None),
        "transcriptFile": "/outputs/sample-video/02-script-voiceover.txt",
    }
    if mode not in ALIGNMENT_MODES:
        doc["audio"]["warning"] = "estimated timing — not for voiced final render"
    t = 0.0
    for i, s in enumerate(doc["scenes"]):
        d = s["wordCount"] / 2.5
        s.update({"startTime": round(t, 3), "endTime": round(t + d, 3),
                  "duration": round(d, 3)})
        if confidences is not None:
            s["confidence"] = confidences[i]
        t += d
    return doc


def self_test():
    failures = []

    def check(name, cond):
        print(f"  {'PASS' if cond else 'FAIL'}  {name}")
        if not cond:
            failures.append(name)

    def has(lines, code, fragment=""):
        return any(l.startswith(code) and fragment in l for l in lines)

    derive_vo, _, _ = modules()

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        root = tmp / "repo"
        shutil.copytree(real_root() / "templates", root / "templates")
        (root / "assets" / "library").mkdir(parents=True)

        case_counter = [0]

        def build(narr2="It took three hundred years to break.",
                  used2=("F002",), facts=FACTS, manifest=MANIFEST,
                  packaging=PACKAGING, audit="PASS — matches the promise",
                  timing=None, timing_name="04-scenes-final-estimated.json",
                  drop=(), vo_override=None, scenes_override=None):
            case_counter[0] += 1
            out = root / "outputs" / f"case-{case_counter[0]}" / "sample-video"
            # each case gets its own outputs tree so sync stays deterministic
            out.mkdir(parents=True)
            (root / "assets" / "library" / "manifest.json").write_text(
                json.dumps(manifest), encoding="utf-8")
            used_lines = "\n".join(f"- {u}" for u in used2) or "-"
            annotated = ANNOTATED_TMPL.format(
                narr2=narr2, wc2=len(narr2.split()), used2=used_lines,
                audit=audit)
            scenes = scenes_override or _scenes_doc(narr2, list(used2))
            vo_text = derive_vo.derive(annotated)[0]
            files = {
                "01-research.md": "# Research\n\nStatus notes may mention "
                                  f"{TAG_VERIFY} and {TAG_SINGLE} freely here.\n",
                "01-facts.json": json.dumps(facts),
                "02-script-annotated.md": annotated,
                "02-script-voiceover.txt": vo_override or vo_text,
                "03-scenes.json": json.dumps(scenes),
                timing_name: json.dumps(timing or _timing_doc(
                    scenes, "word-count-estimate")),
                "05-packaging.md": packaging,
            }
            for name, content in files.items():
                if name not in drop and content is not None:
                    (out / name).write_text(content, encoding="utf-8",
                                            newline="\n")
            return out

        def run_gate(out, bootstrap=False, sync_root=None):
            return gate(out, root=(sync_root or out.parents[1].parents[0]),
                        bootstrap=bootstrap)

        # NOTE: gate's sync check scans root/outputs/*/03-scenes.json — our
        # per-case dirs nest one level deeper, so manifest usedInVideos
        # ["sample-video"] vs collected {} would look stale. Point each case's
        # sync at fresh state by keeping manifests consistent instead: accept
        # the SY warning as expected background noise and assert around it.

        base = build()
        fails, warns, info = run_gate(base, sync_root=root)
        base_ok = [f for f in fails]
        check("happy path: no FAILs", base_ok == [])
        check("estimated-only timing -> TC2 WARN", has(warns, "TC2"))
        check("literal tags in 01-research.md do NOT trip FC6",
              not has(fails, "FC6"))
        check("info block populated",
              info["timing_mode"] == "word-count-estimate"
              and "2 fact(s) used" in info["facts"])

        # QG block writing
        block = build_qg_block(fails, warns, info, bootstrap=False)
        check("QG block contains no literal bracket tags",
              TAG_VERIFY not in block and TAG_SINGLE not in block)
        write_qg_block(base / "STATUS.md", block, root)
        status1 = (base / "STATUS.md").read_text(encoding="utf-8")
        check("STATUS.md created from template with markers",
              QG_BEGIN in status1 and "## Video Info" in status1)
        # human edit survives a re-run; block is replaced not duplicated
        (base / "STATUS.md").write_text(
            status1.replace("Video Slug:", "Video Slug: sample-video"),
            encoding="utf-8", newline="\n")
        write_qg_block(base / "STATUS.md", block + "\nEXTRA-LINE", root)
        status2 = (base / "STATUS.md").read_text(encoding="utf-8")
        check("re-run replaces block, keeps human edits",
              status2.count(QG_BEGIN) == 1 and "EXTRA-LINE" in status2
              and "Video Slug: sample-video" in status2)

        # FC6 — literal tag outside research/facts
        out = build(packaging=PACKAGING + f"\nleaked {TAG_VERIFY} tag\n")
        fails, _, _ = run_gate(out, sync_root=root)
        check("literal tag in 05-packaging.md -> FC6 FAIL",
              has(fails, "FC6", "05-packaging.md"))

        # VC — hand-edited VO
        out = build(vo_override="Someone rewrote this by hand.\n")
        fails, _, _ = run_gate(out, sync_root=root)
        check("hand-edited VO -> VC1 FAIL", has(fails, "VC1"))

        # FC3/FC4/FC5 — fact status rules
        facts_bad = copy.deepcopy(FACTS)
        facts_bad["facts"][1].update(status="VERIFY", scriptCritical=False,
                                     isNumber=False)
        fails, _, _ = run_gate(build(facts=facts_bad), sync_root=root)
        check("used VERIFY fact -> FC3 FAIL", has(fails, "FC3", "F002"))
        facts_bad = copy.deepcopy(FACTS)
        facts_bad["facts"][1].update(status="SINGLE-SOURCE", sources=["S001"],
                                     scriptCritical=False, isNumber=True)
        fails, _, _ = run_gate(build(facts=facts_bad), sync_root=root)
        check("used isNumber SINGLE-SOURCE fact -> FC5 FAIL",
              has(fails, "FC5", "F002"))
        facts_bad = copy.deepcopy(FACTS)
        facts_bad["facts"][0]["sources"] = ["S001"]  # VERIFIED needs >= 2
        fails, _, _ = run_gate(build(facts=facts_bad), sync_root=root)
        check("facts schema violation -> FC1 FAIL", has(fails, "FC1"))

        # FC7 — digit heuristic WARN
        out = build(narr2="It took 300 years to break.", used2=())
        fails, warns, _ = run_gate(out, sync_root=root)
        check("digit narration without usedFacts -> FC7 WARN, no FAIL",
              has(warns, "FC7") and not has(fails, "FC7"))

        # TC2 — voiced-final rule
        scenes = _scenes_doc("It took three hundred years to break.", ["F002"])
        out = build(timing=_timing_doc(scenes, "word-count-estimate"),
                    timing_name="04-scenes-final.json")
        fails, _, _ = run_gate(out, sync_root=root)
        check("04-scenes-final.json with estimate mode -> TC2 FAIL",
              has(fails, "TC2"))

        # TC4 — confidence thresholds
        out = build(timing=_timing_doc(scenes, "transcript-guided-alignment",
                                       confidences=[0.95, 0.7]),
                    timing_name="04-scenes-final.json")
        fails, warns, _ = run_gate(out, sync_root=root)
        check("confidence 0.7 -> TC4 WARN not FAIL",
              has(warns, "TC4", "0.7") and not has(fails, "TC4"))
        out = build(timing=_timing_doc(scenes, "transcript-guided-alignment",
                                       confidences=[0.95, 0.5]),
                    timing_name="04-scenes-final.json")
        fails, _, _ = run_gate(out, sync_root=root)
        check("confidence 0.5 -> TC4 FAIL", has(fails, "TC4", "0.5"))

        # TC3 — long/short scene warnings
        long_doc = _timing_doc(scenes, "word-count-estimate")
        long_doc["scenes"][0].update(duration=15.0, endTime=15.0)
        long_doc["scenes"][1].update(startTime=15.0, endTime=16.5, duration=1.5)
        fails, warns, _ = run_gate(build(timing=long_doc), sync_root=root)
        check("LONG + SHORT scene warnings",
              has(warns, "TC3", "LONG SCENE") and has(warns, "TC3", "SHORT SCENE"))

        # PC — packaging checks
        out = build(packaging="# 05A\n\nNo promise section here.\n")
        fails, _, _ = run_gate(out, sync_root=root)
        check("missing Script Hook Promise -> PC1 FAIL", has(fails, "PC1"))
        _, warns, _ = run_gate(
            build(audit="PENDING — packaging not available yet"),
            sync_root=root)
        check("Hook Promise Audit PENDING -> PC2 WARN", has(warns, "PC2"))

        # FP — missing files
        fails, _, _ = run_gate(build(drop=("05-packaging.md",)), sync_root=root)
        check("missing 05-packaging.md -> FP FAIL",
              has(fails, "FP", "05-packaging.md"))

        # DV — scene diversity (mechanical repetition only; the judgmental
        # half of this lives in /templates/VISUAL-QC-CHECKLIST.md, never here)
        dv_doc = {
            "videoSlug": "sample-video", "fps": 30, "resolution": "1920x1080",
            "scenes": [
                {"sceneNumber": 1,
                 "narration": "Rome ruled from Britain to Egypt.",
                 "wordCount": 6, "template": "map-scene",
                 "props": {"region": "roman-empire-max-extent",
                           "camera": "static"},
                 "assets": {"fromLibrary": ["map-roman-empire"],
                            "newAssets": []}},
                {"sceneNumber": 2,
                 "narration": "Its borders stretched for thousands of miles.",
                 "wordCount": 7, "template": "map-scene",
                 "props": {"region": "roman-empire-max-extent",
                           "camera": "slow-pan-left"},
                 "assets": {"fromLibrary": ["map-roman-empire"],
                            "newAssets": []}},
                {"sceneNumber": 3,
                 "narration": "Defending that frontier took an army.",
                 "wordCount": 6, "template": "map-scene",
                 "props": {"region": "roman-empire-max-extent",
                           "camera": "slow-pan-right"},
                 "assets": {"fromLibrary": ["map-roman-empire"],
                            "newAssets": []}},
                {"sceneNumber": 4, "narration": "A THOUSAND-YEAR EMPIRE.",
                 "wordCount": 3, "template": "text-emphasis",
                 "props": {"text": "A THOUSAND-YEAR EMPIRE",
                           "animation": "impact"},
                 "assets": {"fromLibrary": ["map-roman-empire"],
                            "newAssets": []}},
                {"sceneNumber": 5,
                 "narration": "Nine percent of that army guarded the Rhine.",
                 "wordCount": 8, "template": "stat-card",
                 "props": {"value": "9%", "label": "OF LEGIONS ON THE RHINE"},
                 "assets": {"fromLibrary": [], "newAssets": []}},
            ],
        }
        out = build(scenes_override=dv_doc,
                    timing=_timing_doc(dv_doc, "word-count-estimate"))
        fails, warns, info = run_gate(out, sync_root=root)
        check("3x consecutive map-scene -> DV1 WARN",
              has(warns, "DV1", "map-scene"))
        check("map-roman-empire in 4/5 scenes -> DV2 WARN",
              has(warns, "DV2", "map-roman-empire"))
        check("diversity info populated",
              "consecutive-template warnings: 1" in info["diversity"])

    print()
    if failures:
        print(f"SELF-TEST: {len(failures)} FAILURE(S): {failures}")
        return 1
    print("SELF-TEST: ALL CHECKS PASSED")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("target", nargs="?", help="video slug or output folder")
    ap.add_argument("--bootstrap", action="store_true",
                    help="passed through to validate.py (newAssets cap softened)")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        sys.exit(self_test())
    if not args.target:
        ap.error("video slug or output folder required (or use --self-test)")
    try:
        sys.exit(run(args.target, args.bootstrap))
    except SetupError as e:
        print(f"SETUP ERROR: {e}", file=sys.stderr)
        print("No gate verdict (fail closed).", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()

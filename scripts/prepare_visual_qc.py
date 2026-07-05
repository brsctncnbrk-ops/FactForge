#!/usr/bin/env python3
"""prepare_visual_qc.py — build a Layer-2 visual QC review packet (advisory only).

This script does NOT judge anything (P7: deterministic work goes to scripts,
never the LLM — and the inverse holds too: judgment calls never get faked as
mechanical). It only assembles, per scene, the context a human or a review
agent needs to answer the 10 questions in /templates/VISUAL-QC-CHECKLIST.md:
narration, template, props, assets, duration, and the mechanically-derivable
repetition signals (same template as the previous scene? how long a run? how
much does one asset dominate the video?).

The packet is advisory input for a human or an agent run via the Agent/Task
tool (see VISUAL-QC-CHECKLIST.md "run manually (or via a review agent)").
It is NEVER wired into quality-gate.py's pass/fail — that script stays
mechanical-only per CLAUDE.md's judgmental-checks-stay-human rule. Nothing
here blocks a render; it only prepares what a reviewer needs to look at.

Usage:
    python scripts/prepare_visual_qc.py <video-slug | output-dir> [--file 03-scenes.json]
    python scripts/prepare_visual_qc.py --self-test

Exit codes: 0 packet written, 2 cannot run (fail closed).
"""

import argparse
import json
import sys
import tempfile
from pathlib import Path

DEFAULT_SCENES_FILE = "03-scenes.json"
CHECKLIST_QUESTIONS = [
    "Does this scene visualize the specific claim being narrated right now?",
    "Does the scene carry meaning on its own, without the narration?",
    "Is the composition clean and readable?",
    "Is all on-screen text readable at a glance against its background?",
    "Is this scene visually distinct from the immediately preceding one?",
    "Is there at least one visible motion/change event during the scene?",
    "Does the scene match /templates/STYLE-GUIDE.md?",
    "Does the scene look amateur, empty, or like a generic stock/placeholder image?",
    "Is any single asset reused so often it starts to feel repetitive?",
    "Is there a real risk this scene bores the viewer?",
]


class SetupError(Exception):
    """Broken environment — no packet possible (exit 2)."""


def find_repo_root(start):
    for p in [start] + list(start.parents):
        if (p / "templates" / "VISUAL-QC-CHECKLIST.md").is_file():
            return p
    raise SetupError(f"repo root not found above {start}")


def resolve_out_dir(target, root):
    target_path = Path(target)
    if target_path.is_dir():
        return target_path
    candidate = root / "outputs" / target
    if candidate.is_dir():
        return candidate
    raise SetupError(f"no such output directory: {target}")


def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as e:
        raise SetupError(f"cannot read {path}: {e}")
    except json.JSONDecodeError as e:
        raise SetupError(f"{path} is not valid JSON: {e}")


def build_packet(scenes_doc):
    scenes = sorted(
        (s for s in scenes_doc.get("scenes") or [] if isinstance(s, dict)),
        key=lambda s: s.get("sceneNumber", 0),
    )
    total = len(scenes)
    asset_counts = {}
    for s in scenes:
        for a in (s.get("assets") or {}).get("fromLibrary") or []:
            if isinstance(a, str):
                asset_counts[a] = asset_counts.get(a, 0) + 1

    packet_scenes = []
    prev_template = None
    run_len = 0
    for s in scenes:
        template = s.get("template")
        run_len = run_len + 1 if template is not None and template == prev_template else 1
        fromLibrary = (s.get("assets") or {}).get("fromLibrary") or []
        packet_scenes.append({
            "sceneNumber": s.get("sceneNumber"),
            "template": template,
            "narration": s.get("narration"),
            "props": s.get("props"),
            "assetsUsed": fromLibrary,
            "duration": s.get("duration", s.get("estimatedDuration")),
            "precedingTemplate": prev_template,
            "sameTemplateAsPrevious": template is not None and template == prev_template,
            "consecutiveRunLength": run_len,
            "assetShareInVideo": {
                a: round(asset_counts[a] / total, 3) for a in fromLibrary
            } if total else {},
        })
        prev_template = template

    return {
        "videoSlug": scenes_doc.get("videoSlug"),
        "sceneCount": total,
        "instructions": (
            "Advisory Layer-2 visual QC packet. For EACH scene below, answer "
            "the checklistQuestions using the narration/template/props/assets "
            "context plus /templates/STYLE-GUIDE.md. This is a human or "
            "review-agent judgment pass — never a mechanical pass/fail. Flag "
            "any scene that fails a question for re-templating or a props "
            "rework; do not rewrite quality-gate.py to enforce this."
        ),
        "styleGuideRef": "/templates/STYLE-GUIDE.md",
        "checklistRef": "/templates/VISUAL-QC-CHECKLIST.md",
        "checklistQuestions": CHECKLIST_QUESTIONS,
        "scenes": packet_scenes,
    }


def run(target, file_name):
    root = find_repo_root(Path.cwd())
    out_dir = resolve_out_dir(target, root)
    scenes_path = out_dir / file_name
    if not scenes_path.is_file():
        raise SetupError(f"no such file: {scenes_path}")
    scenes_doc = load_json(scenes_path)
    packet = build_packet(scenes_doc)
    packet_path = out_dir / "visual-qc-packet.json"
    packet_path.write_text(
        json.dumps(packet, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n",
    )
    return packet_path, packet


def self_test():
    failures = []

    def check(name, cond):
        print(f"  {'PASS' if cond else 'FAIL'}  {name}")
        if not cond:
            failures.append(name)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        root = tmp / "repo"
        (root / "templates").mkdir(parents=True)
        (root / "templates" / "VISUAL-QC-CHECKLIST.md").write_text("x", encoding="utf-8")
        out_dir = root / "outputs" / "sample-video"
        out_dir.mkdir(parents=True)

        doc = {
            "videoSlug": "sample-video",
            "scenes": [
                {"sceneNumber": 1, "template": "map-scene", "narration": "A",
                 "props": {"region": "x", "camera": "static"},
                 "assets": {"fromLibrary": ["map-x"], "newAssets": []},
                 "duration": 5.0},
                {"sceneNumber": 2, "template": "map-scene", "narration": "B",
                 "props": {"region": "x", "camera": "static"},
                 "assets": {"fromLibrary": ["map-x"], "newAssets": []},
                 "duration": 5.0},
                {"sceneNumber": 3, "template": "stat-card", "narration": "C",
                 "props": {"value": "1", "label": "L"},
                 "assets": {"fromLibrary": [], "newAssets": []},
                 "duration": 5.0},
            ],
        }
        (out_dir / DEFAULT_SCENES_FILE).write_text(json.dumps(doc), encoding="utf-8")

        packet_path, packet = run(str(out_dir), DEFAULT_SCENES_FILE)
        check("packet file written", packet_path.is_file())
        check("sceneCount matches", packet["sceneCount"] == 3)
        check("10 checklist questions present", len(packet["checklistQuestions"]) == 10)
        s1, s2, s3 = packet["scenes"]
        check("scene 1 has no preceding template", s1["precedingTemplate"] is None)
        check("scene 2 flagged as same template as previous",
              s2["sameTemplateAsPrevious"] is True and s2["consecutiveRunLength"] == 2)
        check("scene 3 breaks the run",
              s3["sameTemplateAsPrevious"] is False and s3["consecutiveRunLength"] == 1)
        check("map-x asset share computed for scenes 1 and 2",
              s1["assetShareInVideo"].get("map-x") == round(2 / 3, 3)
              and s2["assetShareInVideo"].get("map-x") == round(2 / 3, 3))
        check("scene 3 has no assets, empty share map", s3["assetShareInVideo"] == {})
        check("narration/props/duration carried through verbatim",
              s1["narration"] == "A" and s1["props"]["region"] == "x" and s1["duration"] == 5.0)

        # missing scenes file -> SetupError
        try:
            run(str(out_dir), "no-such-file.json")
            check("missing scenes file -> SetupError", False)
        except SetupError:
            check("missing scenes file -> SetupError", True)

    print()
    if failures:
        print(f"SELF-TEST: {len(failures)} FAILURE(S): {failures}")
        return 1
    print("SELF-TEST: ALL CHECKS PASSED")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?", help="video slug or output directory")
    ap.add_argument("--file", default=DEFAULT_SCENES_FILE,
                    help="scenes file to read (default: 03-scenes.json)")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        sys.exit(self_test())

    if not args.target:
        ap.error("target (video slug or output dir) is required unless --self-test")

    try:
        packet_path, packet = run(args.target, args.file)
    except SetupError as e:
        print(f"SETUP ERROR: {e}")
        sys.exit(2)

    print(f"Wrote {packet_path}")
    print(f"{packet['sceneCount']} scene(s) packaged for review.")
    repeats = [s for s in packet["scenes"] if s["consecutiveRunLength"] >= 3]
    if repeats:
        print("NOTE: consecutive-template runs of 3+ (quality-gate.py already "
              "WARNs on these too): " +
              ", ".join(str(s["sceneNumber"]) for s in repeats))
    print("This packet is advisory input for a human or review agent — see "
          "/templates/VISUAL-QC-CHECKLIST.md. It does not block anything.")
    sys.exit(0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""check_visual_qc_report.py — Layer 1.5: enforce that a Layer-2 visual QC
judgment pass exists and came back clean (advisory judgment, mechanical
enforcement).

This script does NOT judge whether a scene looks good — that call is made by
a human or a review agent per /templates/VISUAL-QC-CHECKLIST.md, and written
to outputs/{slug}/visual-qc-report.md in the required format (one
"## Scene {N} — {template}" section per scene, body starting with a bolded
PASS./FLAG. verdict). This script only parses that report and enforces the
result — the same separation quality-gate.py keeps between "is this valid"
(mechanical) and "does this look good" (judgmental), applied one layer
later: here the judgment already happened upstream, deterministically or
not is irrelevant, and this script just refuses to call a video clear
without one on record.

Never merged into quality-gate.py (P8: single responsibility per script);
never invents a verdict — a missing/malformed report is a hard fail-closed
SetupError, not a silent pass.

Usage:
    python scripts/check_visual_qc_report.py <video-slug | output-dir>
    python scripts/check_visual_qc_report.py --self-test

Exit codes: 0 all scenes PASS, 1 one or more scenes FLAG, 2 cannot check
(report missing/malformed, scene count mismatch — fail closed).
"""

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

REPORT_NAME = "visual-qc-report.md"
PACKET_NAME = "visual-qc-packet.json"

SCENE_HEADER_RE = re.compile(r"^##\s+Scene\s+(\d+)\b.*$", re.MULTILINE)
VERDICT_RE = re.compile(r"\*\*\s*(PASS|FLAG)\s*\.?\s*\*\*", re.IGNORECASE)


class SetupError(Exception):
    """Broken environment or malformed report — no verdict possible (exit 2)."""


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


def parse_report(text):
    """Return {sceneNumber: "PASS"|"FLAG"} in document order."""
    headers = list(SCENE_HEADER_RE.finditer(text))
    if not headers:
        raise SetupError("report has no '## Scene N' sections")
    verdicts = {}
    for i, m in enumerate(headers):
        scene_num = int(m.group(1))
        body_start = m.end()
        body_end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
        body = text[body_start:body_end]
        vm = VERDICT_RE.search(body)
        if not vm:
            raise SetupError(
                f"scene {scene_num}: no bolded PASS./FLAG. verdict found "
                "in its section body")
        if scene_num in verdicts:
            raise SetupError(f"duplicate '## Scene {scene_num}' section")
        verdicts[scene_num] = vm.group(1).upper()
    return verdicts


def run(target):
    root = find_repo_root(Path.cwd())
    out_dir = resolve_out_dir(target, root)

    report_path = out_dir / REPORT_NAME
    if not report_path.is_file():
        raise SetupError(
            f"no {REPORT_NAME} in {out_dir} — run prepare_visual_qc.py, "
            "then a Layer-2 judgment pass, before checking")
    try:
        report_text = report_path.read_text(encoding="utf-8")
    except OSError as e:
        raise SetupError(f"cannot read {report_path}: {e}")
    verdicts = parse_report(report_text)

    packet_path = out_dir / PACKET_NAME
    if packet_path.is_file():
        try:
            packet = json.loads(packet_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            raise SetupError(f"cannot read {packet_path}: {e}")
        expected = {s.get("sceneNumber") for s in packet.get("scenes") or []}
        got = set(verdicts.keys())
        if expected != got:
            missing = sorted(expected - got)
            extra = sorted(got - expected)
            raise SetupError(
                f"report scene numbers {sorted(got)} don't match packet "
                f"scene numbers {sorted(expected)} (missing: {missing}, "
                f"extra: {extra}) — regenerate the report against the "
                "current packet")

    flagged = sorted(n for n, v in verdicts.items() if v == "FLAG")
    return verdicts, flagged


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

        packet = {"scenes": [{"sceneNumber": 1}, {"sceneNumber": 2}, {"sceneNumber": 3}]}
        (out_dir / PACKET_NAME).write_text(json.dumps(packet), encoding="utf-8")

        # all-clean report
        (out_dir / REPORT_NAME).write_text(
            "## Scene 1 — map-scene\n\n**PASS.** fine\n\n"
            "## Scene 2 — stat-card\n\n**PASS.** fine\n\n"
            "## Scene 3 — text-emphasis\n\n**PASS.** fine\n",
            encoding="utf-8")
        verdicts, flagged = run(str(out_dir))
        check("all-PASS report -> no flagged scenes", flagged == [])
        check("3 verdicts parsed", verdicts == {1: "PASS", 2: "PASS", 3: "PASS"})

        # one flagged scene
        (out_dir / REPORT_NAME).write_text(
            "## Scene 1 — map-scene\n\n**PASS.** fine\n\n"
            "## Scene 2 — stat-card\n\n**FLAG.** too static\n\n"
            "## Scene 3 — text-emphasis\n\n**PASS.** fine\n",
            encoding="utf-8")
        verdicts, flagged = run(str(out_dir))
        check("one FLAG -> flagged list has scene 2", flagged == [2])

        # missing report -> SetupError
        (out_dir / REPORT_NAME).unlink()
        try:
            run(str(out_dir))
            check("missing report -> SetupError", False)
        except SetupError:
            check("missing report -> SetupError", True)

        # malformed report (no verdict in a section) -> SetupError
        (out_dir / REPORT_NAME).write_text(
            "## Scene 1 — map-scene\n\nsome text with no verdict\n",
            encoding="utf-8")
        try:
            run(str(out_dir))
            check("scene with no verdict -> SetupError", False)
        except SetupError:
            check("scene with no verdict -> SetupError", True)

        # scene-count mismatch vs packet -> SetupError
        (out_dir / REPORT_NAME).write_text(
            "## Scene 1 — map-scene\n\n**PASS.** fine\n",
            encoding="utf-8")
        try:
            run(str(out_dir))
            check("report/packet scene-count mismatch -> SetupError", False)
        except SetupError:
            check("report/packet scene-count mismatch -> SetupError", True)

    print()
    if failures:
        print(f"SELF-TEST: {len(failures)} FAILURE(S): {failures}")
        return 1
    print("SELF-TEST: ALL CHECKS PASSED")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?", help="video slug or output directory")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        sys.exit(self_test())

    if not args.target:
        ap.error("target (video slug or output dir) is required unless --self-test")

    try:
        verdicts, flagged = run(args.target)
    except SetupError as e:
        print(f"SETUP ERROR: {e}")
        sys.exit(2)

    print(f"{len(verdicts)} scene(s) checked against visual-qc-report.md.")
    if flagged:
        print(f"VISUAL QC: FAIL — {len(flagged)} scene(s) flagged: {flagged}")
        print("Re-template/rework these scenes, then regenerate the packet "
              "and re-run the Layer-2 judgment pass before this can pass.")
        sys.exit(1)
    print("VISUAL QC: PASS — every scene cleared its Layer-2 review.")
    sys.exit(0)


if __name__ == "__main__":
    main()

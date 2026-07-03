#!/usr/bin/env python3
"""derive_vo.py — derive 02-script-voiceover.txt from 02-script-annotated.md (P4/P7).

Parse contract (patch Section 14, character-for-character):
- Scene delimiter: a line matching  ^## Scene (\\d+)\\s*$
- Field labels (exact, at line start): "Word Count:", "Estimated Duration:",
  "Narration:", "Used Facts:", "Visual Intent:", "On-screen Text:",
  "Emotional Tone:". Only these labels terminate a Narration block.
- Narration = lines between "Narration:" and the next label/scene/EOF,
  stripped and joined with single spaces (one paragraph per scene).

Output: paragraphs in ascending scene order, exactly one blank line between
paragraphs, UTF-8, LF endings, single trailing newline. Deterministic:
same input -> byte-identical output (quality-gate.py re-derives and diffs).

Fails closed (exit 2, no output written): no scenes found, a scene without
narration, duplicate scene numbers.
Warns (exit 0): declared vs computed Word Count mismatch, narration over
30 words, non-sequential scene numbers.

Content policing (e.g. literal [VERIFY] tags) is NOT this script's job;
quality-gate.py is the single enforcement point.

Usage:
    python derive_vo.py <02-script-annotated.md> [-o OUTPUT]
    python derive_vo.py --self-test
"""

import argparse
import re
import sys
from pathlib import Path

SCENE_RE = re.compile(r"^## Scene (\d+)\s*$")
FIELD_LABELS = (
    "Word Count:",
    "Estimated Duration:",
    "Narration:",
    "Used Facts:",
    "Visual Intent:",
    "On-screen Text:",
    "Emotional Tone:",
)
HARD_CAP_WORDS = 30


class ParseError(Exception):
    """Contract violation in the annotated script (fail closed)."""


def parse_scenes(text):
    """Parse annotated-script text into a list of scene dicts."""
    scenes = []
    current = None
    mode = None
    for raw in text.splitlines():
        m = SCENE_RE.match(raw)
        if m:
            current = {"number": int(m.group(1)), "narration": [], "declared_wc": None}
            scenes.append(current)
            mode = None
            continue
        if current is None:
            continue
        label = next((lb for lb in FIELD_LABELS if raw.startswith(lb)), None)
        if label is not None:
            mode = label
            inline = raw[len(label):].strip()
            if inline:
                if label == "Narration:":
                    current["narration"].append(inline)
                elif label == "Word Count:":
                    current["declared_wc"] = inline
            continue
        stripped = raw.strip()
        if not stripped:
            continue
        if mode == "Narration:":
            current["narration"].append(stripped)
        elif mode == "Word Count:" and current["declared_wc"] is None:
            current["declared_wc"] = stripped
    return scenes


def derive(text):
    """Return (vo_text, report_lines, warnings). Raises ParseError on violations."""
    scenes = parse_scenes(text)
    if not scenes:
        raise ParseError("no '## Scene N' headers found — nothing to derive")

    numbers = [s["number"] for s in scenes]
    dupes = sorted({n for n in numbers if numbers.count(n) > 1})
    if dupes:
        raise ParseError("duplicate scene numbers: " + ", ".join(str(n) for n in dupes))

    missing = [s["number"] for s in scenes if not s["narration"]]
    if missing:
        raise ParseError(
            "scene(s) without Narration: " + ", ".join(str(n) for n in missing)
        )

    warnings = []
    if numbers != sorted(numbers) or numbers != list(range(numbers[0], numbers[0] + len(numbers))):
        warnings.append(f"scene numbers are non-sequential: {numbers}")

    ordered = sorted(scenes, key=lambda s: s["number"])
    paragraphs = []
    report_lines = []
    total = 0
    for s in ordered:
        paragraph = " ".join(s["narration"])
        paragraphs.append(paragraph)
        wc = len(paragraph.split())
        total += wc
        report_lines.append(f"Scene {s['number']}: {wc} words")
        if wc > HARD_CAP_WORDS:
            warnings.append(
                f"Scene {s['number']}: {wc} words exceeds the {HARD_CAP_WORDS}-word hard cap — split the scene"
            )
        declared = s["declared_wc"]
        if declared is None:
            warnings.append(f"Scene {s['number']}: no declared Word Count")
        else:
            try:
                if int(declared) != wc:
                    warnings.append(
                        f"Scene {s['number']}: declared Word Count {declared} != computed {wc}"
                    )
            except ValueError:
                warnings.append(
                    f"Scene {s['number']}: declared Word Count {declared!r} is not a number"
                )
    report_lines.append(f"TOTAL: {total} words across {len(ordered)} scenes")
    vo_text = "\n\n".join(paragraphs) + "\n"
    return vo_text, report_lines, warnings


def run(input_path, output_path):
    text = Path(input_path).read_text(encoding="utf-8")
    try:
        vo_text, report_lines, warnings = derive(text)
    except ParseError as e:
        print(f"PARSE ERROR: {e}", file=sys.stderr)
        print("No output written (fail closed).", file=sys.stderr)
        return 2
    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(vo_text)
    print(f"Wrote {output_path}")
    for line in report_lines:
        print(line)
    for w in warnings:
        print(f"WARNING: {w}")
    return 0


# --- self-test -------------------------------------------------------------

SAMPLE = """# Annotated Video Script — Sample

Target Length: 7 minutes | Target Words: ~1,000-1,100 | Speaking Rate: 150 wpm

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
Mysterious, serious, dramatic.

## Scene 2

Word Count: 12
Estimated Duration: ~5 seconds

Narration:
For three hundred years, something inside the empire
had been quietly breaking.

Used Facts:
- F004

Visual Intent:
Timeline hinting at a long decline before the final fall.

On-screen Text:
A 300-YEAR COLLAPSE

Emotional Tone:
Ominous, intriguing.

## Hook Promise Audit

Hook Match:
PENDING — packaging not available yet

Reason:
Sample audit footer; must not leak into the VO output.
"""

EXPECTED = (
    "Rome did not fall in a single night.\n"
    "\n"
    "For three hundred years, something inside the empire had been quietly breaking.\n"
)


def self_test():
    failures = []

    def check(name, cond):
        print(f"  {'PASS' if cond else 'FAIL'}  {name}")
        if not cond:
            failures.append(name)

    vo_text, report_lines, warnings = derive(SAMPLE)
    check("sample derives to expected VO output (byte-exact)", vo_text == EXPECTED)
    check("multi-line narration joined with single spaces",
          "empire had been quietly breaking" in vo_text)
    check("audit footer / headers / labels not leaked",
          "Hook Promise Audit" not in vo_text and "Scene" not in vo_text
          and "Visual Intent" not in vo_text)
    check("per-scene word counts reported",
          report_lines[0] == "Scene 1: 8 words" and report_lines[1] == "Scene 2: 12 words")
    check("total reported", report_lines[-1] == "TOTAL: 20 words across 2 scenes")
    check("no warnings on clean sample", warnings == [])
    check("deterministic (second run byte-identical)", derive(SAMPLE)[0] == vo_text)

    mismatch = SAMPLE.replace("Word Count: 12", "Word Count: 11", 1)
    _, _, w = derive(mismatch)
    check("declared/computed mismatch warns",
          any("declared Word Count 11 != computed 12" in x for x in w))

    over = SAMPLE.replace(
        "For three hundred years, something inside the empire",
        "word " * 30 + "For three hundred years, something inside the empire", 1)
    _, _, w = derive(over)
    check("hard cap (>30 words) warns", any("hard cap" in x for x in w))

    def raises(bad_text):
        try:
            derive(bad_text)
            return False
        except ParseError:
            return True

    check("no scenes -> ParseError", raises("just some text\nwith no scenes\n"))
    check("missing narration -> ParseError",
          raises("## Scene 1\n\nWord Count: 5\n\nVisual Intent:\nSomething.\n"))
    check("duplicate scene numbers -> ParseError",
          raises(SAMPLE.replace("## Scene 2", "## Scene 1", 1)))

    gap = SAMPLE.replace("## Scene 2", "## Scene 5", 1)
    _, _, w = derive(gap)
    check("non-sequential numbers warn", any("non-sequential" in x for x in w))

    print()
    if failures:
        print(f"SELF-TEST: {len(failures)} FAILURE(S): {failures}")
        return 1
    print("SELF-TEST: ALL CHECKS PASSED")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("input", nargs="?", help="path to 02-script-annotated.md")
    ap.add_argument("-o", "--output",
                    help="output path (default: sibling 02-script-voiceover.txt)")
    ap.add_argument("--self-test", action="store_true",
                    help="run the embedded self-test and exit")
    args = ap.parse_args()

    if args.self_test:
        sys.exit(self_test())
    if not args.input:
        ap.error("input file required (or use --self-test)")
    output = args.output or str(Path(args.input).parent / "02-script-voiceover.txt")
    sys.exit(run(args.input, output))


if __name__ == "__main__":
    main()

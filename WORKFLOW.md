WORKFLOW — Faz Yürütme Rehberi
Bu dosya insan içindir. Her fazda buradaki hazır promptu kopyala, Claude Code'a yapıştır. Kurallar CLAUDE.md'dedir ve her oturumda otomatik okunur; ana kural promptunu tekrar yapıştırma.
Oturum Ritmi (her faz)

1. Fazın promptunu aşağıdan kopyala, yapıştır.
2. (1A–1D) Gelen DESIGN SUMMARY'yi aşağıdaki "Sen neyi kontrol et" listesine göre incele.
3. "ONAY" yaz (gerekirse: "şu değişikliklerle ONAY: ..."). ONAY kelimesi geçmeyen mesaj = özet revizyonu, dosya yazılmaz.
4. Faz bitince: `git add -A && git commit -m "phase-1x complete"` + `/usage` değerini TASKS.md Quota Notes'a işle.
Yarıda Kalma / Devam
Pencere biterse: "stop now" de → Claude Code durumu TASKS.md'ye yazar. Yeni pencerede şunu yapıştır:
text

```text
Continue the current phase from TASKS.md. Do not re-read the whole project.
If TASKS.md says "Design approved: yes", continue implementation without
presenting a new design summary.
```

Phase 1A Prompt
text

```text
Implement Phase 1A only (Repository Skeleton + Global Contracts).

BEFORE writing any files:
1. Read TASKS.md, then ONLY the sections of PROJECT-BRIEF-v2.1.md and
   STABILIZATION-PATCH-v2.1.1.md relevant to Phase 1A (file structure,
   template catalog, patch Sections 3, 5, 7, 9, 20).
2. Present a compact DESIGN SUMMARY covering:
   - For each of the 12 templates: required props, optional props,
     allowed values.
   - How 9:16 variants are represented (recommendation: a single
     aspectRatio prop, NOT duplicated schemas — state your choice).
   - facts-file.schema.json field list.
   - timingMode enum values (must be exactly the four in patch Section 7).
   - Confirmation that every field in the brief's example scenes JSON
     maps to scenes-file.schema.json (including optional usedFacts).
3. STOP and wait for "ONAY".

AFTER approval, tasks:
1. Create the full folder structure (brief file structure + patch
   Section 20 deltas). Both root documents already exist — verify, do not
   recreate.
2. /templates/template-catalog.md (12 templates: name, purpose, props
   table, example props, asset needs, 9:16 variant note).
3. /templates/TEMPLATE-GAPS.md (empty).
4. /templates/schemas/scenes-file.schema.json (optional usedFacts array
   on scenes; timingMode enum; audio metadata block).
5. Schema files for all 12 templates.
6. /templates/schemas/facts-file.schema.json.
7. /assets/library/manifest.json skeleton (extended fields incl. license,
   attributionRequired, status, reusable, usedInVideos, updatedAt).
8. /assets/library/LICENSES.md.
9. /outputs/.gitkeep.
10. Do not create any skill files. Do not implement /render.

AFTER completion: validate all JSON/schema files parse correctly, update
TASKS.md, list files created, list blockers, stop.
```

Sen neyi kontrol et (1A): Şemalarda kaçan hata her alt katmana yayılır — Phase 1'in en kritik onayı budur. Brief'teki örnek scenes JSON'ın her alanı şemada karşılık buluyor mu? 12 şablonun props'ları mantıklı ve yeterince kısıtlı mı (allowed values)? timingMode tam dört değer mi? 9:16 çözümü şema sayısını ikiye katlıyor mu (katlamamalı)?
Phase 1B Prompt
text

```text
Implement Phase 1B only (Research + Script Foundation).

BEFORE writing any files:
1. Read TASKS.md, then ONLY brief sections 01/02-skill and patch
   Sections 3, 5, 6, 13, 14.
2. Present a compact DESIGN SUMMARY covering:
   - Frontmatter descriptions (trigger text) for both SKILL.md files.
   - Fact/source ID assignment rules and how 01-facts.json is produced.
   - derive_vo.py parse contract: the EXACT markdown pattern it reads
     from 02-script-annotated.md (must match patch Section 14 scene
     format character-for-character), and its failure behavior.
   - How search budget (15) and NotebookLM [S1]->S001 mapping are handled.
3. STOP and wait for "ONAY".

AFTER approval, tasks:
1. Create 01-research-skill (SKILL.md + /references: output format,
   research modes, notebooklm-workflow.md).
2. Create 02-script-skill (SKILL.md + /references: output format,
   hook-promise-check.md, word-budget-rules.md).
3. Create 02-script-skill/scripts/derive_vo.py with a small self-test
   (sample annotated snippet -> expected VO output).
4. Do not create example video output yet. Do not implement /render.

AFTER completion: run the derive_vo.py self-test, update TASKS.md,
list files created, list blockers, stop.
```

Sen neyi kontrol et (1B): derive_vo.py parse sözleşmesi ile patch Bölüm 14 sahne formatı harfiyen eşleşiyor mu? (Kırılganlığın merkezi burası — eşleşmezse gate sürekli FAIL verir.) Description'lar tetikleme için yeterince iddialı mı?
Phase 1C Prompt
text

```text
Implement Phase 1C only (Visual Scene System).

BEFORE writing any files:
1. Read TASKS.md, then ONLY brief section 03-skill and patch
   Sections 8, 9, 11 (Scene + Asset checks), 15.
2. Present a compact DESIGN SUMMARY covering:
   - validate.py check list, mapped 1:1 to patch Section 11
     Scene Checks + Asset Checks.
   - How usedFacts IDs are validated against 01-facts.json.
   - Bootstrap flag name and behavior (--bootstrap).
   - TEMPLATE-GAPS.md log entry format.
3. STOP and wait for "ONAY".

AFTER approval, tasks:
1. Create 03-visual-scene-skill (SKILL.md + /references; no schema
   copies inside the skill folder — reference /templates by path).
2. Create 03-visual-scene-skill/scripts/validate.py with a small
   self-test (a minimal valid and an invalid scenes JSON).
3. Do not implement /render.

AFTER completion: run the validate.py self-test, update TASKS.md,
list files created, list blockers, stop.
```

Sen neyi kontrol et (1C): validate.py listesi patch Bölüm 11 ile birebir mi, eksik/fazla kontrol var mı? Bootstrap bayrağı yokken kural sertleşiyor mu?
Phase 1D Prompt
text

```text
Implement Phase 1D only (Timing + Packaging + Quality Gate).

BEFORE writing any files:
1. Read TASKS.md, then ONLY brief sections 04/05-skill, quality gate,
   STATUS.md format, and patch Sections 4, 7, 10, 11, 12.
2. Present a compact DESIGN SUMMARY covering:
   - align.py tool choice + model size (expected: faster-whisper,
     tiny/base) and why it fits 4GB RAM.
   - Concrete confidence threshold value and how it is computed.
   - Fuzzy matching approach (rapidfuzz preferred, difflib acceptable;
     no torch-dependent tools).
   - 05A/05B file layout decision (one 05-packaging.md with two parts,
     or two files — state your choice).
   - quality-gate.py checks mapped 1:1 to patch Section 11, with explicit
     confirmation that NO judgmental checks (title/thumbnail claims) are
     included.
   - STATUS.md QG block markers and exactly which sections the script
     writes vs. the human writes.
3. STOP and wait for "ONAY".

AFTER approval, tasks:
1. Create 04-timing-sync-skill (SKILL.md + /references) + scripts/align.py
   (transcript-guided alignment + proportional-estimate + word-count-estimate
   fallbacks, audio metadata, sanity checks).
2. Create 05-packaging-skill (SKILL.md + /references) with the 05A/05B split.
3. Create /scripts/quality-gate.py (all patch Section 11 checks).
4. Create /scripts/sync_manifest_usage.py.
5. Create the standard STATUS.md template (with QG markers, Session Notes,
   Quota Notes) as a reusable template file.
6. Do not implement /render.

AFTER completion: run quality-gate.py and sync_manifest_usage.py in
dry/self-test mode, update TASKS.md, list files created, list blockers, stop.
```

Sen neyi kontrol et (1D): En çok tasarım kararı burada. Araç seçimi ve eşik değeri somut mu (belirsiz "uygun bir eşik" kabul etme)? Gate'e yargısal kontrol sızmış mı? QG bloğu elle yazılan bölümlere dokunuyor mu (dokunmamalı)?
Phase 1E Prompt
text

```text
Implement Phase 1E only (Example Topic Output). No design checkpoint —
this is production. Follow all skills and CLAUDE.md rules.

Topic: Why the Roman Empire Really Collapsed
Target Language: English | Target Length: 7 minutes
Style: The Infographics Show + cinematic documentary + simple infographic
animation

Produce under /outputs/why-the-roman-empire-really-collapsed/:
01-research.md, 01-facts.json, 02-script-annotated.md,
02-script-voiceover.txt (via derive_vo.py), 03-scenes.json (validate.py
must pass), 04-scenes-final-estimated.json (word-count-estimate mode ONLY —
no real audio exists), 05-packaging.md (05A only), STATUS.md.

Rules:
- No voiced final render. Do not implement /render.
- Run quality-gate.py at the end and report results (estimated timing
  warnings are expected and acceptable at this stage).
- Update TASKS.md and stop.
```

Sen neyi kontrol et (1E): Kodu değil ÜRÜNÜ değerlendir: research fact kalitesi ve kaynak güvenilirliği, hook'un gücü, sahnelerin şablonlara doğal oturup oturmadığı, TEMPLATE-GAPS'e düşen kayıtlar. Sürtünme noktaları sonraki oturumda hedefli düzeltme olur. 1E onayından sonra Faz 2 (/render) kararı sana aittir.

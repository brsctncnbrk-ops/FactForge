# YouTube Production Skill System v2.1.1 — Stabilized Implementation Plan

Bu doküman, `PROJECT-BRIEF-v2.1.md`'yi tamamlayan ve düzelten **bağlayıcı** patch'tir. Repoda brief'in yanına konur; Claude Code her fazda ikisini birlikte takip eder.

## Öncelik Sırası (çelişki durumunda)

```text
1. Mimari Prensipler P1–P8 (brief'teki hali — bu patch onları değiştirmez, uygular)
2. Bu patch (v2.1.1)
3. PROJECT-BRIEF-v2.1.md'nin diğer bölümleri
4. Skill SKILL.md dosyaları
```

## v2.1 → v2.1.1 Değişiklik Özeti

```text
- 5 Core Skills + Render Layer ayrımı netleşti (06-Render skill DEĞİLDİR, Faz 2'dir)
- Phase 1, beş alt faza bölündü (1A–1E); faz sonunda dur-ve-bekle kuralı
- 05-packaging ikiye ayrıldı: 05A Packaging Core + 05B Publishing Finalization
- Fact tracking eklendi: 01-facts.json (makine kaynağı, şemalı) + Used Facts alanı
- VERIFY / SINGLE-SOURCE kullanım kuralı TEK kanonik tabloda toplandı (Bölüm 6)
- Timing terminolojisi gerçekçileşti: transcript-guided alignment + fuzzy matching
- Asset bootstrap istisnası eklendi (ilk 1–3 video için ≤5 kuralı esner)
- Manifest'e ek alanlar; usedInVideos ELLE DEĞİL script ile güncellenir
- STATUS.md doğrulama bölümleri quality-gate.py tarafından OTOMATİK yazılır
- Title/thumbnail iddia kontrolü mekanik gate'ten çıkarıldı, insan checklist'ine taşındı
- Şema değişiklikleri Phase 1A görevlerine açıkça eklendi (usedFacts, timingMode enum,
  facts-file.schema.json)
```

---

# 1. Sistem Adı ve Katman Netleştirme

```text
System name:
YouTube Production Skill System v2.1.1 — 5 Core Skills + Render Layer

Bu projede 5 çekirdek üretim skill'i vardır:

01-research-skill
02-script-skill
03-visual-scene-skill
04-timing-sync-skill
05-packaging-skill

06-Render bir skill DEĞİLDİR.
06-Render, Faz 2'ye ait ayrı bir Remotion + GitHub Actions render katmanıdır.
Kullanıcı açıkça Faz 2'yi istemedikçe Phase 1 sırasında implement edilemez.
```

---

# 2. Claude Code Uygulama Kuralı

Claude Code tüm sistemi tek seferde kurmaya çalışmamalıdır. Proje küçük, doğrulanabilir fazlarla ilerler.

```text
Implementation Rule:
Do not implement the whole system in one pass.
Work only on the phase the user explicitly requests.

After each phase:
1. list created files,
2. list modified files,
3. run available validation scripts and report results,
4. update STATUS.md / progress notes,
5. list remaining blockers,
6. stop and wait for the next instruction.

Never silently skip files.
Never create placeholder logic without marking it clearly as TODO.
Never implement Phase 2 render unless explicitly requested.
```

---

# 3. Phase 1 Alt Fazları

```text
Phase 1A — Repository Skeleton + Global Contracts

Goals:
- Tam klasör yapısını oluştur.
- PROJECT-BRIEF-v2.1.md ve bu patch'i repoya koy.
- /templates/template-catalog.md (12 şablon).
- /templates/TEMPLATE-GAPS.md (boş).
- /templates/schemas/scenes-file.schema.json:
  * scene objesine OPSIYONEL "usedFacts" alanı (fact ID dizisi) DAHİL
  * üst seviye "timingMode" enum'u ŞU DÖRT değerle:
    "forced-alignment" | "transcript-guided-alignment" |
    "proportional-estimate" | "word-count-estimate"
- 12 şablonun her biri için props şeması (map-scene ... transition-break).
- /templates/schemas/facts-file.schema.json (01-facts.json'ın şeması — Bölüm 5).
- /assets/library/manifest.json iskeleti (Bölüm 9'daki alanlarla).
- /assets/library/LICENSES.md.

Stop after Phase 1A.

Phase 1B — Research + Script Foundation

Goals:
- 01-research-skill (SKILL.md + references).
- 01-facts.json üretim kuralları (sourceId/factId, status, scriptCritical, isNumber).
- 02-script-skill (SKILL.md + references).
- derive_vo.py.
- Used Facts sahne alanı + Hook Promise Audit formatı.
- NotebookLM akışı kullanılırsa [S1] → S001 ID eşlemesi kuralı
  (references/notebooklm-workflow.md içine).

Stop after Phase 1B.

Phase 1C — Visual Scene System

Goals:
- 03-visual-scene-skill (SKILL.md + references).
- validate.py: scenes-file şeması + şablon props şemaları + manifest kontrolü +
  usedFacts ID'lerinin 01-facts.json'da mevcutluğu.
- BLOCKED asset kuralı, NEW TEMPLATE PROPOSAL kuralları, TEMPLATE-GAPS loglama.

Stop after Phase 1C.

Phase 1D — Timing + Packaging + Quality Gate

Goals:
- 04-timing-sync-skill + align.py (transcript-guided alignment + iki fallback).
- 05-packaging-skill: 05A Packaging Core + 05B Publishing Finalization ayrımıyla.
- /scripts/quality-gate.py (Bölüm 11'deki kontrol seti).
- /scripts/sync_manifest_usage.py (Bölüm 9 — usedInVideos otomasyonu).
- quality-gate.py'ın STATUS.md otomatik bloğunu yazma davranışı (Bölüm 10).

Stop after Phase 1D.

Phase 1E — Example Topic Output

Goals:
- Örnek konu: Why the Roman Empire Really Collapsed
- Üretilecekler:
  01-research.md, 01-facts.json, 02-script-annotated.md, 02-script-voiceover.txt,
  03-scenes.json, 04-scenes-final-estimated.json, 05-packaging.md (05A), STATUS.md
- Gerçek ses olmadığı için timing YALNIZCA word-count-estimate modunda.
- Sesli final render üretilmez. /render implement edilmez.

Stop after Phase 1E.
```

---

# 4. Packaging İki Aşamalıdır

Attribution Block yalnızca kullanılan asset'ler kesinleşince üretilebilir; packaging ise research sonrası paralel başlar. Çözüm:

```text
05A — Packaging Core  (01-research sonrası çalışabilir)

Produces:
1. Main YouTube Title
2. Alternative Titles
3. Thumbnail Concepts
4. Thumbnail Text Options
5. Video Description Draft
6. Tags / Keywords Draft
7. Pinned Comment Draft
8. Shorts Ideas (9:16 şablonlarla üretilebilir)
9. A/B Test Suggestions
10. CTR Angle Explanation
11. Script Hook Promise

Bu aşama Attribution Block ÜRETMEZ (asset'ler henüz belli değil).

05B — Publishing Finalization  (03-visual sonrası, asset kullanımı kesinleşince)

Produces:
1. Final Video Description
2. Final Tags
3. Final Pinned Comment
4. Attribution Block
5. Upload Checklist

manifest.json'da attributionRequired: true olan herhangi bir asset kullanıldıysa
Attribution Block zorunludur.
```

---

# 5. Fact Registry: 01-facts.json (Makine) + 01-research.md (İnsan)

P8 gereği fact/source kayıtlarının **makine doğruluk kaynağı JSON'dur**, markdown değil. quality-gate.py markdown parse ETMEZ; yalnızca `01-facts.json` okur.

```text
- 01-research.md  → insan dokümanı: anlatı, timeline, hook fikirleri, yapı önerisi.
  Fact'lere ID ile referans verir (ör. "...ordu maliyeti bütçeyi zorladı (F002)").
- 01-facts.json   → kanonik kayıt: tüm kaynaklar ve fact'ler, statülerle.
  Şeması: /templates/schemas/facts-file.schema.json
- Çelişkide 01-facts.json kazanır.
```

## 01-facts.json Formatı

```json
{
  "videoSlug": "why-rome-really-collapsed",
  "searchesUsed": 11,
  "searchBudget": 15,
  "sources": [
    {
      "id": "S001",
      "title": "Source title",
      "url": "https://...",
      "type": "academic | institutional | encyclopedic | popular | weak",
      "reliability": "high | medium | low",
      "notes": ""
    }
  ],
  "facts": [
    {
      "id": "F001",
      "claim": "Rome's western imperial authority ended in 476 CE.",
      "sources": ["S001", "S002"],
      "status": "VERIFIED",
      "scriptCritical": true,
      "isNumber": false,
      "notes": ""
    },
    {
      "id": "F002",
      "claim": "Military costs placed pressure on the imperial budget.",
      "sources": ["S003"],
      "status": "SINGLE-SOURCE",
      "scriptCritical": false,
      "isNumber": false,
      "notes": ""
    },
    {
      "id": "F003",
      "claim": "Uncertain claim.",
      "sources": [],
      "status": "VERIFY",
      "scriptCritical": false,
      "isNumber": false,
      "notes": "İkinci kaynak bulunamadı."
    }
  ]
}
```

## Alan Kuralları

```text
1. Her kaynak S-ID alır, her Key Fact F-ID alır.
2. status: VERIFIED | SINGLE-SOURCE | VERIFY
   - VERIFIED      = en az 2 bağımsız kaynak
   - SINGLE-SOURCE = tek kaynak + güvenilirlik notu
   - VERIFY        = doğrulanamadı
3. scriptCritical: true → narration'da geçecek/ekranda gösterilecek sayılar
   VE videonun ana iddiaları. scriptCritical fact'ler VERIFIED olmak zorundadır.
4. isNumber: true → iddia sayısal veri içeriyor (yıl hariç tutulabilir; skill
   tasarımında netleştirilir). isNumber:true bir fact script'te kullanılacaksa
   status VERIFIED olmalıdır.
5. Kaynaksız fact JSON'a girEMEZ; en fazla VERIFY statüsüyle ve boş sources ile
   "çözülemedi" kaydı olarak durur.
```

---

# 6. Kanonik VERIFY / SINGLE-SOURCE Kullanım Kuralı

Bu tablo tek doğruluk noktasıdır. Başka hiçbir bölüm bu kuralı yeniden tanımlayamaz; skill'ler ve quality-gate.py buraya referans verir.

```text
Status          Script + üretim dosyalarında kullanım
─────────────────────────────────────────────────────────────────────────────
VERIFIED        Serbest.

SINGLE-SOURCE   Yalnızca MİNÖR destekleyici iddia olarak kullanılabilir.
                YASAK olduğu yerler:
                - narration içinde sayısal veri
                - stat-card ve chart-scene verisi
                - videonun ana iddiası / hook iddiası
                - title, thumbnail, description, pinned comment iddiası
                (scriptCritical: true işaretlenen hiçbir fact SINGLE-SOURCE
                 kalamaz; ya ikinci kaynak bulunur ya fact script dışı kalır.)

VERIFY          Research raporu dışında HER YERDE yasak.
─────────────────────────────────────────────────────────────────────────────
```

## Literal Etiket Kuralı

```text
"[VERIFY]" ve "[SINGLE-SOURCE]" literal metinleri yalnızca 01-research.md ve
01-facts.json içinde bulunabilir. Diğer tüm dosyalarda (script, VO, scenes JSON,
packaging) görünmeleri quality-gate FAIL sebebidir. Üretim dosyalarında takip
etiketle değil, fact ID + status üzerinden yapılır.
```

---

# 7. Timing: Transcript-Guided Alignment (Gerçekçi Tanım)

Hedef davranış korunur, terim gerçekçileşir: kullanılacak araçların çoğu (faster-whisper vb.) strict forced alignment değil, transkripsiyon + kelime timestamp üretir.

```text
Primary Timing Mode: transcript-guided word timestamp alignment

Araç adayları: faster-whisper (4GB RAM'e en uygun, torch'suz),
whisper-timestamped, stable-ts. Seçim skill tasarımında yapılır;
tiny/base model yeterlidir (metin elimizde, yalnızca hizalama yapılıyor).

align.py davranışı:
1. Ses dosyasından kelime timestamp'leri üret.
2. Üretilen transkripti 02-script-voiceover.txt ile karşılaştır.
3. Fuzzy matching ile kelime/öbekleri sahnelere geri eşle
   (rapidfuzz önerilir; stdlib difflib kabul edilebilir. Torch bağımlı
   araçlardan — ör. whisperX — 4GB RAM nedeniyle kaçınılır).
4. Düşük güvenli segmentleri işaretle.
5. Güven skoru eşiğin altındaysa sesli final render'ı ENGELLE ve STATUS.md'ye
   kullanıcı aksiyonu yaz (dosya kontrolü, retry komutu).

timingMode değerleri (scenes-file.schema.json enum'u ile birebir):
  forced-alignment | transcript-guided-alignment |
  proportional-estimate | word-count-estimate

Sesli final render kuralı:
  YALNIZCA timingMode "forced-alignment" veya "transcript-guided-alignment"
  olan 04-scenes-final.json geçerli girdidir.
  04-scenes-final-estimated.json hiçbir koşulda sesli final render'a giremez.
```

Mod B (proportional-estimate: ffprobe süresi + kelime oransal dağıtım + normalize) ve Mod C (word-count-estimate: 150 WPM) brief'teki gibi korunur; yalnızca taslak/sessiz önizleme içindir.

---

# 8. Asset Bootstrap İstisnası

```text
≤5 yeni asset/video kuralı, yeniden kullanılabilir kütüphane KURULDUKTAN SONRA
geçerlidir. İlk 1–3 videoda yeni asset sayısı 5'i aşabilir; şartlar:

1. her yeni asset yeniden kullanılabilir olmalı (reusable: true),
2. her yeni asset manifest.json'a eklenmeli,
3. her yeni asset lisans metadata'sı taşımalı,
4. license: Unknown hiçbir asset final çıktıda kullanılamaz,
5. BLOCKED asset'ler asla kullanılamaz,
6. LICENSES.md güncellenmeli.

Bootstrap dönemi sonunda ≤5 kuralı yeniden sertleşir. validate.py bootstrap
modunu bir bayrakla destekler (ör. --bootstrap); bayrak yokken sert kural.
```

---

# 9. Manifest Ek Alanları + usedInVideos Otomasyonu

```json
{
  "id": "icon-warning-red",
  "type": "icon",
  "source": "Tabler Icons",
  "sourceUrl": "https://tabler.io/icons",
  "license": "MIT",
  "attributionRequired": false,
  "attributionText": "",
  "filePath": "/assets/library/icons/icon-warning-red.svg",
  "tags": ["warning", "danger", "alert"],
  "createdAt": "YYYY-MM-DD",
  "updatedAt": "YYYY-MM-DD",
  "status": "ACTIVE",
  "reusable": true,
  "usedInVideos": [],
  "notes": "Default warning icon for map-scene and stat-card."
}
```

```text
Kurallar:
1. license: Unknown → status: BLOCKED (otomatik).
2. BLOCKED asset 03-scenes.json'da görünemez.
3. attributionRequired asset'ler 05B Publishing Finalization'a bildirilir.
4. Final videoda kullanılan her asset manifest.json'da bulunmak zorundadır.
5. Uzak URL'ler indirilip lisanslanıp kütüphaneye eklenmeden final render
   JSON'ında doğrudan kullanılamaz.

usedInVideos OTOMASYONU (P7):
- Bu alan ASLA elle güncellenmez (elle güncellenirse 3. videodan sonra çürür).
- /scripts/sync_manifest_usage.py tüm /outputs/*/03-scenes.json dosyalarını
  tarar ve her asset'in usedInVideos listesini yeniden üretir.
- quality-gate.py çalışırken sync'in güncel olup olmadığını kontrol eder
  (stale ise uyarı verir ve komutu STATUS.md'ye yazar).
```

---

# 10. STATUS.md: Otomatik Doğrulama Bloğu

Doğrulama bölümlerini insan değil, quality-gate.py doldurur (P7). İnsan yalnızca Session Notes yazar.

```text
- quality-gate.py her çalıştığında STATUS.md içindeki işaretli bloğu
  yeniden yazar:

  <!-- QG:BEGIN — bu blok quality-gate.py tarafından üretilir, elle düzenleme -->
  ... Validation / Fact / Asset / Timing durumları ...
  <!-- QG:END -->

- Blok içeriği:
  Validation Status  : derive_vo diff, validate.py, align.py, gate sonucu
  Fact Status        : kullanılan fact sayısı, VERIFY ihlali var mı,
                       scriptCritical fact'ler VERIFIED mi
  Asset Status       : kullanılan/yeni asset sayısı, BLOCKED ihlali,
                       attribution gerekli mi / tamamlandı mı
  Timing Status      : timingMode, ses dosyası mevcut mu, güven skoru,
                       sesli final render'a izin var mı

- İnsanın doldurduğu bölümler: Video Info, Session Notes
  (Current Phase, Completed This Session, Files Created/Modified,
   Commands Run, Blockers, Next Exact Step), Quota Notes.
```

Brief'teki STATUS.md şablonu korunur; yukarıdaki QG bloğu ve Session Notes bölümü eklenir.

---

# 11. quality-gate.py Kontrol Seti (Güncellenmiş)

Tümü mekanik ve sıfır tokendir. Fact kontrolleri **yalnızca 01-facts.json** üzerinden yapılır; markdown parse edilmez.

```text
Fact Checks (kaynak: 01-facts.json + sahnelerin usedFacts alanları):
- 01-facts.json şema validasyonu (facts-file.schema.json).
- Sahnelerde kullanılan her fact ID 01-facts.json'da mevcut mu → değilse FAIL.
- Used Fact status: VERIFY → FAIL.
- scriptCritical: true olan kullanılmış fact status != VERIFIED → FAIL.
- isNumber: true olan kullanılmış fact status != VERIFIED → FAIL.
- Literal "[VERIFY]" / "[SINGLE-SOURCE]" metni 01-research.md ve 01-facts.json
  DIŞINDA herhangi bir dosyada → FAIL.
- Heuristik: sahne narration'ı rakam içeriyor ama usedFacts boş → WARN
  (insan checklist'ine işaret düşer).

VO Checks:
- derive_vo.py yeniden çalıştırılır; mevcut 02-script-voiceover.txt ile
  diff != 0 → FAIL.

Scene Checks:
- 03-scenes.json ve 04-scenes-final*.json şema validasyonu.
- Her sahnenin props'u kendi şablon şemasına karşı doğrulanır.
- Bilinmeyen template adı → FAIL. Eksik required prop → FAIL.
- Sahne narration'ı annotated script'teki narration'dan farklıysa → FAIL.

Asset Checks:
- Kullanılan asset manifest'te yok → FAIL.
- status: BLOCKED veya license: Unknown asset kullanımı → FAIL.
- attributionRequired asset var ama 05-packaging.md'de (05B) Attribution Block
  yok → FAIL.
- newAssets > 5 (bootstrap bayrağı yokken) → FAIL.
- sync_manifest_usage.py çıktısı stale → WARN + komut önerisi.

Timing Checks:
- Final timing JSON şema validasyonu + audio metadata mevcut mu → yoksa FAIL.
- Sesli final render girdisinde timingMode word-count-estimate veya
  proportional-estimate → FAIL.
- Sahne > 12 sn → WARN (LONG SCENE). Sahne < 2 sn → WARN (SHORT SCENE).
- (Alignment modunda) düşük güven skorlu segmentler → WARN, eşik altıysa FAIL.

Packaging Checks:
- Script Hook Promise eksik → FAIL.
- Hook Promise Audit PENDING → WARN.

NOT — mekanik olmayan kontrol YOKTUR:
"Title/thumbnail desteklenmeyen iddia içeriyor mu" kontrolü yargısaldır ve
quality-gate.py'da DEĞİL, Katman 2 insan checklist'indedir (Bölüm 12).
Gate'e konursa ya sahte implement edilir ya hep PASS döner.
```

---

# 12. Katman 2 — İnsan Checklist'i (Ekler)

Brief'teki insan checklist'i korunur; şu maddeler eklenir:

```markdown
- [ ] Title, thumbnail, description ve pinned comment'taki her iddia
      VERIFIED bir fact'e dayanıyor mu? (mekanik gate bunu KONTROL ETMEZ)
- [ ] Rakam içerip usedFacts'i boş olan sahne uyarıları (gate WARN listesi)
      tek tek gözden geçirildi mi?
- [ ] SINGLE-SOURCE fact'ler yalnızca minör destekleyici iddia olarak mı
      kullanılmış? (Bölüm 6 tablosu)
```

---

# 13. Hook Promise Geri Besleme Akışı

```text
05A Packaging Core, 02-script'ten ÖNCE varsa:
- 02-script hook'u Script Hook Promise'i girdi alır.
- Hook Promise Audit PASS olmalı veya hook revize edilmeli.

05A yoksa:
- Hook, research'teki hook fikirleriyle yazılır.
- Audit statüsü: PENDING — packaging not available yet.

05A sonradan üretilince:
- Promise Match Check koşulur.
- Uyumsuzlukta YALNIZCA hook bölümü revize edilir; tam script regeneration'dan
  kaçınılır (kota kuralı 4 ile uyumlu).
```

---

# 14. Annotated Script Sahne Formatı (Used Facts Dahil)

```markdown
## Scene [number]

Word Count:
Estimated Duration:

Narration:
[Clean narration text]

Used Facts:
- F001
- F002

Visual Intent:
[Tek cümle. Detaylı animasyon tarifi YOK — o 03'ün işi.]

On-screen Text:
[2–7 kelime]

Emotional Tone:
[emotion/tone]
```

```text
Kurallar:
1. Used Facts boş olabilir; ama sahne factual claim içeriyorsa boş bırakılamaz.
2. Narration 30 kelimeyi aşarsa sahne bölünür.
3. Template seçimi 03-visual-scene-skill'e aittir; script şablon adı yazmaz.
```

---

# 15. 03-scenes.json: usedFacts Taşınır

```json
{
  "sceneNumber": 8,
  "narration": "The empire became too expensive to defend.",
  "usedFacts": ["F002"],
  "wordCount": 8,
  "estimatedDuration": 3.5,
  "template": "map-scene",
  "props": {
    "region": "roman-empire-max-extent",
    "highlights": ["borders"],
    "icons": [{ "asset": "icon-warning-red", "placement": "borders" }],
    "camera": "slow-zoom-out",
    "onScreenText": "TOO EXPENSIVE TO DEFEND"
  },
  "assets": {
    "fromLibrary": ["map-roman-empire", "icon-warning-red"],
    "newAssets": []
  },
  "emotionalTone": "tension",
  "styleNotes": "Keep the map simple and readable."
}
```

```text
Ek kural:
03-visual-scene-skill YENİ factual claim ekleyemez; yalnızca
02-script-annotated.md'de zaten mevcut iddiaları görselleştirir.
```

---

# 16. Phase 2 Render Güvenlik Kuralı

```text
/render implement edilmeden önce:
1. En az bir tam Phase 1 örnek çıktısı mevcut olmalı.
2. Örnek için quality-gate.py PASS olmalı.
3. 12 şablon şeması stabil olmalı.
4. Manifest yapısı stabil olmalı.
5. Kullanıcı Faz 2'yi AÇIKÇA onaylamalı.

Phase 1 sırasında Remotion component'i veya GitHub Actions workflow'u
oluşturulmaz (açıkça istenmedikçe).

Not: Dış servis limitleri, lisans şartları, GitHub Actions kotaları ve Remotion
lisans koşulları zamanla değişebilir. Faz 2'ye başlamadan güncel resmi
dokümantasyon doğrulanır.
```

---

# 17. Claude Pro Kota Koruma Ek Kuralları

```text
1. Büyük JSON'lar gerekmedikçe komple regenerate edilmez; hedefli sahne editi.
2. SKILL.md kısa tutulur; uzun örnekler /references altında.
3. Deterministik işler script'e (P7): derive_vo, validate, align, quality-gate,
   sync_manifest_usage.
4. STATUS.md güncel durumu içerirken Claude'a tüm projeyi yeniden okutma.
5. Her oturum şununla biter: tamamlanan dosyalar + doğrulama durumu +
   sıradaki net adım (STATUS.md Session Notes).
6. İlk 2–3 videoda her ana aşamanın öncesi/sonrası /usage değeri
   Quota Notes'a kaydedilir; optimizasyon kararları (ör. NotebookLM akışı)
   tahminle değil ölçümle verilir.
```

---

# 18. Claude Code Ana Uygulama Promptu

```text
You are implementing the YouTube Production Skill System v2.1.1.

Important:
This is a 5 Core Skills + Render Layer system.
06-Render is Phase 2 and must not be implemented now.

Do not implement everything in one pass.
Work only on the phase I explicitly request.

Global rules:
- Follow PROJECT-BRIEF-v2.1.md AND STABILIZATION-PATCH-v2.1.1.md.
  On conflict: P1–P8 principles > this patch > the rest of the brief.
- Keep SKILL.md files concise; long examples go to /references.
- Use scripts for deterministic tasks (P7).
- Use /templates/schemas as the machine source of truth (P8).
  Fact records live in 01-facts.json (facts-file.schema.json), not markdown.
- Do not duplicate schemas or catalogs inside skill folders.
- Do not use BLOCKED or Unknown-license assets.
- Do not invent sources or facts.
- Never use VERIFY facts outside 01-research.md / 01-facts.json.
- SINGLE-SOURCE facts: minor supporting claims only — never numbers,
  stat-cards, charts, main claims, or packaging claims (Section 6 table).
- usedInVideos is script-maintained (sync_manifest_usage.py), never hand-edited.
- quality-gate.py writes the QG block in STATUS.md automatically.
- Judgmental checks (title/thumbnail claims) belong to the human checklist,
  not quality-gate.py.
- Do not implement /render unless I explicitly request Phase 2.

After each phase:
1. list files created,
2. list files modified,
3. list commands run,
4. list validation results,
5. list blockers,
6. stop and wait.

Start with the phase I request.
```

---

# 19. Phase 1A Başlangıç Promptu

```text
Implement Phase 1A only.

Goal:
Create the repository skeleton and global contracts for the
YouTube Production Skill System v2.1.1.

Use:
- PROJECT-BRIEF-v2.1.md
- STABILIZATION-PATCH-v2.1.1.md

Tasks:
1. Create the full folder structure (brief file structure + patch deltas below).
2. Add both documents to the repo root.
3. Create /templates/template-catalog.md (12 templates: name, purpose,
   props table, example props, asset needs, 9:16 variant note).
4. Create /templates/TEMPLATE-GAPS.md (empty).
5. Create /templates/schemas/scenes-file.schema.json with:
   - optional "usedFacts" array on scene objects,
   - "timingMode" enum: forced-alignment | transcript-guided-alignment |
     proportional-estimate | word-count-estimate,
   - audio metadata block definition.
6. Create schema files for the 12 approved templates:
   map-scene, timeline-scene, stat-card, comparison-split, list-reveal,
   quote-card, silhouette-scene, chart-scene, icon-grid, text-emphasis,
   image-spotlight, transition-break.
7. Create /templates/schemas/facts-file.schema.json
   (sources: id/title/url/type/reliability/notes;
    facts: id/claim/sources/status/scriptCritical/isNumber/notes).
8. Create /assets/library/manifest.json skeleton with the extended fields
   (license, attributionRequired, status, reusable, usedInVideos, updatedAt...).
9. Create /assets/library/LICENSES.md.
10. Create /outputs/.gitkeep.
11. Do not create any skill files yet.
12. Do not implement /render.
13. Do not create example video output yet.

After completion:
- list all created files,
- explain validation status,
- list remaining blockers,
- stop.
```

---

# 20. Dosya Yapısı Deltası (v2.1'e Ekler)

```text
/youtube-production-skills
  STABILIZATION-PATCH-v2.1.1.md          ← bu doküman (repo köküne)

  /scripts
    quality-gate.py
    sync_manifest_usage.py               ← YENİ (usedInVideos otomasyonu)

  /templates/schemas
    facts-file.schema.json               ← YENİ (01-facts.json şeması)
    scenes-file.schema.json              ← GÜNCEL (usedFacts + timingMode enum)

  /outputs/{video-slug}
    01-facts.json                        ← YENİ (fact registry, makine kaynağı)
```

Diğer tüm yapı PROJECT-BRIEF-v2.1.md'deki gibidir.

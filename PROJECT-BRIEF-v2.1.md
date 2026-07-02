# YouTube Production Skill System v2.1 — 5 Skill Pipeline — Project Brief

Bu projede amaç, YouTube videoları üretmek için ajan mantığından çok **skill tabanlı, modüler ve geliştirilebilir bir içerik üretim sistemi** kurmak.

Kanal konsepti İngilizce olacak. İçerik tarzı; bilgi, tarih, ekonomi, medeniyetler, hayatta kalma senaryoları, "what if" konuları ve infografik anlatım üzerine kurulacak. Referans tarz: **The Infographics Show + sinematik belgesel anlatımı + veri destekli hikâye anlatımı**.

## v2.1 Değişiklik Özeti (v2'ye göre)

```text
- Sistem resmi adı: "YouTube Production Skill System v2.1 — 5 Skill Pipeline"
- 01-research: Manual Source Mode + Web Search Mode + hibrit mod + Research Request Output
- 01-research: Çift kaynak kuralı DARALTILDI (yalnızca script-kritik sayılar)
- 01-research: Video başına arama bütçesi (max 15 web search)
- 01-research: NotebookLM opsiyonel akış olarak references'a eklendi
- 02-script: VO script artık LLM ile değil, scripts/derive_vo.py ile mekanik türetilir
- 02-script: Promise Match Check + Hook Promise Audit eklendi
- 03-visual: Props şemaları JSON Schema dosyası oldu (/templates/schemas/) + validate.py
- 03-visual: NEW TEMPLATE PROPOSAL eşiği sıkılaştı + TEMPLATE-GAPS.md (videolar arası log)
- 04-timing: İki katmanlı fallback (oransal normalizasyon + saf tahmin); estimated dosya ile
  sesli final render YASAK
- 04-timing: Final JSON'a audio metadata eklendi
- Asset manifest: lisans alanları + BLOCKED kuralı + LICENSES.md
- 05-packaging: Script Hook Promise + Attribution Block eklendi
- STATUS.md standart formatı + Quota Notes bölümü
- Quality gate büyük ölçüde script'e döküldü (scripts/quality-gate.py)
- Yeni prensipler: P7 (Deterministik İş Script'e), P8 (Şema Öncelikli Sözleşmeler)
- Yeni bölüm: 06-Render (Remotion + GitHub Actions) — Faz 2
- Yeni bölüm: Claude Pro Kota Kuralları
```

---

# Mimari Prensipler (Tüm Skill'ler İçin Bağlayıcı)

Bu prensipler her skill'in üzerinde durur. Skill'ler arasında çelişki olursa bu bölüm kazanır.

## P1 — Audio-First Timing (Ses Master Clock'tur)

Gerçek sahne sürelerini script'teki tahminler değil, üretilen ElevenLabs ses dosyası belirler. Script aşamasındaki süre tahminleri sadece planlama aracıdır. Ses üretildikten sonra `04-timing-sync-skill` forced alignment ile gerçek süreleri çıkarır ve sahne JSON'ını günceller. **Final render her zaman forced-alignment ile üretilmiş `04-scenes-final.json` ile yapılır.** Alignment başarısız olursa fallback modları devreye girer (bkz. 04) ama fallback çıktısı asla sesli final render'a girdi olamaz. Video sese göre şekillenir; asla tersi değil.

## P2 — Şablon Tabanlı Sahneler (Özgün Animasyon Tarifi Yok)

Visual-scene-skill her sahne için özgün animasyon tarifi YAZMAZ. Her narration segmentini önceden tanımlı bir **sahne şablonuna** eşler ve şablonun parametrelerini (props) doldurur. Şablonlar Remotion'da bir kez component olarak kodlanır; sonrasında her video sadece props üretir. Şablon kataloğu `/templates/template-catalog.md`'de, props şemaları `/templates/schemas/`'ta tanımlıdır. Yeni şablon eklemek bilinçli bir karardır (bkz. NEW TEMPLATE PROPOSAL kuralı).

## P3 — Büyüyen Asset Kütüphanesi

Sıfır ek bütçe kısıtı nedeniyle her video onlarca yeni asset gerektiremez. `/assets/library/` altında merkezi bir asset kütüphanesi tutulur (`manifest.json` ile indekslenir). Visual-scene-skill önce kütüphaneden asset seçer; kütüphanede yoksa `NEW ASSET` olarak işaretler (hedef: video başına ≤ 5 yeni asset). Her yeni asset kütüphaneye eklenir ve manifest güncellenir.

**Lisans kuralı:** Lisans alanı olmayan hiçbir asset kütüphaneye eklenemez. Lisansı bilinmeyen asset `BLOCKED` işaretlenir ve final çıktıda kullanılamaz.

Başlangıç kütüphanesi ücretsiz kaynaklardan kurulur:

- İkonlar: Lucide, Tabler Icons (MIT)
- Emoji/figür: OpenMoji (CC BY-SA — attribution zorunlu)
- Harita verisi: Natural Earth (public domain)
- Oyun/genel görsel öğeler: Kenney (CC0)

## P4 — Tek Doğruluk Kaynağı: Annotated Script

Annotated video script, narration metninin tek doğruluk kaynağıdır. ElevenLabs voiceover script'i ayrıca YAZILMAZ ve **LLM tarafından da türetilmez**; `02-script-skill/scripts/derive_vo.py` annotated script'teki narration alanlarını sırayla birleştirerek mekanik üretir. İki dosyanın narration içerikleri karakter karakter aynıdır (quality gate bunu diff ile doğrular). Narration'da değişiklik yapılacaksa önce annotated script güncellenir, VO script yeniden türetilir.

## P5 — Doğrulanabilir Araştırma

Research skill'in ürettiği her önemli bilgi doğrulanabilir olmalıdır. Kaynaksız bilgi üretilmez. Emin olunamayan bilgi `[VERIFY]` etiketiyle işaretlenir ve script'e giremez. Sayısal veriler için çift kaynak kuralı **daraltılmış** kapsamda uygulanır (bkz. 01-research-skill). Web/kaynak erişimi yoksa bilgi uydurulmaz; Research Request Output üretilir.

## P6 — Video Bazlı Çıktı Klasörü

Çıktılar türe göre değil, videoya göre gruplanır. Her video `/outputs/{video-slug}/` altında kendi klasörüne sahiptir. Session handoff'ta tek klasör + `STATUS.md` tüm durumu gösterir.

## P7 — Deterministik İş Script'e (YENİ)

Deterministik, tekrarlanabilir her iş LLM'e değil, çalıştırılabilir script'lere yaptırılır: VO türetme (`derive_vo.py`), forced alignment (`align.py`), şema doğrulama (`validate.py`), kalite kapısı (`quality-gate.py`). Bu hem hatayı sıfırlar hem Claude Pro kotasını korur. Bir işin LLM'e mi script'e mi ait olduğu tartışmalıysa varsayılan cevap script'tir.

## P8 — Şema Öncelikli Sözleşmeler (YENİ)

Skill'ler arası veri sözleşmelerinin makine doğruluk kaynağı JSON Schema dosyalarıdır (`/templates/schemas/`). Markdown katalog insan dokümanıdır; çelişkide şema kazanır. Remotion tarafında TypeScript tipleri aynı şemalardan üretilir (`json-schema-to-typescript`) — skill'den component'e tek doğruluk kaynağı.

---

# Claude Pro Kota Kuralları (Bağlayıcı)

Proje Claude Pro aboneliğiyle, Claude Code üzerinden yürütülecektir. Pro'da kullanım limitleri claude.ai ve Claude Code arasında **paylaşılır** (5 saatlik oturum penceresi + haftalık limit). Bu nedenle:

```text
1. Aşama başına bir oturum: Bir 5 saatlik pencereye bir skill aşaması sığdırılır.
   STATUS.md session handoff'un tek kaynağıdır.
2. Deterministik işler script'e (P7). LLM yalnızca yaratıcı/yargısal işe harcanır.
3. CLAUDE.md < 200 satır, SKILL.md gövdesi < 500 satır. Uzun format/örnekler
   /references altında (progressive disclosure).
4. Büyük JSON'lar komple regenerate edilmez; tek sahne düzeyinde selektif edit yapılır.
5. Research'te arama bütçesi uygulanır (bkz. 01-research-skill).
6. Render GitHub Actions'ta çalışır — Claude kotasından tamamen bağımsız.
7. Kota ölçümü: İlk 2-3 videoda her aşamanın öncesi/sonrası /usage değeri
   STATUS.md "Quota Notes" bölümüne kaydedilir. Optimizasyon kararları
   (ör. NotebookLM akışını devreye almak) tahminle değil bu ölçümle verilir.
```

---

# Genel Çalışma Akışı

Kullanıcı bir video konusu verir:

```text
Video Topic: Why the Roman Empire Really Collapsed
Target Language: English
Target Length: 7 minutes
Style: The Infographics Show + cinematic documentary + simple infographic animation
```

Sistem şu akışla çalışır:

```text
01-research-skill
      │
      ├──────────────────────────────┐
      ▼                              ▼
02-script-skill              05-packaging-skill
  (+ derive_vo.py)           (paralel çalışabilir)
      │
      ▼
03-visual-scene-skill
  (+ validate.py)
      │
      ▼
[MANUEL ADIM: ElevenLabs ses üretimi — pipeline dışı]
      │
      ▼
04-timing-sync-skill
  (align.py / fallback modları)
      │
      ▼
[quality-gate.py — PASS zorunlu]
      │
      ▼
06-render (Remotion + GitHub Actions — Faz 2)
```

Notlar:

- `05-packaging-skill` research bittikten sonra script'i beklemeden çalışabilir. Ürettiği **Script Hook Promise**, script skill'e hook girdisi olarak geri beslenir; tıklama vaadini videonun ilk 20 saniyesi karşılamalıdır.
- Packaging henüz çalışmadıysa script, research'teki hook fikirleriyle yazılır; packaging tamamlandığında Promise Match Check sonradan audit olarak koşulur, uyumsuzsa hook revize edilir (sert bağımlılık yok).
- Ses üretimi bilinçli olarak pipeline dışındadır. Kullanıcı VO script'i alır, ElevenLabs'te sesi üretir ve dosyayı `/outputs/{video-slug}/audio/voiceover.mp3` olarak bırakır. `04-timing-sync-skill` bu dosyanın varlığıyla tetiklenir.

Her skill kendi görevini yapmalı, başka skill'in alanına girmemelidir. Bir skill güncellenirken diğerleri bozulmamalıdır.

---

# 01-research-skill

## Görevi

Verilen video konusunu araştırır ve script yazımı için sağlam, **doğrulanabilir** bir bilgi temeli oluşturur. Video metni yazmaz; sadece araştırır, düzenler ve script skill'ine kaliteli hammadde sağlar.

## Çalışma Modları

```text
1. Manual Source Mode  — kullanıcı kaynak/not sağlar
2. Web Search Mode     — web search aracı mevcutsa (varsayılan)
Hibrit               — kullanıcı kaynak verdiyse VE web varsa: önce manuel
                        kaynaklar işlenir, web search eksikleri ve ikinci
                        kaynakları tamamlar
```

### Mod Seçimi

```text
If user provided sources AND web search available → Hibrit
If user provided sources only                    → Manual Source Mode
If web search available only                     → Web Search Mode
If no sources and no web search                  → Research Request Output
                                                    (bilgi UYDURULMAZ)
```

### Manual Source Mode Kuralları

```text
- Kullanıcı kaynak sağlamışsa önce o kaynaklar kullanılır.
- Kaynağı olmayan önemli bilgi Key Fact olarak yazılamaz.
- Kaynağı belirsiz bilgiler [VERIFY] etiketi alır.
- Kaynak yetersizse çıktının sonunda "Missing Sources" bölümü oluşturulur.
```

### Research Request Output (kaynak yoksa)

```markdown
# Research Request

This topic requires external sources before a verified script can be produced.

## Topic
[video topic]

## Sources Needed
1. Academic or institutional overview source
2. At least one source for key dates and events
3. At least one source for numbers/statistics
4. Optional: one popular source for audience-friendly framing

## Suggested Search Queries
- query 1
- query 2
- query 3

## Current Status
Research cannot be marked complete until sources are provided or web search is available.
```

## Zorunlu Doğrulama Kuralları

1. **Her Key Fact için kaynak** verilir. Kaynaksız fact çıktıya giremez.
2. **Daraltılmış çift kaynak kuralı:** Yalnızca **script-kritik sayılar** — narration'da geçecek veya ekranda gösterilecek (stat-card, chart-scene) sayısal veriler — için en az 2 bağımsız kaynak zorunludur. Research raporundaki diğer destekleyici sayılar tek kaynak + güvenilirlik notu ile kalabilir ve `[SINGLE-SOURCE]` işaretlenir. Script tek kaynaklı bir sayıyı kullanmak isterse: bütçe içinde hedefli ikinci kaynak araması yapılır; bulunamazsa sayı `[VERIFY]` olur ve script'e giremez.
3. **Arama bütçesi:** Video başına en fazla **15 web search** (ikinci-kaynak aramaları dahil). Bütçe dolduğunda kalan doğrulamalar `[VERIFY]` olarak işaretlenir ve raporlanır.
4. **Emin olunamayan her bilgi `[VERIFY]` etiketi alır.** Script skill `[VERIFY]` etiketli bilgiyi metne alamaz; ya çözülür ya çıkarılır. (Projenin genel Knowledge Honesty / TBD kuralının research'e uygulanmış hali.)
5. **Source Notes bölümü zorunludur** ve her kaynağın güvenilirlik notunu içerir (akademik / kurumsal / ansiklopedik / popüler / zayıf).

## Üretmesi Gereken Çıktılar

```text
1. Topic Summary
2. Core Story Angle
3. Key Facts (her biri kaynaklı)
4. Timeline / Sequence of Events
5. Important Characters, Groups, Countries, or Institutions
6. Numbers, Data, and Statistics (script-kritik olanlar çift kaynaklı)
7. Common Misconceptions
8. Surprising Details
9. Conflict / Tension Points
10. Possible Hook Ideas
11. Suggested Video Structure
12. Source Notes (zorunlu, güvenilirlik notlu)
13. Missing Sources (koşullu — çözülemeyen iddialar varsa)
```

## Araştırma Mantığı

Araştırma yüzeysel olmamalıdır. Videoda kullanılabilecek ilginç, şaşırtıcı ve izleyiciyi merakta tutacak detaylar bulunmalıdır. Örneğin konu "Why the Roman Empire Really Collapsed" ise sadece "barbarian invasions" demek yeterli değildir; ekonomi, ordu maliyeti, politik istikrarsızlık, enflasyon, sınır güvenliği, iç çürüme ve halk üzerindeki etkiler de açıklanmalıdır.

## Çıktı Formatı

```markdown
# Research Report

## Topic Summary
Short explanation of the topic.

## Core Story Angle
The main narrative angle of the video.

## Key Facts
- Fact 1 — [Source: URL]
- Fact 2 — [Source: URL]
- Fact 3 [VERIFY] — tek kaynak bulundu, ikinci kaynak doğrulanamadı

## Timeline / Sequence
1. Event — [Source: URL]
2. Event — [Source: URL]

## Numbers, Data, and Statistics
- Statistic — [Sources: URL1, URL2]            ← script-ready (çift kaynaklı)
- Statistic — [Source: URL1] [SINGLE-SOURCE]   ← rapor içi; script'e girmeden
                                                  önce ikinci kaynak gerekir

## Surprising Details
- Detail 1 — [Source: URL]

## Hook Ideas
1. Hook idea
2. Hook idea
3. Hook idea

## Suggested Video Structure
- Intro
- Problem setup
- Main story
- Turning point
- Final lesson

## Source Notes
1. URL — kaynak türü, güvenilirlik değerlendirmesi
2. URL — kaynak türü, güvenilirlik değerlendirmesi

## Missing Sources (koşullu)
- Claim: ...
  Status: [VERIFY]
  Needed Source Type: ...
```

## Opsiyonel: NotebookLM Ön-Akışı

Zorunlu değildir; kota ölçümü yüksek çıkarsa devreye alınır. `references/notebooklm-workflow.md` dosyasında dokümante edilir:

```text
- Konu → NotebookLM Discover Sources + manuel kaynak ekleme → 5-10 kaynağa küratörlük
- Numaralı kaynak listesi (URL'li) notebook'a ayrı kaynak olarak yapıştırılır
- Standart ekstraksiyon prompt'u (Custom Instructions'a gömülü) Research Report
  formatını üretir; her fact'in sonuna [S1], [S2] kaynak referansı zorunludur
- Çıktı Manual Source Mode'a yapıştırılır; Claude tarafında yalnızca normalizasyon,
  kalite notlaması, çift kaynak kontrolü ve [VERIFY] etiketleme kalır
- Uyarı: grounded ≠ hatasız; kaynak küratörlüğü kullanıcıya aittir
```

## Kalite Kriterleri

- Uydurma bilgi içermemeli; mekanizması yukarıdaki doğrulama kurallarıdır.
- Video metnine dönüştürülebilecek kadar zengin olmalı.
- Sıkıcı ansiklopedi dili değil, hikâye anlatımına uygun bilgi seçimi.
- Arama bütçesine uyulmalı ve kullanılan arama sayısı raporlanmalı.

---

# 02-script-skill

## Görevi

`01-research-skill` çıktısını alır ve İngilizce YouTube video metnine dönüştürür. Ana görev: araştırma notlarını sıkıcı bilgi listesinden çıkarıp izleyicinin sonuna kadar izlemek isteyeceği bir hikâye anlatımına çevirmek.

## Tek Doğruluk Kaynağı Kuralı (P4)

Bu skill **yalnızca Annotated Video Script** üretir. ElevenLabs Voiceover Script'i `scripts/derive_vo.py` mekanik olarak türetir:

```text
derive_vo.py:
- 02-script-annotated.md'yi parse eder
- Narration bloklarını sahne sırasıyla birleştirir (aralarında boş satır)
- 02-script-voiceover.txt'yi yazar
- Sahne başına ve toplam kelime sayısı raporu üretir
- quality-gate.py bu dosyayı yeniden üretip diff'leyerek P4'ü doğrular (fark = 0)
```

## Hız ve Kelime Bütçesi Kuralı (P1 desteği)

```text
Konuşma hızı varsayımı: ~150 kelime/dakika (≈ 2.5 kelime/saniye)
Sahne narration bütçesi: 12–25 kelime (≈ 5–10 saniye)
Sert üst sınır: 30 kelime/sahne (aşan narration iki sahneye bölünür)
7 dakikalık video toplam bütçesi: ~1.000–1.100 kelime
```

Her sahnede kelime sayısı raporlanır. Bu tahminler planlamadır; gerçek süreler `04-timing-sync-skill`'den gelir. Ancak kelime disiplini kritiktir: 40 kelimelik sahne narration'ı 16 saniyelik durağan sahne üretir — bunu hiçbir timing düzeltmesi kurtaramaz.

## `[VERIFY]` ve Sayı Kuralı

- `[VERIFY]` etiketli bilgi script'e alınamaz. Kritikse research'e dönülüp çözülür; değilse çıkarılır.
- Narration'da veya ekranda (stat-card/chart) kullanılacak **her sayı çift kaynaklı olmalıdır.** Research'te `[SINGLE-SOURCE]` işaretli bir sayı kullanılmak isteniyorsa önce research'e ikinci kaynak talebi gönderilir.

## Promise Match Check

Packaging'in ürettiği Script Hook Promise mevcutsa, hook yazıldıktan sonra şu kontrol yapılır:

```text
1. İlk 20 saniye başlık vaadini net karşılıyor mu?
2. İlk 20 saniye thumbnail konseptiyle görsel/duygusal olarak uyumlu mu?
3. Hook yanıltmadan merak yaratıyor mu?
4. Hook yavaş/jenerik arka plan anlatımından kaçınıyor mu?
```

Cevaplardan biri "no" ise hook yeniden yazılır. Script çıktısının sonuna **Hook Promise Audit** eklenir:

```markdown
## Hook Promise Audit

Title Promise:
Why Rome Was Already Dead Before It Fell

Thumbnail Promise:
ROME WAS ALREADY DEAD

Hook Match:
PASS

Reason:
The first 20 seconds clearly state that Rome did not collapse in one moment and
frames the story as an internal breakdown that began before the final invasions.
```

Packaging henüz yoksa audit `PENDING — packaging bekliyor` olarak işaretlenir ve packaging sonrası koşulur.

## 1. Annotated Video Script (birincil çıktı)

Her sahne şu bilgileri içerir:

```text
Scene Number
Word Count
Estimated Duration (150 wpm varsayımıyla)
Narration
Visual Intent (1 cümlelik görsel niyet — detaylı tarif DEĞİL, o 03'ün işi)
On-screen Text
Emotional Tone
```

Örnek:

```markdown
## Scene 1

Word Count: 9
Estimated Duration: ~4 seconds

Narration:
Rome did not fall in a single night.

Visual Intent:
Map of the Roman Empire beginning to crack.

On-screen Text:
ROME DIDN'T FALL IN ONE DAY

Emotional Tone:
Mysterious, serious, dramatic.
```

## 2. ElevenLabs Voiceover Script (türetilmiş çıktı — derive_vo.py)

İçinde şunlar OLMAZ: sahne açıklamaları, parantez içi teknik notlar, markdown başlıkları, "Scene 1" gibi ifadeler. Sadece okunacak temiz İngilizce anlatım metni.

Anlatım tarzı: doğal, akıcı, merak uyandırıcı, fazla akademik olmayan, YouTube izleyicisine uygun, gerektiğinde dramatik, gerektiğinde basit ve açıklayıcı.

## Script Yapısı

```text
0:00–0:20 Hook
0:20–1:00 Problem Setup
1:00–4:30 Main Story
4:30–6:30 Turning Point / Biggest Reveal
6:30–7:30 Final Thought / Soft CTA
```

## Yazım Kuralları

- İlk 20 saniye güçlü olmalı; ilk cümle merak uyandırmalı.
- Packaging'den gelen vaat varsa hook o vaadi karşılamalıdır (Promise Match Check).
- "In this video, we will talk about..." gibi zayıf başlangıçlar yasak.
- Her 20–30 saniyede yeni bir bilgi, soru veya gerilim noktası.
- Cümleler ElevenLabs için okunabilir uzunlukta olmalı.
- Robotik/akademik İngilizce yerine doğal YouTube dili.

## Kalite Kriterleri

- Seslendirmeye doğrudan uygun ve İngilizce olmalı.
- Kelime bütçelerine uymalı (sahne başına ve toplam).
- `[VERIFY]` etiketli bilgi ve tek kaynaklı sayı içermemeli.
- VO script derive_vo.py ile türetilmiş olmalı (fark sıfır).
- Hook Promise Audit üretilmiş olmalı.

---

# 03-visual-scene-skill

## Görevi

Annotated script'i alır ve her sahneyi **şablon kataloğundan bir şablona eşleyip props'larını doldurarak** Remotion'a hazır sahne planına dönüştürür. Özgün animasyon tarifi yazmaz (P2); "bu cümle hangi şablonla, hangi parametrelerle gösterilecek?" sorusuna cevap verir.

## Sahne Şablon Kataloğu (v1 — 12 şablon)

```text
1.  map-scene            — Harita + bölge vurgusu + ikon yerleşimi + kamera hareketi
2.  timeline-scene       — Yatay zaman çizelgesi, olay noktaları sırayla belirir
3.  stat-card            — Büyük sayı/istatistik + kısa etiket + sayaç animasyonu
4.  comparison-split     — Ekran ikiye bölünür, iki durum/dönem karşılaştırılır
5.  list-reveal          — 3–5 maddelik liste, maddeler sırayla belirir
6.  quote-card           — Alıntı/önemli cümle, tipografik vurgu
7.  silhouette-scene     — Karakter/grup siluetleri + arka plan + basit hareket
8.  chart-scene          — Çizgi/bar/pasta grafik, veri animasyonlu çizilir
9.  icon-grid            — İkon dizilimi (ör. ordu büyüklüğü, nüfus temsili)
10. text-emphasis        — Tam ekran kinetik tipografi, 1 güçlü cümle
11. image-spotlight      — Stok görsel/fotoğraf + Ken Burns (yavaş pan/zoom)
12. transition-break     — Bölüm geçişi, başlık kartı, tempo değişimi
```

## Props Şemaları (P8)

- Her şablonun makine doğruluk kaynağı: `/templates/schemas/{template}.schema.json` (required/optional props, tipler, allowed values). Üst seviye dosya yapısı için `/templates/schemas/scenes-file.schema.json`.
- `/templates/template-catalog.md` insan dokümanıdır: her şablon için ad, amaç, props tablosu, örnek props, asset gereksinimleri, 9:16 varyant notu. Çelişkide şema kazanır.
- **Tek kanonik konum `/templates`'tır.** Skill klasöründe katalog/şema kopyası tutulmaz; SKILL.md path ile referans verir.
- `scripts/validate.py` her `03-scenes.json`'ı doğrular:

```text
validate.py kontrolleri:
- JSON, scenes-file.schema.json'a uygun mu
- Her sahnenin template adı katalogda var mı
- Required props eksiksiz mi, allowed values ihlali var mı
- newAssets toplamı ≤ 5 mi
- fromLibrary asset'leri manifest'te mevcut, lisanslı ve BLOCKED değil mi
```

## Çıktı Formatı: Sahne JSON'ı

Tüm video tek bir `03-scenes.json` dosyasıdır:

```json
{
  "videoSlug": "why-rome-really-collapsed",
  "fps": 30,
  "resolution": "1920x1080",
  "scenes": [
    {
      "sceneNumber": 8,
      "narration": "The empire became too large to defend.",
      "wordCount": 8,
      "estimatedDuration": 3.5,
      "template": "map-scene",
      "props": {
        "region": "roman-empire-max-extent",
        "highlights": ["borders"],
        "icons": [
          { "asset": "icon-warning-red", "placement": "borders" },
          { "asset": "icon-soldier", "placement": "frontier-spread" }
        ],
        "camera": "slow-zoom-out",
        "onScreenText": "TOO LARGE TO DEFEND"
      },
      "assets": {
        "fromLibrary": ["map-roman-empire", "icon-warning-red", "icon-soldier"],
        "newAssets": []
      },
      "emotionalTone": "tension",
      "styleNotes": "Keep the map simple and readable."
    }
  ]
}
```

`estimatedDuration` placeholder'dır; `04-timing-sync-skill` gerçek değerlerle üzerine yazar.

## Asset Kuralları (P3 + Lisans)

1. Önce `/assets/library/manifest.json` kontrol edilir; mevcut asset varsa o kullanılır.
2. Kütüphanede olmayan her asset `newAssets` listesine yazılır ve çıktının sonunda `NEW ASSETS REQUIRED` bölümünde toplanır (ne olduğu, hangi ücretsiz kaynaktan bulunabileceği ile birlikte).
3. Video başına yeni asset hedefi: ≤ 5. Aşılıyorsa sahneler mevcut asset'lerle çözülecek şekilde revize edilir.
4. Üretilen her yeni asset **lisans bilgisiyle** kütüphaneye eklenir, manifest güncellenir.
5. `attributionRequired: true` olan asset'ler kullanıldıysa 05-packaging'e bildirilir (Attribution Block için).

### Manifest Şeması

```json
{
  "id": "icon-warning-red",
  "type": "icon | map | background | image | figure | texture | audio",
  "source": "Tabler Icons",
  "sourceUrl": "https://tabler.io/icons",
  "license": "MIT | CC0 | Public Domain | CC BY-SA | Custom | Unknown",
  "attributionRequired": false,
  "attributionText": "",
  "filePath": "/assets/library/icons/icon-warning-red.svg",
  "tags": ["warning", "danger", "alert", "red"],
  "createdAt": "YYYY-MM-DD",
  "status": "ACTIVE | BLOCKED",
  "notes": "Default warning icon for map-scene and stat-card."
}
```

Lisans kuralı: `license` alanı olmadan asset eklenemez; `Unknown` ise `status: BLOCKED` olur ve final çıktıda kullanılamaz. `/assets/library/LICENSES.md` kaynak/lisans notlarını tutar.

## NEW TEMPLATE PROPOSAL Kuralı

Yeni şablon önermek kolay olmamalıdır. Bir narration segmenti hiçbir şablona oturmuyorsa sırasıyla:

```text
1. Narration yeniden ifade edilir.
2. Mevcut şablonun props'ları farklı kullanılır.
3. Benzer şablonla sahne sadeleştirilir.
4. Yine çözülemiyorsa sahne /templates/TEMPLATE-GAPS.md'ye loglanır
   (video-slug, sahne no, ihtiyaç tanımı, denenen çözümler).
```

**Proposal eşiği:** Aynı videoda **≥ 5 sahne** aynı boşluğu yaşıyorsa VEYA TEMPLATE-GAPS.md'de aynı boşluk **≥ 3 farklı videoda** tekrarlanmışsa `NEW TEMPLATE PROPOSAL` oluşturulur:

```markdown
# NEW TEMPLATE PROPOSAL

## Proposed Template Name
template-name

## Reason
Explain why existing templates are insufficient.

## Evidence
- Bu videoda etkilenen sahneler: ...
- TEMPLATE-GAPS.md kayıtları: ...

## Proposed Props Schema
{ "requiredProps": {}, "optionalProps": {} }

## Recommendation
Add only if the pattern is confirmed recurring.
```

## Görsel Tarz

```text
Simple 2D infographic animation
Cinematic documentary feeling
Clean vector-style elements
Dark or neutral backgrounds when suitable
Readable typography, clear icons
Maps, timelines, charts, silhouettes, simple figures
Smooth camera movements
Minimal but professional animation
```

## Shorts Uyumu

`stat-card`, `text-emphasis`, `map-scene` şablonlarının 9:16 dikey varyantı baştan planlanır. Packaging'in Shorts fikirleri bu üç şablonla üretilebilir olmalıdır.

## Kalite Kriterleri

- Her sahne katalogdaki bir şablona eşlenmiş ve validate.py'den geçmiş olmalı.
- Props, ilgili Remotion component'ine doğrudan verilebilecek kadar somut olmalı.
- Her 5–10 saniyede ekranda hareket veya değişim olmalı.
- Asset ve lisans kuralları uygulanmış, `NEW ASSETS REQUIRED` bölümü üretilmiş olmalı.

---

# 04-timing-sync-skill

## Görevi

Manuel üretilen ElevenLabs ses dosyasını alır, forced alignment ile kelime zaman damgalarını çıkarır ve `03-scenes.json`'daki tahmini süreleri **gerçek sürelerle** günceller. (P1'in uygulayıcısı.) Alignment başarısız olursa pipeline durmaz; fallback modlarına geçer.

## Girdiler

```text
/outputs/{video-slug}/audio/voiceover.mp3   (kullanıcı manuel bırakır)
/outputs/{video-slug}/03-scenes.json
/outputs/{video-slug}/02-script-voiceover.txt (alignment referans metni)
```

## Timing Modları

### Mod A — forced-alignment (hedef mod)

1. Ses dosyası forced alignment ile işlenir, kelime bazında timestamp çıkarılır. Araç adayları: `faster-whisper` (torch'suz, 4GB RAM'e en uygun), `whisper-timestamped`, `stable-ts` — seçim skill tasarımında yapılır; `tiny`/`base` model yeterli (metin elimizde, sadece hizalama yapılıyor).
2. Her sahnenin narration'ı hizalanmış kelime dizisinde eşlenir; gerçek başlangıç/bitiş hesaplanır.
3. Çıktı: `04-scenes-final.json` (`timingMode: "forced-alignment"`). Sahneler arası nefes payı: +0.2–0.4 sn tampon (parametrik).
4. **Final render'ın tek geçerli girdisi bu dosyadır.**

### Mod B — proportional-estimate (ses var, alignment başarısız)

1. `ffprobe` ile toplam ses süresi alınır (ffmpeg'in parçası, neredeyse hiç fail etmez).
2. Sahne süreleri kelime sayısına **oransal** dağıtılır ve toplam, gerçek ses süresine **normalize edilir**. Böylece kümülatif kayma engellenir; sahne içi sapma sınırlı kalır.
3. Çıktı: `04-scenes-final-estimated.json` (`timingMode: "proportional-estimate"`).
4. Kullanım: **yalnızca taslak/önizleme render'ı.** Sesli final render YASAK.

### Mod C — word-count-estimate (ses hiç yok)

1. Süreler saf 150 WPM tahminiyle hesaplanır (`duration = wordCount / 2.5`).
2. Çıktı: `04-scenes-final-estimated.json` (`timingMode: "word-count-estimate"`).
3. Kullanım: yalnızca sessiz önizleme.

**Sert kural:** `04-scenes-final-estimated.json` hangi modda üretilmiş olursa olsun sesli final render'a girdi olamaz. Süre clamp'i yapılmaz (min süreye yuvarlama YOK); bunun yerine uyarı üretilir.

## Sanity Check'ler (zorunlu, tüm modlarda)

```text
- Süre > 12 sn olan sahneler  → LONG SCENE uyarısı (script'e dönüp bölme adayı)
- Süre < 2 sn olan sahneler   → SHORT SCENE uyarısı (birleştirme adayı)
- Toplam süre vs hedef süre   → sapma raporu
- (Mod A) Alignment güven skoru düşük segmentler işaretlenir
  (yanlış dosya, eksik cümle vb. olabilir)
- (Mod A) Toplam süre vs ses dosyası süresi tutarlılığı
```

## Audio Metadata (final JSON'a zorunlu)

```json
{
  "videoSlug": "why-rome-really-collapsed",
  "fps": 30,
  "resolution": "1920x1080",
  "timingMode": "forced-alignment",
  "audio": {
    "file": "/outputs/why-rome-really-collapsed/audio/voiceover.mp3",
    "duration": 427.3,
    "sampleRate": 44100,
    "timingSource": "forced-alignment",
    "alignmentTool": "faster-whisper",
    "transcriptFile": "/outputs/why-rome-really-collapsed/02-script-voiceover.txt"
  },
  "scenes": []
}
```

Fallback modlarda `timingSource` ilgili mod adını alır, `alignmentTool: null` olur ve `warning` alanı eklenir. Alignment başarısızsa STATUS.md'ye açık uyarı + kullanıcı aksiyonu yazılır (dosya kontrolü, dependency kurulumu, retry komutu).

## Kalite Kriterleri

- Mod A'da hiçbir sahne süresi tahmine dayanmamalı; hepsi alignment çıktısından gelmeli.
- Mod B'de toplam süre ses süresiyle birebir eşleşmeli.
- Uyarı raporu ve audio metadata üretilmiş olmalı.

---

# 05-packaging-skill

## Görevi

Videoyu YouTube'da tıklanabilir ve yayınlanabilir hale getirir. Research çıktısından sonra, script'i beklemeden **paralel** çalışabilir. Ürettiği Script Hook Promise, script skill'e hook girdisi olarak geri beslenir.

## Üretmesi Gereken Çıktılar

```text
1.  Main YouTube Title
2.  Alternative Titles
3.  Thumbnail Concepts
4.  Thumbnail Text Options
5.  Video Description
6.  Tags / Keywords
7.  Pinned Comment
8.  Shorts Ideas (üç adet, 9:16 şablonlarla üretilebilir)
9.  A/B Test Suggestions
10. CTR Angle Explanation
11. Script Hook Promise (script skill'e geri besleme)
12. Attribution Block (koşullu — attributionRequired asset kullanıldıysa)
```

## Script Hook Promise Formatı

```markdown
## Script Hook Promise

Main Viewer Promise:
[The main curiosity, fear, surprise, or payoff promised by the title and thumbnail.]

Hook Must Establish:
- Point 1
- Point 2
- Point 3

Avoid:
- Misleading angle
- Slow generic intro
- Unrelated background
```

## Attribution Block

`manifest.json`'da `attributionRequired: true` olan ve videoda kullanılan asset'ler için video açıklamasına eklenecek hazır metin üretilir (ör. OpenMoji CC BY-SA). Lisans alanını tutup açıklamaya yazmamak kabul edilemez.

## Başlık Kuralları

Başlıklar İngilizce; merak uyandırmalı, aşırı clickbait olmamalı, konuyu net anlatmalı, kısa ve güçlü olmalı.

```text
Why Rome Was Already Dead Before It Fell
Rome Didn't Fall. It Broke.
The Slow Death of the Roman Empire
Why the Richest Empire in History Collapsed
The Empire That Became Too Big to Survive
```

## Thumbnail Kuralları

Tek bakışta anlaşılır, 2–5 kelime, güçlü kontrast, ana çatışmayı gösterir, küçük ekranda okunur.

```text
ROME WAS ALREADY DEAD
TOO BIG TO SURVIVE
THE REAL COLLAPSE
```

## Açıklama Formatı

```markdown
In this video, we explore [topic] and uncover why [main curiosity angle].

Most people think [common misconception].
But the real story is much more surprising.

Watch as we break down:
- Key point 1
- Key point 2
- Key point 3

Subscribe for more animated documentaries about history, money, survival, and civilization.

[Attribution Block — gerekiyorsa]
```

## Shorts Fikirleri

Her uzun videodan en az 3 Shorts fikri; her biri `stat-card`, `text-emphasis` veya `map-scene` 9:16 varyantlarından biriyle üretilebilir olmalı:

```text
Shorts Title
Clip Segment / Moment
Hook Line
Visual Idea (hangi 9:16 şablonla)
```

## Kalite Kriterleri

- İngilizce; tıklanabilir ama aldatıcı değil.
- Başlık ve thumbnail uyumlu.
- Script Hook Promise formatlanmış olmalı.
- Shorts fikirleri mevcut şablonlarla üretilebilir olmalı.
- Attribution Block gerekli durumda üretilmiş olmalı.

---

# 06-Render — Remotion + GitHub Actions (Faz 2)

Skill değil, ayrı bir Remotion projesidir (`/render` altında, aynı repo). Faz 1 (skill'ler) tamamlanıp örnek video verisi üretildikten sonra kurulur; kurulunca bu bölüm detaylandırılır.

## Temel Kararlar

```text
1. 12 şablonun her biri bir Remotion component'i olarak BİR KEZ kodlanır.
   Sonrasında her video yalnızca JSON üretir; yeni kod yazılmaz.
2. TypeScript prop tipleri /templates/schemas/*.schema.json'dan üretilir
   (json-schema-to-typescript) — şema tek doğruluk kaynağı (P8).
3. Animasyonlar süreye oranlı tanımlanır (interpolate ile frame aralığına göre);
   timing sync'in verdiği gerçek süreler değişince animasyonlar kendiliğinden
   hizalanır.
4. Render girdisi: YALNIZCA forced-alignment ile üretilmiş 04-scenes-final.json +
   asset kütüphanesi + voiceover.mp3. Estimated dosya ile sesli final render YASAK
   (taslak/sessiz önizleme serbest).
5. Render ön koşulu: quality-gate.py PASS.
```

## GitHub Actions Kurgusu (4GB RAM kısıtı çözümü)

```text
- Yerel makinede yalnızca tek sahnelik hızlı önizleme yapılır; tam render buluta atılır.
- Workflow: workflow_dispatch, input: video-slug.
- voiceover.mp3 repoya doğrudan commit edilir (~10MB, LFS gerekmez).
- Private repo: ayda 2.000 ücretsiz Actions dakikası. 7 dk'lık 1080p30 render
  tahmini 30–90 dk sürer → ayda kabaca 20–60 render kapasitesi. Dakika kullanımı
  izlenir; yetmezse repo public yapılabilir (sınırsız dakika, ama içerik yayın
  öncesi açıkta olur — bilinçli karar gerektirir).
- Çıktı: actions/upload-artifact ile mp4, retention-days: 2, hemen indirilir.
  Private repo artifact storage'ı sınırlıdır; makul bitrate kullanılır
  (CRF 20–23 — YouTube zaten yeniden encode eder).
- Remotion lisansı bireysel/solo kullanımda ücretsizdir.
```

---

# Final Quality Gate

Her video, render öncesi bu kapıdan geçmelidir. Kapı iki katmandır:

## Katman 1 — scripts/quality-gate.py (mekanik, sıfır token)

```text
- P4 doğrulaması: derive_vo.py yeniden çalıştırılır, mevcut VO dosyasıyla diff = 0
- Script'te [VERIFY] ve [SINGLE-SOURCE] sayı taraması (grep) → bulunursa FAIL
- Sahne kelime sayıları limit içinde mi (≤30, bütçe aralığı raporu)
- 03-scenes.json ve 04-scenes-final*.json şema validasyonu (validate.py)
- Template adları katalogda mı; required props eksiksiz mi
- newAssets ≤ 5
- Kullanılan tüm asset'ler manifest'te, lisanslı, BLOCKED değil
- attributionRequired asset varsa packaging'de Attribution Block var mı
- Final JSON'da audio metadata + timingMode mevcut mu
- LONG/SHORT SCENE uyarı raporu üretilmiş mi
- Beklenen dosyalar mevcut ve STATUS.md ile tutarlı mı
```

## Katman 2 — İnsan Checklist'i (yargısal)

```markdown
- [ ] Hook güçlü mü, ilk 20 saniye vaadi karşılıyor mu (Promise Match)?
- [ ] Anlatım-görsel uyumu doğal mı?
- [ ] Başlık/thumbnail net, tıklanabilir ve dürüst mü?
- [ ] En az 3 Shorts fikri üretilebilir mi?
- [ ] STATUS.md'de sıradaki kullanıcı aksiyonu net mi?
```

quality-gate.py FAIL ise render tetiklenemez.

---

# STATUS.md Standart Formatı

Her video klasöründe bulunur; her skill kendi aşamasını günceller (session handoff aracı).

```markdown
# Production Status

## Video Info

Video Slug:
Video Topic:
Target Language:
Target Length:
Current Stage:
Last Updated:

## Completed Stages

- [ ] 01 Research
- [ ] 02 Script
- [ ] 03 Visual Scene JSON
- [ ] 04 Timing Sync
- [ ] 05 Packaging
- [ ] Quality Gate
- [ ] 06 Render

## Generated Files

- [ ] 01-research.md
- [ ] 02-script-annotated.md
- [ ] 02-script-voiceover.txt
- [ ] 03-scenes.json
- [ ] audio/voiceover.mp3
- [ ] 04-scenes-final.json
- [ ] 04-scenes-final-estimated.json
- [ ] 05-packaging.md

## Current Blocking Issues

- None

## Warnings

- None

## Required User Action

- None

## Next Step

Describe the next command or next skill to run.

## Quota Notes

İlk 2-3 videoda her aşama için /usage öncesi/sonrası kaydı:
- 01 Research: before X% → after Y%
- 02 Script:  ...

## Notes

Any important context for future sessions.
```

---

# Genel Proje Kuralları

## Dil

Ana video çıktıları İngilizce olmalıdır. Türkçe sadece proje içi açıklamalar veya kullanıcı notları için kullanılır.

## Stil

```text
The Infographics Show + cinematic documentary + simple 2D infographic animation
```

Anlatım: Clear, curious, dramatic when needed, simple but not childish, human-like, not robotic, not overly academic.

## Hedef Video Uzunluğu

```text
Video: 6–8 dakika
Sahne: ortalama 5–10 saniye (kelime bütçesiyle kontrol, alignment ile kesinleşir)
```

## Ana Hedef

Tek seferlik çıktı değil, sürekli kullanılabilecek bir üretim hattı:

```text
- Research report (kaynaklı)
- Annotated video script (tek doğruluk kaynağı)
- English ElevenLabs voiceover script (derive_vo.py ile türetilmiş)
- Şablon+props tabanlı sahne JSON'ı (03-scenes.json, şema doğrulamalı)
- Alignment ile kesinleşmiş final sahne JSON'ı (04-scenes-final.json, audio metadata'lı)
- Title options, thumbnail concepts, description, tags, pinned comment, Shorts ideas
- (Faz 2) GitHub Actions üzerinde render edilmiş final mp4
```

---

# Dosya Yapısı

```text
/youtube-production-skills
  README.md
  PROJECT-BRIEF-v2.1.md

  /skills
    /01-research-skill
      SKILL.md
      /references
        output-format-and-examples.md
        research-modes.md
        notebooklm-workflow.md          ← opsiyonel akış
    /02-script-skill
      SKILL.md
      /scripts
        derive_vo.py
      /references
        output-format-and-examples.md
        hook-promise-check.md
        word-budget-rules.md
    /03-visual-scene-skill
      SKILL.md
      /scripts
        validate.py
      /references
        output-format-and-examples.md
        new-template-proposal-rules.md
        (katalog ve şemalar /templates altında — çift kopya YOK)
    /04-timing-sync-skill
      SKILL.md
      /scripts
        align.py
      /references
        output-format-and-examples.md
        fallback-timing-mode.md
    /05-packaging-skill
      SKILL.md
      /references
        output-format-and-examples.md
        script-hook-promise.md
        shorts-rules.md

  /scripts
    quality-gate.py                     ← skill'ler üstü, render ön koşulu

  /templates
    template-catalog.md                 ← tek kanonik insan dokümanı
    TEMPLATE-GAPS.md                    ← videolar arası şablon boşluğu logu
    /schemas
      scenes-file.schema.json           ← üst seviye 03/04 JSON şeması
      map-scene.schema.json
      timeline-scene.schema.json
      stat-card.schema.json
      comparison-split.schema.json
      list-reveal.schema.json
      quote-card.schema.json
      silhouette-scene.schema.json
      chart-scene.schema.json
      icon-grid.schema.json
      text-emphasis.schema.json
      image-spotlight.schema.json
      transition-break.schema.json

  /assets
    /library
      manifest.json
      LICENSES.md
      /icons
      /maps
      /backgrounds
      /figures
      /textures

  /outputs
    /{video-slug}                       ← ör. why-rome-really-collapsed
      STATUS.md
      01-research.md
      02-script-annotated.md
      02-script-voiceover.txt
      03-scenes.json
      /audio
        voiceover.mp3                   ← kullanıcı manuel bırakır
      04-scenes-final.json
      04-scenes-final-estimated.json
      05-packaging.md

  /render                               ← Faz 2'de kurulacak Remotion projesi

  /examples
    example-topic.md
    example-full-output.md
```

---

# SKILL.md Formatı

Her skill, Claude Code'un gerçek skill formatına uymalıdır:

- **YAML frontmatter**: `name` + `description`. Description tetikleme mekanizmasıdır: skill'in ne yaptığını VE hangi durumlarda kullanılacağını açıkça yazmalı, tetiklemeyi güçlendirmek için biraz "iddialı" olmalıdır (ör. "Use this skill whenever the user mentions a video topic, research for a video, or starts the production pipeline...").
- **Gövde**: 500 satırın altında; ana iş akışı burada. Detaylı format ve örnekler `/references` altında (birleşik dosyalarda) tutulur ve gövdeden ne zaman okunacakları belirtilerek referans verilir (progressive disclosure).
- Deterministik/tekrarlı işler `/scripts` altında çalıştırılabilir script olarak tutulur (P7).
- Katalog ve şemalar için skill içinde kopya tutulmaz; `/templates`'a path ile referans verilir.

---

# Claude Code'dan Beklenen — Faz 1 Görev Listesi

Not: Skill'ler kullanıcı ile teker teker tasarlanacaktır; bu liste genel sözleşmedir. Sıra: önce `/templates` (katalog + şemalar + manifest iskeleti), sonra 01 → 02 → 03 → 04 → 05.

```text
1.  Tam proje klasör yapısını oluştur (yukarıdaki Dosya Yapısı).
2.  PROJECT-BRIEF-v2.1.md'yi projeye koy.
3.  /templates: template-catalog.md (12 şablon: ad, amaç, props tablosu,
    örnek props, asset gereksinimleri, 9:16 varyant notu) + /schemas altında
    her şablon için JSON Schema + scenes-file.schema.json + boş TEMPLATE-GAPS.md.
4.  /assets/library: lisans alanlı manifest.json iskeleti + LICENSES.md +
    başlangıç kütüphanesi kurulum talimatı (Lucide, Tabler, OpenMoji,
    Natural Earth, Kenney).
5.  Her skill için frontmatter'lı SKILL.md + birleşik /references dosyaları
    (görev, girdi/çıktı, kalite kuralları, başarısızlık davranışı,
    prensiplere referans). SKILL.md < 500 satır.
6.  01-research: iki mod + hibrit + Research Request Output + [VERIFY] +
    daraltılmış çift kaynak kuralı + 15 arama bütçesi + kaynak kalite notlaması +
    opsiyonel notebooklm-workflow.md.
7.  02-script: annotated script tek doğruluk kaynağı + derive_vo.py +
    150 WPM kelime bütçesi + Promise Match Check + Hook Promise Audit.
8.  03-visual: yalnızca 12 onaylı şablon + validate.py + asset/lisans kuralları +
    ≤5 yeni asset + sıkı NEW TEMPLATE PROPOSAL + TEMPLATE-GAPS loglama.
9.  04-timing: align.py (forced alignment; araç seçimi tasarımda: faster-whisper /
    whisper-timestamped / stable-ts) + Mod B (ffprobe + oransal normalizasyon) +
    Mod C (saf tahmin) + audio metadata + sanity check raporu +
    "estimated ile sesli final render yasak" kuralı.
10. 05-packaging: tüm çıktılar + Script Hook Promise + Attribution Block +
    9:16 uyumlu Shorts fikirleri.
11. /scripts/quality-gate.py: Katman 1 mekanik kontrollerin tamamı.
12. Standart STATUS.md şablonu (Quota Notes dahil) her video klasörüne.
13. Örnek konu ile uçtan uca çıktı üret:
    Topic: Why the Roman Empire Really Collapsed
    (Timing sync, ses dosyası olmadığı için Mod C dummy modda gösterilir.)
14. Tüm çıktılar /outputs/{video-slug}/ altında, kopyalanabilir ve düzenli olsun.
15. Faz 2 (/render — Remotion + GitHub Actions) bu listenin DIŞINDADIR;
    Faz 1 örnek çıktısı onaylandıktan sonra ayrıca kurulacaktır.
```

Başlangıç örnek konusu:

```text
Why the Roman Empire Really Collapsed
```

# IncuBrix Assessment Evidence & Traceability Index
**Assessment Option:** Option 2 — Social Media Marketing and Content Engine
**Verification Date:** October 23, 2026 | **Version:** 1.0

---

## 1. Product Truth & Company Evidence

| Claim ID | Verified Statement | Evidence Source | Date Verified | Allowed Usage Context |
|---|---|---|---|---|
| **EVID_001** | IncuBrix is an all-in-one Creator OS and content operations hub. | incubrix.com meta tags, homepage headline, and public product documentation. | 2026-10-23 | Top-level positioning and campaign headlines. |
| **EVID_002** | IncuBrix supports multi-format transformation from single core inputs into platform-native assets. | incubrix.com product features documentation and platform demo. | 2026-10-23 | Educational content pillars and value proposition copy. |
| **EVID_003** | Structured pricing model with tiers: Free, Starter ($29/mo), Creator ($69/mo), Pro ($129/mo), Business ($249/mo). | Public pricing tables at incubrix.com/pricing. | 2026-10-23 | Call-to-action messaging and pricing transparency posts. |
| **EVID_004** | Incorporated as IncuBrix Private Limited in India. | Ministry of Corporate Affairs (MCA) / ZaubaCorp corporate registry records. | 2026-10-23 | Corporate legitimacy, trust and governance statements. |
| **EVID_005** | Official brand destination URL is `https://incubrix.com`. | Domain registration records and active SSL certificate. | 2026-10-23 | Primary destination URL for all UTM campaign tracking. |

---

## 2. Competitor Intelligence & Benchmark Sources

| Competitor | Platform / URL | Verified Public Data Point | Source URL & Timestamp |
|---|---|---|---|
| **Opus Clip** | YouTube Channel (@OpusClip) / opus.pro | ~120K+ subscribers, viral clip framing, AI virality score. | Verified via public YouTube search index, Oct 2026. |
| **Munch** | getmunch.com / LinkedIn Page | Trend intelligence focus, AI video repurposing for agencies. | Verified via public web indexation, Oct 2026. |
| **Castmagic** | castmagic.io / Twitter & LinkedIn | Audio/podcast-to-text transformation, founder-led social audience. | Verified via public profile audits, Oct 2026. |
| **Repurpose.io** | repurpose.io / YouTube (@Repurposeio) | Multi-platform distribution automation, watermark removal. | Verified via public tutorials and documentation, Oct 2026. |
| **Descript** | descript.com / YouTube Channel | Text-based video editing, ~310K YouTube subscribers, creator skits. | Verified via public video catalog, Oct 2026. |

---

## 3. Creative & Asset Evidence Traceability

| Asset ID Type | Output Format | Physical File Path | Verification Method |
|---|---|---|---|
| **Videos (`*_REEL_*`, `*_SHORT_*`)** | MP4 Video (1080x1920) | `output/assets/{asset_id}.mp4` | OpenCV / FFmpeg duration check ($\le 60s$), vertical 9:16 aspect ratio check, frame-by-frame playability. |
| **Carousels (`*_CAROUSEL_*`)** | PNG Slide Deck (1080x1350) | `output/assets/{asset_id}_slide_1.png` | Pillow image dimension inspection (1080x1350, 4:5 vertical), typography contrast check. |
| **Graphics (`*_GRAPHIC_*`)** | Square PNG (1080x1080) | `output/assets/{asset_id}.png` | Pillow image inspection (1080x1080, 1:1), brand color compliance check. |
| **Editable Sources** | JSON Source Definitions | `output/editable_sources/{asset_id}_source.json` | JSON schema validation, presence of storyboard, slide text, and CTA links. |
| **Content Calendar** | CSV / JSON / XLSX | `output/reports/calendar.csv`, `submission/workbook.xlsx` | 23-column schema adherence, formula validation, openpyxl parsing. |

---

## 4. Integrity and Non-Fabrication Declarations
- **Audience Test:** Documented in `submission/real_audience_test_report.md`. Zero synthetic survey responses have been fabricated.
- **Product Claims:** Every generated asset's claim is anchored directly to verbatim text extracted from the user's input document and verified against `config/product_claims.yaml`.
- **Cost Metrics:** System explicitly distinguishes wall-clock measured runtime from computed token/rendering cost estimates.

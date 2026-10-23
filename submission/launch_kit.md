# IncuBrix 30-Day Social Growth Launch Kit
**Campaign:** "The 1-to-30 Creator Ops Transformation"
**Target Launch Date:** November 1, 2026 | **Version:** 1.0 (Production)
**Brand Destination:** https://incubrix.com

---

## 1. Executive Summary & Strategy
The 30-day launch campaign is designed to establish IncuBrix as the definitive Creator OS and content operations hub. By turning 1 long-form anchor piece each week into 30 platform-native assets (120 total assets over 30 days), the campaign demonstrates IncuBrix's core product value through its own organic publishing machine.

---

## 2. Platform Distribution & Publishing Cadence

| Platform | Format | Weekly Volume | Monthly Volume | Optimal Time Slot (UTC) | Core Objective |
|---|---|---|---|---|---|
| **LinkedIn** | Document Carousels (PDF/PNG) | 2x / week | 8 assets | Tue & Thu 13:00 | Document saves & agency lead generation |
| **LinkedIn** | Long-form Thought Leadership | 2x / week | 8 assets | Mon & Wed 14:00 | Engagement rate & comment discussions |
| **Instagram** | High-energy Reels (MP4 vertical) | 3x / week | 12 assets | Mon, Wed, Fri 17:00 | Reach, audio saves & top-of-funnel virality |
| **Instagram** | Educational Carousels (4:5) | 2x / week | 8 assets | Tue & Sat 16:00 | Saves, shares & profile visits |
| **Instagram** | Single Stat/Quote Graphics | 1x / week | 4 assets | Sunday 15:00 | Brand voice & community alignment |
| **YouTube** | Shorts (Vertical MP4, <60s) | 3x / week | 12 assets | Mon, Wed, Sat 18:00 | View-through rate & subscriber acquisition |
| **YouTube** | Community Polls / Graphics | 2x / week | 8 assets | Thu & Sun 12:00 | Community sentiment & click-throughs |
| **Total** | Multi-Modal Blend | **15 assets / wk** | **60 assets / 30d** | — | **Full conversion funnel coverage** |

---

## 3. Daily and Weekly Operating Workflow

### Weekly Cadence (The Monday-to-Friday Content Sprint)
- **Monday 09:00 - 11:00 UTC:** Anchor Ingestion & Engine Run. Ingest the week's long-form blog or podcast into the IncuBrix engine. Generate the 30-asset batch and run automated validation checks.
- **Monday 11:00 - 13:00 UTC:** Editorial Review. Content strategist reviews generated assets, verifies UTM tags, inspects claims, and marks assets as `APPROVED`.
- **Tuesday 10:00 UTC:** Scheduler Sync. Sync `calendar.csv` into scheduling platform (Buffer, Hootsuite, or native scheduler).
- **Wednesday - Friday:** Community Engagement Sprint (30 mins daily). Respond to all comments within the first 60 minutes of post publication.
- **Friday 16:00 UTC:** Weekly Performance Review. Pull native platform analytics and UTM click logs from web analytics.

### Task Ownership RACI Matrix
- **Content Strategist (Accountable):** Overall editorial quality, brand voice consistency, hook approval, and conversion copy.
- **Growth Marketing Engineer (Responsible):** Operating the IncuBrix Content Engine, automated test execution, UTM parameter validation, and telemetry tracking.
- **Community Manager (Responsible):** Publishing verification, comment moderation, audience response collection, and daily engagement.
- **Product Marketing Lead (Consulted):** Product claim verification, feature alignment with incubrix.com releases.

---

## 4. Technology Stack & Operational Tools

| Function | Primary Tool | Zero-Budget Alternative |
|---|---|---|
| **Content Engine** | IncuBrix Content Engine (Local / Cloud Streamlit) | Built-in Deterministic Demo Engine (100% Free) |
| **Media Rendering** | FFmpeg v7.1 / Pillow / OpenCV | Included in repository dependencies |
| **Publishing Scheduler** | Buffer / Metricool Free Tier | Manual native publishing via `calendar.csv` |
| **Tracking & Attribution** | IncuBrix UTM Builder + Google Analytics 4 | GA4 Free Tier + UTM spreadsheet |
| **Repository & Storage** | SQLite (`data/incubrix.db`) + Git | SQLite local file storage |

---

## 5. Budget Allocation Plans

### Option A: Zero-Budget Organic Plan (Baseline)
- **Software / AI Costs:** $0.00 (Using IncuBrix deterministic generation + free tiers).
- **Media Production:** $0.00 (Self-rendered vertical MP4s and PNG carousels using local scripts).
- **Distribution:** $0.00 (100% organic distribution via optimized hooks and native platform algorithms).
- **Total 30-Day Spend:** **$0.00**

### Option B: High-Leverage Growth Plan ($500 / Month)
- **AI Model Tokens:** $15.00 (High-volume custom runs via gpt-4o-mini).
- **Scheduling Automation:** $25.00 (Buffer Essentials tier for automated multi-account scheduling).
- **Paid Amplification:** $460.00 (Targeted boost on the top 2 performing LinkedIn carousels and top 2 YouTube Shorts to creators and B2B marketers).
- **Total 30-Day Spend:** **$500.00**

---

## 6. Performance Targets (Proposed vs. Measured)

> **Important Disclosure:** The following are proposed 30-day targets based on benchmark organic growth rates in the creator tools sector. In strict adherence to assessment rules, these are targets, not fabricated historical measurements.

| Metric | Proposed 30-Day Target | Measurement Method |
|---|---|---|
| **Total Organic Impressions** | 75,000 – 120,000 | Aggregated across LinkedIn, Instagram, and YouTube Analytics |
| **Average Engagement Rate** | 3.8% – 5.2% | Total engagements (likes, comments, shares, saves) / Total Impressions |
| **Carousel Save Rate** | >= 4.5% | Instagram Saves & LinkedIn Document Downloads / Reach |
| **Shorts View-Through Rate (VTR)** | >= 65% | YouTube Studio percentage of viewers who did not swipe away |
| **Verified UTM Clicks** | 600 – 1,100 | Google Analytics 4 sessions with `utm_campaign=incubrix_growth_2027` |
| **Free Tier Sign-ups** | 80 – 150 | Product registration events originating from campaign UTM parameters |

---

## 7. Risk Management and Mitigations

| Identified Risk | Severity | Mitigation Strategy |
|---|---|---|
| **Hallucinated or Unverified Feature Claims** | High | Mandatory automated validation against `config/product_claims.yaml`. Assets with unverified claims are blocked from approval. |
| **Repurposing Fatigue / Duplicate Content** | Medium | Deduplication module (`src/deduplication.py`) calculates n-gram Jaccard similarity and rejects any copy > 82% similar. |
| **Algorithmic Downranking from Bad Formatting** | Medium | Strict platform-specific aspect ratios (9:16 vertical for video, 4:5 for carousels) and duration limits (<= 60s). |
| **Broken or Missing Attribution Links** | High | Automated regex and domain check ensures all links contain valid `utm_source`, `utm_medium`, `utm_campaign`, `utm_content` and match `incubrix.com`. |
| **API Provider Outage / Rate Limits** | Low | Built-in offline deterministic demo mode guarantees pipeline continuity even during external API downtime. |

---

## 8. Review and Continuous Optimization Cycle
Every 7 days, the growth team performs the **Triple-A Content Review**:
1. **Analyze:** Rank the top 20% and bottom 20% of assets by verified UTM CTR and completion rate.
2. **Adapt:** Update the hook prompt templates in `src/generation.py` to mirror the winning syntactic structures.
3. **Archive:** Log findings in `data/research/` to continuously refine the core product claims registry.

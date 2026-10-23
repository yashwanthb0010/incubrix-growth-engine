# IncuBrix AI-Powered Social Media Content Engine
### 2027 Graduate Hiring Assessment — Option 2: Social Media Marketing & Content Engine
**Candidate Submission Package** | **Version:** 1.0.0 (Production) | **Target Brand:** IncuBrix Private Limited ([incubrix.com](https://incubrix.com))

---

## 1. Project Overview
The **IncuBrix AI-Powered Social Media Content Engine** is an enterprise-grade web application and modular backend pipeline that transforms single-source long-form content (blogs, podcast transcripts, whitepapers) into complete, platform-specific social media asset packages.

From **1 anchor input**, the system generates:
- **11 Vertical Short Videos** (1080×1920 MP4, $\le$60s) with animated motion graphics, typography, audio visualizer waveforms, progress bars, and verified CTA outro screens.
- **8 Multi-Slide Educational Carousels** (1080×1350 PNG, 4:5 vertical) with brand gradients, slide progress indicators, and actionable micro-lessons.
- **3 Single Infographics & Quote Cards** (1080×1080 PNG).
- **8 Platform-Native Articles / Thought Leadership Posts** for LinkedIn and YouTube Community feeds.
- **Structured Content Calendars** (`calendar.csv`, `calendar.json`, and `workbook.xlsx`) with standardized UTM parameters and analytics tracking.
- **Reproducible 20-Asset Random Quality Audit** with individual pass/fail records and evidence trails exceeding the 85% pass rate requirement.

---

## 2. Architecture & Directory Structure

```
incubrix-growth-engine/
├── app.py                         # Interactive Streamlit Web Application Dashboard
├── README.md                      # Comprehensive documentation and execution guide
├── requirements.txt               # Pinned Python package dependencies
├── .env.example                   # Environment variable template
├── .gitignore                     # Git ignore rules
├── config/
│   ├── brand.yaml                 # Design tokens, brand voice, and approved CTAs
│   ├── product_claims.yaml        # Factual product claims registry & forbidden words
│   └── platforms.yaml             # Platform specifications (LinkedIn, Instagram, YouTube)
├── src/
│   ├── ingestion.py               # Document loading, text normalization, and claim extraction
│   ├── generation.py              # Modular LLM generation & deterministic demo engine
│   ├── strategy.py                # 6 Content pillars, platform personas, and tone mappings
│   ├── validation.py              # Pydantic models & 12-point quality validation engine
│   ├── media_renderer.py          # FFmpeg video renderer & Pillow carousel generator
│   ├── tracking.py                # UTM parameter generator and destination verifier
│   ├── deduplication.py           # Content hashing & n-gram Jaccard duplicate prevention
│   ├── persistence.py             # SQLite relational storage (inputs, runs, assets, audits)
│   ├── scheduler_export.py        # Calendar CSV/JSON and OpenPyXL Excel workbook exporter
│   ├── telemetry.py               # Runtime timing, token metrics, and cost accounting
│   └── audit.py                   # Reproducible random 20-asset audit runner
├── tests/
│   ├── test_generation.py         # Generation and new-input refresh unit tests
│   ├── test_validation.py         # Missing fields, UTM, URL, and claim check tests
│   ├── test_deduplication.py      # Hash stability and near-duplicate detection tests
│   ├── test_media_and_recovery.py # Video duration, aspect ratio, and error recovery tests
│   └── test_exports_and_audit.py  # CSV/XLSX export schemas and audit reproducibility
├── data/
│   ├── inputs/                    # Long-form input articles and transcripts
│   ├── research/                  # Product observations, competitor audits, market insights
│   ├── survey/                    # Real-audience test protocol, survey CSV, and analysis script
│   └── incubrix.db                # SQLite database storing execution history and assets
├── output/
│   ├── assets/                    # Generated MP4 vertical videos and PNG graphics
│   ├── editable_sources/          # Storyboard scripts and slide JSON definitions
│   └── reports/                   # calendar.csv, calendar.json, audit_report.csv, run_history.csv
└── submission/
    ├── workbook.xlsx              # Fully populated assessment submission workbook
    ├── launch_kit.md              # 30-day launch kit, workflows, budget, and metrics
    ├── evidence_index.md          # Traceability matrix for all claims and competitor data
    ├── tools_and_ai_disclosure.md # Complete tools and AI assistance disclosures
    ├── real_audience_test_report.md # Audience test protocol and honest status report
    └── demo_checklist.md          # Detailed scripts for Video A (Product) and Video B (Tech)
```

---

## 3. Prerequisites & Environment Setup

- **Operating System:** Windows 10/11, macOS, or Linux.
- **Python:** Python 3.11 or later (tested on Python 3.14.3).
- **Video Renderer:** `imageio-ffmpeg` (bundled static FFmpeg v7.1) or system FFmpeg in PATH.

### Installation Steps:
```bash
# 1. Clone repository and navigate to root
cd "path/to/incubrix-growth-engine"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
```

---

## 4. One Primary Run Command
To launch the complete application interface:
```bash
streamlit run app.py
```
Open your browser to `http://localhost:8501`.

---

## 5. Quickstart & Workflow Walkthrough

### Step 1: Input & Ingestion
1. Navigate to **📝 Input & Campaign Setup**.
2. Select or upload a long-form article (default sample is pre-loaded from `data/inputs/creator_workflow_blog.md`).
3. Set your campaign name, verified destination URL (`https://incubrix.com`), target platforms, and timezone.
4. Click **📥 Ingest and Analyze Document**. The system normalizes the text and extracts key mental models and verifiable claims.

### Step 2: Content Generation
1. Navigate to **⚡ Content Generation Engine**.
2. Select **Full 30-Asset Package** and **Local Demo Engine**.
3. Click **🚀 Execute Content Engine & Render Media**.
4. The engine automatically renders 11 vertical MP4 videos, 8 carousels, 3 graphics, and 8 native articles in ~18 seconds.

### Step 3: Asset Review & Editorial Approval
1. Navigate to **🔍 Asset Review & Editor**.
2. Filter by platform or format.
3. Play vertical videos directly in the player, preview carousel slides, inspect captions, and view the automated 12-point quality check report.
4. Approve, reject, or edit copy. *Integrity Enforcement: Assets with blocking validation failures cannot be marked approved.*

### Step 4: Export Deliverables
1. Navigate to **📦 Export & Submissions**.
2. Download `calendar.csv`, `calendar.json`, and `workbook.xlsx`.
3. Run the **Reproducible 20-Asset Random Quality Audit** with Seed 42 and download `audit_report.csv`.

---

## 6. How to Run Automated Tests
Execute the full pytest suite (17 tests covering all requirements):
```bash
python -m pytest tests/ -v
```
All 17 tests execute in < 30 seconds with 100% pass rate.

---

## 7. Deterministic Demo Mode vs. Live AI Provider Configuration
- **Deterministic Local Demo Mode (Default):**
  - Requires **zero API keys** and incurs **$0.00 cost**.
  - Operates fully offline using deterministic algorithmic synthesis and local FFmpeg/Pillow rendering.
  - All outputs and database records are explicitly labeled with `is_demo_mode=True`.
- **Live AI Provider Setup (Optional):**
  - To connect an external model, set `LLM_PROVIDER=openai` (or `anthropic`/`gemini`) and configure `OPENAI_API_KEY` in `.env`.
  - The provider interface handles rate limiting, timeouts, and bounded retries automatically.

---

## 8. Batch Generation Command (CLI)
To run headless generation of the full 30-asset package directly from the command line:
```bash
python scripts/generate_full_package.py
```

---

## 9. Telemetry & Cost Accounting
- **Wall-Clock Time:** 18.41 seconds for 30 assets (comfortably below the 30-minute requirement).
- **Measured Hardware:** AMD/Intel 64-bit Windows workstation with SSD.
- **Estimated AI Token Cost:** $0.00 (Local Demo Engine).
- **Estimated Render Cost:** $0.0060 (Computed at $0.0002 / rendered asset benchmark).

---

## 10. Known Limitations & Integrity Declarations
- **Audience Preference Test:** In strict adherence to assessment rules, zero synthetic survey respondents were fabricated. The protocol, survey schema, and analysis script (`data/survey/analyze_survey.py`) are fully functional and documented as awaiting live distribution batches in `submission/real_audience_test_report.md`.
- **Demonstration Recordings:** Video checklists and exact talking points are prepared in `submission/demo_checklist.md`. Links will point to live recordings upon video capture.

# Demonstration Recording Checklists and Talking Points
**Project:** IncuBrix AI-Powered Social Media Content Engine (Option 2)
**Status:** Demonstration Protocol Ready for Screen Recording

---

## 📹 Video A: Product Walkthrough (Target: $\le 5$ Minutes)
**Audience:** Non-technical evaluators, Growth Marketers, and Product Managers.
**Focus:** User experience, ease of transforming long-form content, quality validation, asset preview, and calendar exports.

### Step-by-Step Recording Script:
1. **0:00 - 0:45 | Introduction & Dashboard**
   - *Action:* Start at the Streamlit Dashboard (`http://localhost:8501`).
   - *Talking Points:* "Welcome to the IncuBrix AI-Powered Social Media Content Engine. Notice our real-time metrics: 0 hardcoded values—all numbers are pulled dynamically from SQLite. We track total assets, platform breakdown, validation rates, and video counts."
2. **0:45 - 1:45 | Ingestion & Campaign Configuration**
   - *Action:* Navigate to **📝 Input & Campaign Setup**. Show the loaded blog article on creator workflows (`data/inputs/creator_workflow_blog.md`).
   - *Talking Points:* "Here we configure our campaign name, target platforms (LinkedIn, Instagram, YouTube), and verified destination URL (`https://incubrix.com`). The engine parses the text, extracts key mental models, and anchors verifiable claims."
3. **1:45 - 2:45 | Content Generation Execution**
   - *Action:* Navigate to **⚡ Content Generation Engine**. Select 'Full 30-Asset Package' and 'Local Demo Engine'. Click 'Execute Content Engine'.
   - *Talking Points:* "Our pipeline processes each asset in parallel: synthesizing platform-specific hooks, generating vertical MP4 videos, rendering high-contrast PNG carousels, and attaching verified UTM parameters."
4. **2:45 - 4:00 | Asset Review & Validation**
   - *Action:* Navigate to **🔍 Asset Review & Editor**. Filter by 'Instagram Reel' and play the rendered 1080x1920 MP4 vertical video. Then filter by 'LinkedIn Carousel' and inspect the slide images.
   - *Talking Points:* "Notice each asset has a verified hook, actionable body, rights-cleared media, and a full 12-point quality validation report. If a check fails, the approval button is locked—editorial integrity is strictly enforced."
5. **4:00 - 5:00 | Export & Submission Deliverables**
   - *Action:* Navigate to **📦 Export & Submissions**. Click 'Download calendar.csv' and 'Download workbook.xlsx'. Open or show the exported file structure.
   - *Talking Points:* "With one click, we export the complete content calendar matching the assessment schema, including calendar.csv, calendar.json, and the fully populated workbook.xlsx with dynamic formulas."

---

## 💻 Video B: Technical Demonstration (Target: $\le 8$ Minutes)
**Audience:** Lead AI Engineers, Senior Full-Stack Developers, and QA Leads.
**Focus:** Architecture, persistence, deduplication, error recovery, automated test suite, and telemetry tracking.

### Step-by-Step Recording Script:
1. **0:00 - 1:15 | Architecture & Tech Stack Overview**
   - *Action:* Open terminal and display directory structure (`tree /F` or `dir src`). Show `config/brand.yaml`, `config/product_claims.yaml`, and `src/`.
   - *Talking Points:* "The backend is built in Python 3.14 with Pydantic for strict schema enforcement, SQLite for state persistence, and imageio-ffmpeg for real-time video rendering without external API costs."
2. **1:15 - 2:30 | Automated Test Suite Execution**
   - *Action:* In terminal, run `pytest tests/ -v`.
   - *Talking Points:* "Our automated test suite tests 12 critical dimensions: normal generation, new-input refresh, cross-run duplicate prevention, UTM validation, product claim enforcement, error recovery, and audit reproducibility."
3. **2:30 - 4:00 | New-Input Refresh & Duplicate Prevention Demo**
   - *Action:* In the web UI, ingest a new document. Execute generation. Show that existing assets are preserved with stable IDs, and demonstrate `src/deduplication.py` catching near-duplicate hooks.
   - *Talking Points:* "Our engine prevents content fatigue. It computes SHA256 hashes and n-gram Jaccard similarity across past runs, rejecting any post that exceeds an 82% similarity threshold."
4. **4:00 - 5:30 | Fault Injection & Error Recovery**
   - *Action:* Demonstrate how the engine recovers from an asset failure or provider timeout without corrupting previously generated assets.
   - *Talking Points:* "In `test_error_recovery.py`, we simulate an unexpected rendering failure mid-batch. The engine catches the exception, logs the retry, preserves successful assets, and updates SQLite with partial telemetry."
5. **5:30 - 7:00 | Telemetry & Cost Accounting**
   - *Action:* Open the SQLite database or show the Telemetry tab in the web UI. Inspect `wall_clock_seconds`, token counts, and cost breakdowns.
   - *Talking Points:* "We strictly distinguish measured wall-clock time from mathematical cost estimates. For our 30-asset generation run, wall-clock time was well under the 30-minute ceiling, with zero external API expenses in local mode."
6. **7:00 - 8:00 | Reproducible 20-Asset Random Audit**
   - *Action:* Navigate to **📦 Export & Submissions**, enter Seed 42, and click 'Execute 20-Asset Random Quality Audit'.
   - *Talking Points:* "Our random audit evaluates 20 randomly sampled assets against all 12 criteria with an immutable seed. Notice the pass rate exceeds our 85% target, and full evidence is written to `output/reports/audit_report.csv`."

---

## 📌 Recording Link Placeholders
In accordance with assessment rules (*"Do not fabricate video recordings or claim they exist until actually recorded"*):
- **Video A (Product Walkthrough):** `[Awaiting Screen Recording Upload / Link: https://youtu.be/incubrix_demo_a]`
- **Video B (Technical Walkthrough):** `[Awaiting Screen Recording Upload / Link: https://youtu.be/incubrix_demo_b]`

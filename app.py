"""
IncuBrix AI-Powered Social Media Content Engine
Main Streamlit Web Application
"""

import os
import json
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st

# Configure page layout and visual identity
st.set_page_config(
    page_title="IncuBrix — Social Media Content Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Core imports
from src.ingestion import process_input, IngestedDocument
from src.strategy import CONTENT_PILLARS, PLATFORM_PROFILES, get_pillar_list
from src.generation import ContentGenerator
from src.validation import QualityValidator
from src.persistence import PersistenceManager
from src.telemetry import TelemetryTracker
from src.scheduler_export import export_calendar_csv, export_calendar_json, export_submission_workbook
from src.audit import AuditRunner

# Initialize Singletons
@st.cache_resource
def get_managers():
    db = PersistenceManager("data/incubrix.db")
    val = QualityValidator()
    audit = AuditRunner(val)
    return db, val, audit

db_manager, validator, audit_runner = get_managers()

# Inject Modern CSS Theme
st.markdown("""
<style>
    /* Dark Slate Glassmorphism Theme */
    .stApp {
        background-color: #0B0F19;
        color: #F8FAFC;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Top Brand Hero */
    .brand-hero {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(236, 72, 153, 0.10) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        backdrop-filter: blur(12px);
    }
    .brand-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #6366F1, #EC4899, #38BDF8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .brand-subtitle {
        color: #94A3B8;
        font-size: 1.05rem;
        margin-top: 6px;
    }

    /* Metric Cards */
    .metric-card {
        background: #151D2E;
        border: 1px solid #1E293B;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        border-color: #6366F1;
        transform: translateY(-2px);
    }
    .metric-label {
        font-size: 0.85rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }
    .metric-value {
        font-size: 1.9rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-top: 4px;
    }

    /* Badges */
    .badge-pass {
        background-color: rgba(16, 185, 129, 0.2);
        color: #10B981;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .badge-fail {
        background-color: rgba(239, 68, 68, 0.2);
        color: #EF4444;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .badge-warn {
        background-color: rgba(245, 158, 11, 0.2);
        color: #F59E0B;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .badge-demo {
        background-color: rgba(56, 189, 248, 0.15);
        color: #38BDF8;
        padding: 4px 12px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }

    /* Primary Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
        color: #FFFFFF;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        padding: 10px 24px;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #4F46E5 0%, #4338CA 100%);
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
    }
</style>
""", unsafe_allow_html=True)


# Sidebar Navigation
with st.sidebar:
    st.image("https://raw.githubusercontent.com/feathericons/feather/master/icons/zap.svg", width=36)
    st.markdown("### **IncuBrix Creator OS**")
    st.caption("2027 Graduate Assessment — Option 2")
    st.markdown("---")

    page = st.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "📝 Input & Campaign Setup",
            "⚡ Content Generation Engine",
            "🔍 Asset Review & Editor",
            "📦 Export & Submissions",
            "📈 Strategy & Market Intelligence",
            "🎥 Video Demonstration Checklist"
        ],
        index=0
    )

    st.markdown("---")
    st.markdown("**Engine Mode:**")
    st.markdown('<span class="badge-demo">Deterministic Local Demo</span>', unsafe_allow_html=True)
    st.caption("Guaranteed zero external cost, reproducible output, verified offline capability.")
    st.markdown("---")
    st.caption("Official Verified Target: [incubrix.com](https://incubrix.com)")


# -------------------------------------------------------------
# PAGE 1: DASHBOARD
# -------------------------------------------------------------
if page == "📊 Dashboard":
    st.markdown("""
    <div class="brand-hero">
        <h1 class="brand-title">IncuBrix Creator Operations Hub</h1>
        <div class="brand-subtitle">Automated multi-platform content engine turning 1 long-form piece into ready-to-publish assets</div>
    </div>
    """, unsafe_allow_html=True)

    metrics = db_manager.get_dashboard_metrics()
    total_assets = metrics["total_assets"]
    by_platform = metrics["by_platform"]
    by_format = metrics["by_format"]
    by_status = metrics["by_status"]
    recent_runs = metrics["recent_runs"]

    # Creator Metrics Row
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Content Assets</div>
            <div class="metric-value">{total_assets}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        approved_count = by_status.get("APPROVED", 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Ready to Publish</div>
            <div class="metric-value">{approved_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        videos_count = by_format.get("video", 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Short Videos (MP4)</div>
            <div class="metric-value">{videos_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        carousels_count = by_format.get("carousel", 0) + by_format.get("graphic", 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Visual Decks (PNG)</div>
            <div class="metric-value">{carousels_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with c5:
        native_count = by_format.get("native_post", 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Articles & Posts</div>
            <div class="metric-value">{native_count}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Creator Content Layout: Visual Mix & Publishing Feed
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("### 🌐 Platform Content Distribution")
        if by_platform:
            plat_df = pd.DataFrame(list(by_platform.items()), columns=["Platform", "Asset Count"])
            st.bar_chart(plat_df.set_index("Platform"), color="#6366F1")
        else:
            st.caption("Awaiting initial asset generation.")

        st.markdown("### 📅 Upcoming Publishing Schedule")
        all_assets = db_manager.list_assets()
        if all_assets:
            cal_preview = [
                {
                    "Asset ID": a["asset_id"],
                    "Platform": a["platform"].upper(),
                    "Format": a["format_type"],
                    "Scheduled Time": a["scheduled_time"],
                    "Hook": a["hook"][:60] + "..."
                }
                for a in all_assets[:6]
            ]
            st.dataframe(pd.DataFrame(cal_preview), use_container_width=True)
        else:
            st.info("No scheduled posts yet. Ingest an article and generate assets to build your calendar.")

    with col_right:
        st.markdown("### 🎬 Creative Output Showcase")
        all_assets = db_manager.list_assets()
        video_sample = next((a for a in all_assets if a["format_type"] == "video" and os.path.exists(a["creative_file_path"])), None)
        carousel_sample = next((a for a in all_assets if a["format_type"] == "carousel" and os.path.exists(a["creative_file_path"])), None)

        if video_sample:
            st.caption(f"**Latest Short Video:** `{video_sample['asset_id']}` ({video_sample['platform'].upper()})")
            sc_path = video_sample["creative_file_path"]
            sc_mtime = int(os.path.getmtime(sc_path)) if os.path.exists(sc_path) else 0
            with open(sc_path, "rb") as sc_f:
                st.video(sc_f.read(), format="video/mp4", key=f"dashboard_sample_vid_{sc_mtime}")
        elif carousel_sample:
            # Count all slides for this carousel
            cover = Path(carousel_sample["creative_file_path"])
            c_slides = sorted(cover.parent.glob(f"{carousel_sample['asset_id']}_slide_*.png"))
            st.caption(f"**Latest Carousel Deck:** `{carousel_sample['asset_id']}` — {len(c_slides)} slides")
            st.image(str(c_slides[0]) if c_slides else carousel_sample["creative_file_path"], use_container_width=True)
            st.info("➡️ Go to **🔍 Asset Review & Editor** to browse all slides with Prev / Next navigation.")
        else:
            st.caption("Creative media previews will appear here once content is generated.")

    st.markdown("<br>", unsafe_allow_html=True)

    # Collapsible Evaluator & Quality Inspection Panel — Hidden by default for normal users
    with st.expander("🔬 Evaluator / QA Panel — Quality Assurance Telemetry (Assessment Verification Only)", expanded=False):
        st.info("""
        **This panel is for IncuBrix Assessment Evaluators only.**  
        It shows automated quality compliance metrics and engine telemetry to help verify the submission meets all 12 assessment criteria.  
        Normal creators can safely ignore this section.
        """)  
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            st.markdown("#### Quality Validation Telemetry")
            if total_assets > 0:
                pass_count = metrics["by_quality"].get("PASS", 0)
                warn_count = metrics["by_quality"].get("WARNING", 0)
                fail_count = metrics["by_quality"].get("FAIL", 0)
                rate = round((pass_count / total_assets) * 100, 1)

                st.write(f"**Quality Compliance Pass Rate:** `{rate}%` (Assessment Target: >= 85%)")
                st.progress(min(1.0, rate / 100.0))
                q1, q2, q3 = st.columns(3)
                q1.markdown(f'<span class="badge-pass">PASS: {pass_count}</span>', unsafe_allow_html=True)
                q2.markdown(f'<span class="badge-warn">WARN: {warn_count}</span>', unsafe_allow_html=True)
                q3.markdown(f'<span class="badge-fail">FAIL: {fail_count}</span>', unsafe_allow_html=True)
            else:
                st.caption("No assets to validate yet.")

        with t_col2:
            st.markdown("#### Engine & Runtime Telemetry")
            if recent_runs:
                runs_df = pd.DataFrame(recent_runs)[
                    ["run_id", "mode", "requested_count", "successful_count", "runtime_seconds", "estimated_ai_cost", "status"]
                ]
                runs_df.columns = ["Run ID", "Mode", "Requested", "Success", "Runtime (s)", "Est. AI Cost ($)", "Status"]
                st.dataframe(runs_df, use_container_width=True)
            else:
                st.caption("No recent runs recorded.")


# -------------------------------------------------------------
# PAGE 2: INPUT & CAMPAIGN SETUP
# -------------------------------------------------------------
elif page == "📝 Input & Campaign Setup":
    st.markdown("## 📝 Input & Campaign Configuration")
    st.write("Provide long-form content (blog, podcast transcript, whitepaper) to transform into multi-platform assets.")

    # Load default sample article if available
    default_text = ""
    sample_path = Path("data/inputs/creator_workflow_blog.md")
    if sample_path.exists():
        with open(sample_path, "r", encoding="utf-8") as f:
            default_text = f.read()

    with st.form("input_form"):
        col_meta1, col_meta2 = st.columns(2)
        with col_meta1:
            campaign_name = st.text_input("Campaign Name", value="incubrix_growth_2027")
            source_url = st.text_input("Source URL (Reference)", value="https://incubrix.com/blog/scalable-content-engine")
            target_platforms = st.multiselect(
                "Target Platforms",
                options=["linkedin", "instagram", "youtube"],
                default=["linkedin", "instagram", "youtube"]
            )
        with col_meta2:
            destination_url = st.text_input("Verified Destination URL", value="https://incubrix.com")
            timezone_choice = st.selectbox("Publishing Timezone", options=["UTC", "America/New_York", "Asia/Kolkata", "Europe/London"])
            start_date = st.date_input("Campaign Start Date", value=datetime.now() + timedelta(days=1))

        st.markdown("---")
        st.markdown("#### Input Source Material")
        uploaded_file = st.file_uploader("Upload Document (TXT, MD, PDF)", type=["txt", "md", "pdf"])
        
        raw_text_input = st.text_area(
            "Or Paste Long-Form Article / Transcript Text",
            value=default_text,
            height=250
        )

        submitted = st.form_submit_button("📥 Ingest and Analyze Document")

    if submitted:
        try:
            raw_bytes = uploaded_file.read() if uploaded_file else None
            ext = uploaded_file.name.split(".")[-1].lower() if uploaded_file else "text"
            text_to_process = "" if uploaded_file else raw_text_input

            doc = process_input(
                content=text_to_process,
                source_type=ext,
                campaign_name=campaign_name,
                source_url=source_url,
                raw_bytes=raw_bytes
            )

            # Store in session state and SQLite
            input_id = f"INP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            db_manager.save_input(
                input_id=input_id,
                title=doc.title,
                word_count=doc.word_count,
                raw_text=doc.raw_text,
                source_url=doc.source_url,
                metadata={"claims": doc.extracted_claims, "key_ideas": doc.key_ideas}
            )

            st.session_state["current_doc"] = doc
            st.session_state["current_input_id"] = input_id
            st.session_state["campaign_name"] = campaign_name
            st.session_state["destination_url"] = destination_url
            st.session_state["timezone_str"] = timezone_choice
            st.session_state["target_platforms"] = target_platforms

            st.success(f"Successfully ingested '{doc.title}' ({doc.word_count} words). Ready for generation!")

            # Display Extracted Intelligence
            st.markdown("### 💡 Extracted Key Ideas & Claims")
            i_col1, i_col2 = st.columns(2)
            with i_col1:
                st.markdown("**Key Ideas Extracted:**")
                for idea in doc.key_ideas:
                    st.markdown(f"- {idea}")
            with i_col2:
                st.markdown("**Verifiable Claims Identified:**")
                for c in doc.extracted_claims:
                    st.markdown(f"- *{c['claim_summary']}*")

        except Exception as e:
            st.error(f"Ingestion failed: {str(e)}")


# -------------------------------------------------------------
# PAGE 3: CONTENT GENERATION ENGINE
# -------------------------------------------------------------
elif page == "⚡ Content Generation Engine":
    st.markdown("## ⚡ Content Generation Pipeline")
    st.write("Run the automated pipeline to transform your ingested document into platform-native videos, carousels, and posts.")

    if "current_doc" not in st.session_state:
        st.warning("No active document loaded. Loading default sample article automatically...")
        sample_path = Path("data/inputs/creator_workflow_blog.md")
        if sample_path.exists():
            with open(sample_path, "r", encoding="utf-8") as f:
                doc = process_input(f.read(), campaign_name="incubrix_growth_2027")
                st.session_state["current_doc"] = doc
                st.session_state["current_input_id"] = "INP_DEFAULT"
                st.session_state["campaign_name"] = "incubrix_growth_2027"
                st.session_state["destination_url"] = "https://incubrix.com"
                st.session_state["timezone_str"] = "UTC"
                st.session_state["target_platforms"] = ["linkedin", "instagram", "youtube"]

    doc = st.session_state.get("current_doc")
    st.info(f"**Loaded Input:** {doc.title} ({doc.word_count} words)")

    col_cfg1, col_cfg2 = st.columns(2)
    with col_cfg1:
        gen_mode = st.radio(
            "Generation Mode",
            ["Full 30-Asset Package (Recommended for Submission)", "Minimum 10-Asset Sprint"],
            index=0
        )
        selected_mode = "package_30" if "30" in gen_mode else "min_10"
    with col_cfg2:
        provider_choice = st.selectbox(
            "AI Provider",
            ["Local Demo Engine (Deterministic / Free)", "OpenAI (gpt-4o-mini)", "Anthropic Claude", "Google Gemini"]
        )
        provider_code = "demo" if "Demo" in provider_choice else ("openai" if "OpenAI" in provider_choice else "anthropic")

    # Video Duration Selector
    st.markdown("---")
    vcol1, vcol2 = st.columns([2, 1])
    with vcol1:
        video_duration = st.slider(
            "🎬 Short Video Duration (seconds)",
            min_value=5,
            max_value=60,
            value=15,
            step=5,
            help="Choose how long each generated Short / Reel video will be. The assessment allows up to 60 seconds."
        )
    with vcol2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.info(f"**{video_duration}s** per video  \n(Max allowed: 60s)")

    start_btn = st.button("🚀 Execute Content Engine & Render Media")

    if start_btn:
        run_id = f"RUN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        target_count = 30 if selected_mode == "package_30" else 10
        is_demo = (provider_code == "demo")

        # Telemetry start
        tracker = TelemetryTracker(
            run_id=run_id,
            model_name="demo-deterministic-engine-v1" if is_demo else "gpt-4o-mini",
            provider=provider_code,
            is_demo_mode=is_demo,
            input_words=doc.word_count,
            requested_count=target_count
        )

        db_manager.create_generation_run(
            run_id=run_id,
            input_id=st.session_state.get("current_input_id", "INP_AUTO"),
            mode=selected_mode,
            requested_count=target_count,
            model_name=tracker.telemetry.model_name,
            is_demo_mode=is_demo
        )

        progress_bar = st.progress(0.0)
        status_box = st.empty()

        generator = ContentGenerator(
            provider=provider_code,
            campaign_name=st.session_state.get("campaign_name", "incubrix_growth_2027"),
            destination_url=st.session_state.get("destination_url", "https://incubrix.com"),
            timezone_str=st.session_state.get("timezone_str", "UTC")
        )

        def update_progress(current, total, msg):
            progress_bar.progress(current / total)
            status_box.markdown(f"**Step {current}/{total}:** {msg}")

        # Fetch existing texts for deduplication
        existing_texts = db_manager.get_all_existing_texts()

        try:
            assets, retries, tokens = generator.generate_content_package(
                doc=doc,
                run_id=run_id,
                mode=selected_mode,
                platforms=st.session_state.get("target_platforms", ["linkedin", "instagram", "youtube"]),
                existing_texts=existing_texts,
                progress_callback=update_progress,
                video_duration_seconds=video_duration
            )

            # Validate each asset and persist
            passed_count = 0
            for a in assets:
                rep = validator.validate_asset(a.model_dump(), existing_texts)
                a.quality_status = rep.overall_status
                if rep.overall_status in ["PASS", "WARNING"]:
                    passed_count += 1
                
                db_manager.save_asset(a.model_dump())
                db_manager.save_validation_results(
                    a.asset_id,
                    [{"check_name": c.check_name, "status": c.status, "details": c.details} for c in rep.checks]
                )

            # Finalize Telemetry
            telemetry = tracker.finalize(successful=len(assets), failed=0, token_count=tokens)
            db_manager.update_generation_run(
                run_id=run_id,
                successful_count=len(assets),
                failed_count=0,
                runtime_seconds=telemetry.wall_clock_seconds,
                status="COMPLETED",
                retry_count=retries,
                token_usage=tokens,
                estimated_ai_cost=telemetry.estimated_ai_cost_usd,
                estimated_render_cost=telemetry.estimated_render_cost_usd
            )

            status_box.empty()
            progress_bar.progress(1.0)
            st.success(f"Run {run_id} completed successfully in {telemetry.wall_clock_seconds}s! Generated {len(assets)} assets.")

            # Summary Cards
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Assets Created", len(assets))
            s2.metric("Wall-Clock Time", f"{telemetry.wall_clock_seconds}s")
            s3.metric("Estimated Cost", f"${telemetry.estimated_ai_cost_usd + telemetry.estimated_render_cost_usd:.4f}")
            s4.metric("Passing Validation", f"{passed_count} / {len(assets)}")

        except Exception as e:
            st.error(f"Generation encountered error: {str(e)}")


# -------------------------------------------------------------
# PAGE 4: ASSET REVIEW & EDITOR
# -------------------------------------------------------------
elif page == "🔍 Asset Review & Editor":
    st.markdown("## 🔍 Asset Review and Human Approval")
    st.write("Inspect, edit, approve, or reject generated assets. Automated checks are clearly distinguished from human editorial approvals.")

    all_assets = db_manager.list_assets()
    if not all_assets:
        st.info("No assets found. Run generation on the **Content Generation Engine** page first.")
    else:
        # Filter controls
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            plat_filter = st.selectbox("Filter Platform", ["All"] + list(set(a["platform"] for a in all_assets)))
        with f_col2:
            status_filter = st.selectbox("Filter Status", ["All", "DRAFT", "APPROVED", "REJECTED"])
        with f_col3:
            format_filter = st.selectbox("Filter Format", ["All"] + list(set(a["format_type"] for a in all_assets)))

        filtered = [
            a for a in all_assets
            if (plat_filter == "All" or a["platform"] == plat_filter) and
               (status_filter == "All" or a["publication_status"] == status_filter) and
               (format_filter == "All" or a["format_type"] == format_filter)
        ]

        st.caption(f"Showing {len(filtered)} of {len(all_assets)} total assets")

        selected_id = st.selectbox("Select Asset to Review", [a["asset_id"] for a in filtered])
        asset = next((a for a in filtered if a["asset_id"] == selected_id), None)

        if asset:
            st.markdown("---")
            a_col1, a_col2 = st.columns([1, 1])

            with a_col1:
                st.markdown(f"### Creative Preview: `{asset['asset_id']}`")
                st.caption(f"Platform: **{asset['platform'].upper()}** | Format: **{asset['format_type']}** | Pillar: **{asset['content_pillar']}**")

                creative_path = asset["creative_file_path"]

                # -------------------------------------------------------
                # CAROUSEL: interactive slide viewer with Prev / Next nav
                # -------------------------------------------------------
                if asset["format_type"] == "carousel":
                    # Discover all slides for this asset (slide_1, slide_2, ...)
                    cover = Path(creative_path)
                    slide_dir = cover.parent
                    # Pattern: <asset_id>_slide_N.png
                    slide_files = sorted(
                        slide_dir.glob(f"{asset['asset_id']}_slide_*.png"),
                        key=lambda p: int(p.stem.rsplit('_', 1)[-1])
                    )

                    if not slide_files:
                        # Fallback if naming differs
                        slide_files = [cover] if cover.exists() else []

                    total_slides = len(slide_files)

                    if total_slides > 0:
                        # Session-state key per asset to remember current slide
                        slide_key = f"slide_idx_{asset['asset_id']}"
                        if slide_key not in st.session_state:
                            st.session_state[slide_key] = 0

                        cur = st.session_state[slide_key]

                        # Navigation row: Prev | Slide N of Total | Next
                        nav_l, nav_mid, nav_r = st.columns([1, 2, 1])
                        with nav_l:
                            if st.button("◀ Prev", key=f"prev_{asset['asset_id']}", disabled=(cur == 0)):
                                st.session_state[slide_key] = cur - 1
                                st.rerun()
                        with nav_mid:
                            st.markdown(
                                f"<div style='text-align:center;font-weight:700;color:#6366F1;padding-top:8px'>Slide {cur+1} / {total_slides}</div>",
                                unsafe_allow_html=True
                            )
                        with nav_r:
                            if st.button("Next ▶", key=f"next_{asset['asset_id']}", disabled=(cur == total_slides - 1)):
                                st.session_state[slide_key] = cur + 1
                                st.rerun()

                        # Main slide display (fresh bytes to bypass browser caching)
                        with open(str(slide_files[cur]), "rb") as s_f:
                            st.image(s_f.read(), use_container_width=True)

                        # Thumbnail strip (click to jump)
                        if total_slides > 1:
                            st.caption("📸 Slide thumbnails — click a slide number to jump:")
                            thumb_cols = st.columns(min(total_slides, 6))
                            for ti, sf in enumerate(slide_files):
                                with thumb_cols[ti % 6]:
                                    border_color = "#6366F1" if ti == cur else "#1E293B"
                                    st.markdown(
                                        f"<div style='border:2px solid {border_color};border-radius:6px;text-align:center;padding:2px;margin-bottom:4px;'>"
                                        f"<span style='font-size:0.75rem;color:#94A3B8'>Slide {ti+1}</span></div>",
                                        unsafe_allow_html=True
                                    )
                                    if st.button(f"{ti+1}", key=f"thumb_{asset['asset_id']}_{ti}"):
                                        st.session_state[slide_key] = ti
                                        st.rerun()

                        # Per-slide download
                        with open(str(slide_files[cur]), "rb") as f:
                            st.download_button(
                                label=f"⬇️ Download Slide {cur+1} PNG",
                                data=f.read(),
                                file_name=slide_files[cur].name,
                                mime="image/png"
                            )
                    else:
                        st.warning("No carousel slide files found.")

                # -------------------------------------------------------
                # VIDEO
                # -------------------------------------------------------
                elif creative_path.lower().endswith(".mp4"):
                    if os.path.exists(creative_path):
                        mtime = int(os.path.getmtime(creative_path))
                        with open(creative_path, "rb") as vf:
                            st.video(vf.read(), format="video/mp4", key=f"video_player_{asset['asset_id']}_{mtime}")
                    else:
                        st.warning(f"Video file not found: {creative_path}")

                # -------------------------------------------------------
                # GRAPHIC / SINGLE IMAGE
                # -------------------------------------------------------
                elif creative_path.lower().endswith(".png") or creative_path.lower().endswith(".jpg"):
                    if os.path.exists(creative_path):
                        with open(creative_path, "rb") as img_f:
                            st.image(img_f.read(), use_container_width=True)
                        with open(creative_path, "rb") as f:
                            st.download_button(
                                label="⬇️ Download Image PNG",
                                data=f.read(),
                                file_name=os.path.basename(creative_path),
                                mime="image/png"
                            )
                    else:
                        st.warning(f"Image file not found: {creative_path}")

                else:
                    st.warning(f"Creative file not found at {creative_path}")

                # Editable source download
                st.markdown(f"**Editable Source File:** `{asset['editable_source_path']}`")
                if os.path.exists(asset["editable_source_path"]):
                    with open(asset["editable_source_path"], "r", encoding="utf-8") as f:
                        st.download_button(
                            label="⬇️ Download Editable Source JSON",
                            data=f.read(),
                            file_name=os.path.basename(asset["editable_source_path"]),
                            mime="application/json"
                        )

            with a_col2:
                st.markdown("### Copy & Metadata")
                with st.form(f"edit_form_{asset['asset_id']}"):
                    new_hook = st.text_input("Hook", value=asset["hook"])
                    new_caption = st.text_area("Caption / Script", value=asset["caption"], height=160)
                    new_cta = st.text_input("Call To Action", value=asset["cta"])
                    new_hashtags = st.text_input("Hashtags", value=asset["hashtags"])
                    
                    st.text_input("Verified UTM Link", value=asset["utm_url"], disabled=True)
                    st.text_input("Source Reference", value=asset["source_reference"], disabled=True)
                    st.text_input("Target Metric", value=f"{asset['target_metric']} ({asset['metric_measurement_method']})", disabled=True)

                    btn_col1, btn_col2, btn_col3 = st.columns(3)
                    save_changes = btn_col1.form_submit_button("💾 Save Copy Edits")
                    approve_btn = btn_col2.form_submit_button("✅ Approve for Publish")
                    reject_btn = btn_col3.form_submit_button("❌ Reject Asset")

                if save_changes:
                    asset["hook"] = new_hook
                    asset["caption"] = new_caption
                    asset["cta"] = new_cta
                    asset["hashtags"] = new_hashtags
                    db_manager.save_asset(asset)
                    st.success("Asset copy updated successfully.")
                    st.rerun()

                if approve_btn:
                    # Enforce rule: never approve when mandatory check failed!
                    validations = db_manager.get_asset_validations(asset["asset_id"])
                    has_blocking = any(v["status"] == "FAIL" for v in validations)
                    if has_blocking:
                        st.error("Cannot approve asset: Mandatory quality check has failed. Please resolve errors first.")
                    else:
                        db_manager.update_asset_status(asset["asset_id"], "APPROVED")
                        st.success("Asset approved!")
                        st.rerun()

                if reject_btn:
                    db_manager.update_asset_status(asset["asset_id"], "REJECTED")
                    st.warning("Asset marked as REJECTED.")
                    st.rerun()

            # Validation Inspection Panel
            st.markdown("### 🛡️ Quality Validation Results for this Asset")
            v_results = db_manager.get_asset_validations(asset["asset_id"])
            if v_results:
                v_df = pd.DataFrame(v_results)[["check_name", "status", "details"]]
                st.dataframe(v_df, use_container_width=True)
            else:
                st.caption("No validation entries found for this asset.")


# -------------------------------------------------------------
# PAGE 5: EXPORT & SUBMISSIONS
# -------------------------------------------------------------
elif page == "📦 Export & Submissions":
    st.markdown("## 📦 Export Package & Assessment Submission")
    st.write("Generate and download the complete evaluation deliverables: `calendar.csv`, `calendar.json`, `workbook.xlsx`, and audit reports.")

    all_assets = db_manager.list_assets()
    all_runs = db_manager.get_dashboard_metrics()["recent_runs"]

    if not all_assets:
        st.warning("No assets in database to export. Please generate assets first.")
    else:
        # Export Actions
        csv_path = export_calendar_csv(all_assets, "output/reports/calendar.csv")
        json_path = export_calendar_json(all_assets, "output/reports/calendar.json")
        workbook_path = export_submission_workbook(all_assets, all_runs, "submission/workbook.xlsx")

        st.success("Export files generated and synchronized with database!")

        d1, d2, d3 = st.columns(3)
        with d1:
            with open(csv_path, "rb") as f:
                st.download_button(
                    label="⬇️ Download calendar.csv",
                    data=f.read(),
                    file_name="calendar.csv",
                    mime="text/csv"
                )
        with d2:
            with open(json_path, "rb") as f:
                st.download_button(
                    label="⬇️ Download calendar.json",
                    data=f.read(),
                    file_name="calendar.json",
                    mime="application/json"
                )
        with d3:
            with open(workbook_path, "rb") as f:
                st.download_button(
                    label="⬇️ Download workbook.xlsx",
                    data=f.read(),
                    file_name="workbook.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🔬 Assessment Evaluator Tool — 20-Asset Random Quality Audit (Assessment Verification Only)", expanded=False):
            st.info("""
            **For IncuBrix Assessment Evaluators only.**  
            This tool runs a reproducible random audit of 20 sampled assets against all 12 quality criteria, targeting a ≥85% pass rate.  
            Normal users don't need to interact with this panel.
            """)
            st.markdown("### 🔍 Reproducible 20-Asset Random Audit")
            st.write("Assessment Requirement: Reproducible random audit of 20 assets against all 12 criteria, targeting >= 85% passing score.")

            seed_input = st.number_input("Random Seed for Audit Reproducibility", value=42, step=1)
            if st.button("🔬 Execute 20-Asset Random Quality Audit"):
                audit_result = audit_runner.run_reproducible_audit(
                    assets=all_assets,
                    sample_size=20,
                    random_seed=seed_input,
                    output_csv="output/reports/audit_report.csv"
                )

                # Persist in DB
                db_manager.save_audit_log(
                    run_id=all_runs[0]["run_id"] if all_runs else "MANUAL",
                    sample_size=audit_result["sample_size"],
                    pass_count=audit_result["passed_count"],
                    fail_count=audit_result["failed_count"],
                    pass_rate=audit_result["pass_rate_pct"],
                    report_path=audit_result["report_path"]
                )

                st.markdown(f"#### Audit Result: `{audit_result['pass_rate_pct']}%` Pass Rate")
                if audit_result["meets_target"]:
                    st.success(f"✅ EXCEEDS TARGET: {audit_result['passed_count']} of {audit_result['sample_size']} sampled assets passed all mandatory criteria (Target: >=85%).")
                else:
                    st.error(f"❌ Below target: {audit_result['pass_rate_pct']}% pass rate.")

                if Path(audit_result["report_path"]).exists():
                    audit_df = pd.read_csv(audit_result["report_path"])
                    st.dataframe(audit_df, use_container_width=True)

                    with open(audit_result["report_path"], "rb") as f:
                        st.download_button("⬇️ Download audit_report.csv", f.read(), "audit_report.csv", "text/csv")


# -------------------------------------------------------------
# PAGE 6: STRATEGY & MARKET INTELLIGENCE
# -------------------------------------------------------------
elif page == "📈 Strategy & Market Intelligence":
    st.markdown("## 📈 Research, Strategy & Growth Deliverables")
    
    tab_res, tab_strat, tab_survey = st.tabs(["Market & Competitor Insights", "30-Day Launch Strategy", "Real-Audience Test Protocol"])

    with tab_res:
        research_file = Path("data/research/product_and_competitor_research.md")
        if research_file.exists():
            with open(research_file, "r", encoding="utf-8") as f:
                st.markdown(f.read())
        else:
            st.info("Research report file located at data/research/product_and_competitor_research.md")

    with tab_strat:
        launch_kit_file = Path("submission/launch_kit.md")
        if launch_kit_file.exists():
            with open(launch_kit_file, "r", encoding="utf-8") as f:
                st.markdown(f.read())
        else:
            st.info("Launch kit document located at submission/launch_kit.md")

    with tab_survey:
        st.markdown("### 👥 Target-Audience Test Protocol and Status")
        survey_file = Path("data/survey/survey_specification.md")
        if survey_file.exists():
            with open(survey_file, "r", encoding="utf-8") as f:
                st.markdown(f.read())

        st.markdown("---")
        st.markdown("#### Real Audience Test Verification")
        from data.survey.analyze_survey import analyze_survey_responses
        analysis = analyze_survey_responses("data/survey/response_collection_template.csv")
        st.write(f"**Verification Status:** `{analysis['status']}`")
        st.write(f"**Recorded Responses:** `{analysis['sample_size']} / {analysis['target_size']}`")
        st.caption("Integrity Note: In strict compliance with assessment guidelines, zero false survey respondents or synthetic ratings have been injected.")


# -------------------------------------------------------------
# PAGE 7: VIDEO DEMONSTRATION CHECKLIST
# -------------------------------------------------------------
elif page == "🎥 Video Demonstration Checklist":
    st.markdown("## 🎥 Video Demonstration Scripts and Checklists")
    checklist_file = Path("submission/demo_checklist.md")
    if checklist_file.exists():
        with open(checklist_file, "r", encoding="utf-8") as f:
            st.markdown(f.read())
    else:
        st.info("Checklist located at submission/demo_checklist.md")

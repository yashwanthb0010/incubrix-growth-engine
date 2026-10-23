"""
Batch Generation Script
Generates the complete 30-asset initial production package from data/inputs/creator_workflow_blog.md,
runs 12-point quality validation on all 30 assets, saves to SQLite, and exports all submission files.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion import process_input
from src.generation import ContentGenerator
from src.validation import QualityValidator
from src.persistence import PersistenceManager
from src.telemetry import TelemetryTracker
from src.scheduler_export import export_calendar_csv, export_calendar_json, export_submission_workbook
from src.audit import AuditRunner


def main():
    print("=== INCUBRIX FULL 30-ASSET PACKAGE GENERATOR ===")
    input_file = Path("data/inputs/creator_workflow_blog.md")
    if not input_file.exists():
        raise FileNotFoundError(f"Missing input file: {input_file}")

    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    doc = process_input(content, campaign_name="incubrix_growth_2027")
    print(f"[1/5] Ingested document: '{doc.title}' ({doc.word_count} words).")

    db = PersistenceManager("data/incubrix.db")
    input_id = f"INP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    db.save_input(
        input_id=input_id,
        title=doc.title,
        word_count=doc.word_count,
        raw_text=doc.raw_text,
        source_url=doc.source_url,
        metadata={"claims": doc.extracted_claims, "key_ideas": doc.key_ideas}
    )

    run_id = f"RUN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    tracker = TelemetryTracker(
        run_id=run_id,
        model_name="demo-deterministic-engine-v1",
        provider="demo",
        is_demo_mode=True,
        input_words=doc.word_count,
        requested_count=30
    )

    db.create_generation_run(
        run_id=run_id,
        input_id=input_id,
        mode="package_30",
        requested_count=30,
        model_name=tracker.telemetry.model_name,
        is_demo_mode=True
    )

    generator = ContentGenerator(
        provider="demo",
        campaign_name="incubrix_growth_2027",
        destination_url="https://incubrix.com",
        timezone_str="UTC"
    )

    print("[2/5] Generating 30 platform-native assets across LinkedIn, Instagram, and YouTube...")
    def on_progress(curr, total, msg):
        print(f"  [{curr:02d}/{total:02d}] {msg}")

    existing_texts = db.get_all_existing_texts()
    assets, retries, tokens = generator.generate_content_package(
        doc=doc,
        run_id=run_id,
        mode="package_30",
        platforms=["linkedin", "instagram", "youtube"],
        existing_texts=existing_texts,
        progress_callback=on_progress
    )

    validator = QualityValidator()
    print("[3/5] Validating assets against all 12 quality criteria...")
    passed_count = 0
    assets_data = []

    for a in assets:
        data = a.model_dump()
        rep = validator.validate_asset(data, existing_texts)
        data["quality_status"] = rep.overall_status
        if rep.overall_status in ["PASS", "WARNING"]:
            passed_count += 1
            data["publication_status"] = "APPROVED"
        else:
            data["publication_status"] = "DRAFT"

        db.save_asset(data)
        db.save_validation_results(
            a.asset_id,
            [{"check_name": c.check_name, "status": c.status, "details": c.details} for c in rep.checks]
        )
        assets_data.append(data)

    telemetry = tracker.finalize(successful=len(assets), failed=0, token_count=tokens)
    db.update_generation_run(
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

    print(f"[4/5] Run finished in {telemetry.wall_clock_seconds} seconds! Pass count: {passed_count}/{len(assets)}.")

    print("[5/5] Exporting submission calendar.csv, calendar.json, and workbook.xlsx...")
    all_runs = db.get_dashboard_metrics()["recent_runs"]
    export_calendar_csv(assets_data, "output/reports/calendar.csv")
    export_calendar_json(assets_data, "output/reports/calendar.json")
    export_submission_workbook(assets_data, all_runs, "submission/workbook.xlsx")

    # Run Reproducible Audit
    audit_runner = AuditRunner(validator)
    audit_res = audit_runner.run_reproducible_audit(assets_data, sample_size=20, random_seed=42, output_csv="output/reports/audit_report.csv")
    db.save_audit_log(
        run_id=run_id,
        sample_size=audit_res["sample_size"],
        pass_count=audit_res["passed_count"],
        fail_count=audit_res["failed_count"],
        pass_rate=audit_res["pass_rate_pct"],
        report_path=audit_res["report_path"]
    )

    print(f"=== AUDIT RESULTS ===")
    print(f"Sample Size: {audit_res['sample_size']}")
    print(f"Passed: {audit_res['passed_count']} / {audit_res['sample_size']}")
    print(f"Pass Rate: {audit_res['pass_rate_pct']}% (Target: >= 85%)")
    print(f"Meets Target: {audit_res['meets_target']}")
    print(f"Audit Report: {audit_res['report_path']}")
    print("=== GENERATION AND SUBMISSION PACKAGE COMPLETE ===")


if __name__ == "__main__":
    main()

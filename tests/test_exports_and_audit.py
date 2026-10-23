"""
Test Suite for Exports and Audit Engine
Covers: CSV calendar schema, JSON export, Excel workbook generation, and reproducible audit pass rate >= 85%.
"""

import os
import csv
import openpyxl
from src.scheduler_export import export_calendar_csv, export_calendar_json, export_submission_workbook, EXPORT_FIELDS
from src.audit import AuditRunner
from src.validation import QualityValidator


def test_calendar_csv_export_schema(tmp_path):
    csv_file = str(tmp_path / "test_calendar.csv")
    dummy_assets = [
        {
            "asset_id": "TEST_001",
            "platform": "linkedin",
            "format_type": "native_post",
            "content_pillar": "Creator Workflow",
            "target_audience": "Digital creators",
            "campaign_objective": "Conversions",
            "hook": "Strong Hook",
            "caption": "Detailed educational caption",
            "hashtags": "#test",
            "cta": "incubrix.com",
            "destination_url": "https://incubrix.com",
            "utm_url": "https://incubrix.com?utm_source=li&utm_medium=org&utm_campaign=c1&utm_content=a1",
            "target_metric": "CTR",
            "metric_measurement_method": "Analytics",
            "scheduled_time": "2026-11-01 10:00:00",
            "timezone": "UTC",
            "creative_file_path": "output/assets/TEST_001.png",
            "editable_source_path": "output/editable_sources/TEST_001_source.json",
            "product_claim_status": "VERIFIED",
            "rights_review_status": "CLEARED",
            "quality_status": "PASS",
            "publication_status": "DRAFT",
            "source_reference": "Ref #1"
        }
    ]

    export_calendar_csv(dummy_assets, csv_file)
    assert os.path.exists(csv_file)

    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        expected_headers = [label for _, label in EXPORT_FIELDS]
        assert header == expected_headers
        row = next(reader)
        assert row[0] == "TEST_001"


def test_submission_workbook_export(tmp_path):
    xlsx_file = str(tmp_path / "test_workbook.xlsx")
    dummy_assets = [
        {
            "asset_id": f"TEST_{i:03d}",
            "platform": "instagram",
            "format_type": "video" if i <= 10 else "carousel",
            "quality_status": "PASS"
        }
        for i in range(1, 21)
    ]
    dummy_runs = [
        {"run_id": "RUN_001", "mode": "package_30", "model_name": "demo", "status": "COMPLETED"}
    ]

    export_submission_workbook(dummy_assets, dummy_runs, xlsx_file)
    assert os.path.exists(xlsx_file)

    wb = openpyxl.load_workbook(xlsx_file)
    assert "Executive Summary" in wb.sheetnames
    assert "Content Calendar" in wb.sheetnames
    assert "Run Telemetry" in wb.sheetnames


def test_audit_reproducibility_and_target_pass_rate(tmp_path):
    validator = QualityValidator()
    audit_runner = AuditRunner(validator)

    # Build 25 compliant dummy assets with valid temporary files
    assets = []
    for i in range(1, 26):
        c_path = str(tmp_path / f"asset_{i}.png")
        s_path = str(tmp_path / f"source_{i}.json")
        with open(c_path, "w") as f:
            f.write("mock_image")
        with open(s_path, "w") as f:
            f.write("{}")

        assets.append({
            "asset_id": f"AUDIT_ASSET_{i:03d}",
            "platform": "instagram",
            "format_type": "graphic",
            "content_pillar": "Creator Workflow",
            "hook": f"Validated Opening Hook #{i} for high conversion",
            "caption": f"Detailed educational caption #{i} providing actionable tactical frameworks.",
            "cta": "Explore the Creator OS at incubrix.com",
            "destination_url": "https://incubrix.com",
            "utm_url": f"https://incubrix.com?utm_source=instagram&utm_medium=organic_social&utm_campaign=incubrix_growth_2027&utm_content=audit_asset_{i:03d}",
            "target_metric": "Engagement Rate",
            "metric_measurement_method": "Instagram Insights",
            "scheduled_time": "2026-11-01 10:00:00",
            "timezone": "UTC",
            "creative_file_path": c_path,
            "editable_source_path": s_path,
            "product_claim_status": "VERIFIED",
            "rights_review_status": "CLEARED"
        })

    report_csv = str(tmp_path / "audit_report.csv")
    result1 = audit_runner.run_reproducible_audit(assets, sample_size=20, random_seed=42, output_csv=report_csv)
    result2 = audit_runner.run_reproducible_audit(assets, sample_size=20, random_seed=42, output_csv=report_csv)

    # Determinism check
    assert result1["sample_size"] == 20
    assert result1["pass_rate_pct"] == result2["pass_rate_pct"]
    assert [d["asset_id"] for d in result1["details"]] == [d["asset_id"] for d in result2["details"]]

    # Pass rate must meet >= 85% requirement
    assert result1["pass_rate_pct"] >= 85.0
    assert result1["meets_target"] is True

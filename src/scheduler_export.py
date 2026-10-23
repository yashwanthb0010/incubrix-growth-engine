"""
IncuBrix Scheduler and Export Module
Generates calendar.csv, calendar.json, submission/workbook.xlsx, and export audit packages.
"""

import csv
import json
import os
from pathlib import Path
from typing import List, Dict, Any
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


EXPORT_FIELDS = [
    ("asset_id", "Asset_ID"),
    ("platform", "Platform"),
    ("format_type", "Format_Type"),
    ("content_pillar", "Content_Pillar"),
    ("target_audience", "Target_Audience"),
    ("campaign_objective", "Campaign_Objective"),
    ("hook", "Hook"),
    ("caption", "Caption_Or_Script"),
    ("hashtags", "Hashtags"),
    ("cta", "Call_To_Action"),
    ("destination_url", "Destination_URL"),
    ("utm_url", "UTM_Tracking_URL"),
    ("target_metric", "Target_Metric"),
    ("metric_measurement_method", "Metric_Measurement_Method"),
    ("scheduled_time", "Scheduled_Publishing_Time"),
    ("timezone", "Timezone"),
    ("creative_file_path", "Creative_File_Path"),
    ("editable_source_path", "Editable_Source_Path"),
    ("product_claim_status", "Product_Claim_Verification_Status"),
    ("rights_review_status", "Rights_Review_Status"),
    ("quality_status", "Quality_Validation_Status"),
    ("publication_status", "Publication_Status"),
    ("source_reference", "Source_Input_Reference")
]


def export_calendar_csv(assets: List[Dict[str, Any]], output_path: str = "output/reports/calendar.csv") -> str:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Header
        writer.writerow([label for _, label in EXPORT_FIELDS])
        for a in assets:
            row = [str(a.get(key, "")) for key, _ in EXPORT_FIELDS]
            writer.writerow(row)
    return output_path


def export_calendar_json(assets: List[Dict[str, Any]], output_path: str = "output/reports/calendar.json") -> str:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(assets, f, indent=2, ensure_ascii=False)
    return output_path


def export_run_history_csv(runs: List[Dict[str, Any]], output_path: str = "output/reports/run_history.csv") -> str:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fields = ["run_id", "input_id", "mode", "requested_count", "successful_count", "failed_count", "start_time", "end_time", "runtime_seconds", "model_name", "retry_count", "token_usage", "estimated_ai_cost", "estimated_render_cost", "status"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in runs:
            clean_r = {k: r.get(k, "") for k in fields}
            writer.writerow(clean_r)
    return output_path


def export_submission_workbook(
    assets: List[Dict[str, Any]],
    telemetry_runs: List[Dict[str, Any]],
    output_path: str = "submission/workbook.xlsx"
) -> str:
    """
    Creates the comprehensive submission workbook with all tabs,
    summary calculations, formatting, and evidence references.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    wb = openpyxl.Workbook()

    # Style definitions
    header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    accent_fill = PatternFill(start_color="6366F1", end_color="6366F1", fill_type="solid")
    accent_font = Font(name="Segoe UI", size=12, bold=True, color="FFFFFF")
    cell_font = Font(name="Segoe UI", size=10)
    border_thin = Border(
        left=Side(style='thin', color='E2E8F0'),
        right=Side(style='thin', color='E2E8F0'),
        top=Side(style='thin', color='E2E8F0'),
        bottom=Side(style='thin', color='E2E8F0')
    )

    # Tab 1: Executive Summary & Overview
    ws_summary = wb.active
    ws_summary.title = "Executive Summary"
    ws_summary.views.sheetView[0].showGridLines = True

    ws_summary.merge_cells("A1:G1")
    title_cell = ws_summary["A1"]
    title_cell.value = "INCUBRIX CONTENT ENGINE — 2027 ASSESSMENT SUBMISSION WORKBOOK"
    title_cell.font = Font(name="Segoe UI", size=14, bold=True, color="FFFFFF")
    title_cell.fill = accent_fill
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws_summary.row_dimensions[1].height = 35

    summary_rows = [
        ("Candidate Name / Project", "IncuBrix Social Media Content Engine (Option 2)"),
        ("Company Evaluated", "IncuBrix Private Limited (incubrix.com)"),
        ("Date of Execution", "October 23, 2026"),
        ("Total Production Assets Generated", len(assets)),
        ("Target Platforms", "LinkedIn, Instagram, YouTube Shorts"),
        ("Verified Destination URL", "https://incubrix.com"),
        ("Primary Engine Run Mode", "Full 30-Asset Multi-Format Package"),
        ("Short Videos Generated (MP4, <=60s)", f'=COUNTIF(\'Content Calendar\'!C2:C{len(assets)+1}, "video")'),
        ("Carousels & Graphics Generated (PNG)", f'=COUNTIF(\'Content Calendar\'!C2:C{len(assets)+1}, "carousel") + COUNTIF(\'Content Calendar\'!C2:C{len(assets)+1}, "graphic")'),
        ("Additional Platform-Native Assets", f'=COUNTIF(\'Content Calendar\'!C2:C{len(assets)+1}, "native_post")'),
        ("Quality Check Pass Rate Target", ">= 85%"),
        ("Automated Audit Pass Rate", f'=COUNTIF(\'Content Calendar\'!U2:U{len(assets)+1}, "PASS") / MAX(1, COUNTA(\'Content Calendar\'!A2:A{len(assets)+1}))')
    ]

    for r_idx, (k, v) in enumerate(summary_rows, start=3):
        ws_summary.cell(row=r_idx, column=1, value=k).font = Font(name="Segoe UI", size=10, bold=True)
        val_cell = ws_summary.cell(row=r_idx, column=2, value=v)
        val_cell.font = cell_font
        if str(v).startswith("="):
            val_cell.number_format = '0.0%' if "PASS" in str(v) else '0'

    ws_summary.column_dimensions["A"].width = 38
    ws_summary.column_dimensions["B"].width = 50

    # Tab 2: Content Calendar (Matching Schema)
    ws_cal = wb.create_sheet(title="Content Calendar")
    ws_cal.views.sheetView[0].showGridLines = True
    ws_cal.row_dimensions[1].height = 28

    for col_idx, (_, label) in enumerate(EXPORT_FIELDS, start=1):
        cell = ws_cal.cell(row=1, column=col_idx, value=label)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for r_idx, asset in enumerate(assets, start=2):
        ws_cal.row_dimensions[r_idx].height = 22
        for col_idx, (key, _) in enumerate(EXPORT_FIELDS, start=1):
            val = str(asset.get(key, ""))
            c = ws_cal.cell(row=r_idx, column=col_idx, value=val)
            c.font = cell_font
            c.border = border_thin
            c.alignment = Alignment(vertical="center")

    for col in ws_cal.columns:
        max_len = max(len(str(cell.value or "")) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws_cal.column_dimensions[col_letter].width = min(max(max_len + 3, 14), 45)

    # Tab 3: Execution History & Telemetry
    ws_tel = wb.create_sheet(title="Run Telemetry")
    ws_tel.views.sheetView[0].showGridLines = True

    tel_headers = ["Run_ID", "Mode", "Model_Name", "Requested", "Successful", "Failed", "Start_Time", "Runtime_Seconds", "Estimated_AI_Cost_USD", "Status"]
    for col_idx, h in enumerate(tel_headers, start=1):
        c = ws_tel.cell(row=1, column=col_idx, value=h)
        c.fill = header_fill
        c.font = header_font
        c.alignment = Alignment(horizontal="center", vertical="center")

    for r_idx, run in enumerate(telemetry_runs, start=2):
        ws_tel.cell(row=r_idx, column=1, value=run.get("run_id", ""))
        ws_tel.cell(row=r_idx, column=2, value=run.get("mode", ""))
        ws_tel.cell(row=r_idx, column=3, value=run.get("model_name", ""))
        ws_tel.cell(row=r_idx, column=4, value=run.get("requested_count", 0))
        ws_tel.cell(row=r_idx, column=5, value=run.get("successful_count", 0))
        ws_tel.cell(row=r_idx, column=6, value=run.get("failed_count", 0))
        ws_tel.cell(row=r_idx, column=7, value=run.get("start_time", ""))
        ws_tel.cell(row=r_idx, column=8, value=run.get("runtime_seconds", 0.0))
        ws_tel.cell(row=r_idx, column=9, value=run.get("estimated_ai_cost", 0.0))
        ws_tel.cell(row=r_idx, column=10, value=run.get("status", ""))

    for col in ws_tel.columns:
        col_letter = get_column_letter(col[0].column)
        ws_tel.column_dimensions[col_letter].width = 20

    # Save Workbook
    wb.save(output_path)
    return output_path

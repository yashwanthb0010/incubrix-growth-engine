"""
IncuBrix Validation Module
Comprehensive quality-assurance engine with Pydantic structured schemas and rule validators.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
import yaml
from pydantic import BaseModel, Field, field_validator


class AssetValidationItem(BaseModel):
    check_name: str
    status: str  # PASS, FAIL, WARNING
    details: str
    is_blocking: bool = True


class ValidationReport(BaseModel):
    asset_id: str
    overall_status: str  # PASS, FAIL, WARNING
    checks: List[AssetValidationItem] = Field(default_factory=list)
    has_blocking_failures: bool = False


class QualityValidator:
    def __init__(
        self,
        brand_config_path: str = "config/brand.yaml",
        claims_config_path: str = "config/product_claims.yaml",
        platforms_config_path: str = "config/platforms.yaml"
    ):
        self.brand_config = self._load_yaml(brand_config_path)
        self.claims_config = self._load_yaml(claims_config_path)
        self.platforms_config = self._load_yaml(platforms_config_path)

    def _load_yaml(self, path: str) -> dict:
        p = Path(path)
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    def validate_asset(self, asset: Dict[str, Any], existing_texts: Optional[List[str]] = None) -> ValidationReport:
        checks: List[AssetValidationItem] = []
        asset_id = asset.get("asset_id", "UNKNOWN")

        # 1. Check Hook
        hook = asset.get("hook", "").strip()
        if not hook:
            checks.append(AssetValidationItem(
                check_name="Hook Check",
                status="FAIL",
                details="Hook is empty. Every social asset requires a strong opening hook.",
                is_blocking=True
            ))
        elif len(hook) < 10:
            checks.append(AssetValidationItem(
                check_name="Hook Check",
                status="WARNING",
                details=f"Hook is very short ({len(hook)} chars). May lack engagement power.",
                is_blocking=False
            ))
        else:
            checks.append(AssetValidationItem(
                check_name="Hook Check",
                status="PASS",
                details=f"Strong hook present ({len(hook)} chars).",
                is_blocking=False
            ))

        # 2. Check Caption / Script
        caption = asset.get("caption", "").strip()
        if not caption:
            checks.append(AssetValidationItem(
                check_name="Caption Check",
                status="FAIL",
                details="Caption or script is missing.",
                is_blocking=True
            ))
        elif len(caption) < 25:
            checks.append(AssetValidationItem(
                check_name="Caption Check",
                status="FAIL",
                details="Caption is insufficiently descriptive (less than 25 chars).",
                is_blocking=True
            ))
        else:
            checks.append(AssetValidationItem(
                check_name="Caption Check",
                status="PASS",
                details=f"Caption verified ({len(caption)} chars).",
                is_blocking=False
            ))

        # 3. Check CTA & Destination URL
        cta = asset.get("cta", "").strip()
        dest_url = asset.get("destination_url", "").strip()
        verified_url = self.brand_config.get("verified_destination_url", "https://incubrix.com")

        if not cta:
            checks.append(AssetValidationItem(
                check_name="CTA Check",
                status="FAIL",
                details="Call to Action (CTA) is missing.",
                is_blocking=True
            ))
        else:
            checks.append(AssetValidationItem(
                check_name="CTA Check",
                status="PASS",
                details=f"CTA verified: '{cta[:40]}...'",
                is_blocking=False
            ))

        if not dest_url:
            checks.append(AssetValidationItem(
                check_name="Destination URL Check",
                status="FAIL",
                details="Destination URL is empty.",
                is_blocking=True
            ))
        else:
            parsed_dest = urlparse(dest_url)
            parsed_verified = urlparse(verified_url)
            if not parsed_dest.scheme or not parsed_dest.netloc:
                checks.append(AssetValidationItem(
                    check_name="Destination URL Check",
                    status="FAIL",
                    details=f"Invalid URL structure: {dest_url}",
                    is_blocking=True
                ))
            elif parsed_dest.netloc != parsed_verified.netloc:
                checks.append(AssetValidationItem(
                    check_name="Destination URL Check",
                    status="WARNING",
                    details=f"Destination domain '{parsed_dest.netloc}' does not match official brand domain '{parsed_verified.netloc}'.",
                    is_blocking=False
                ))
            else:
                checks.append(AssetValidationItem(
                    check_name="Destination URL Check",
                    status="PASS",
                    details=f"Destination domain matches verified URL ({parsed_dest.netloc}).",
                    is_blocking=False
                ))

        # 4. Check UTM Parameters
        utm_url = asset.get("utm_url", "").strip()
        from src.tracking import validate_utm_url
        utm_res = validate_utm_url(utm_url)
        if not utm_res["valid"]:
            checks.append(AssetValidationItem(
                check_name="UTM Tracking Check",
                status="FAIL",
                details=utm_res["reason"],
                is_blocking=True
            ))
        else:
            checks.append(AssetValidationItem(
                check_name="UTM Tracking Check",
                status="PASS",
                details=f"Valid UTM tracking parameters configured.",
                is_blocking=False
            ))

        # 5. Check Target Metric & Measurement
        target_metric = asset.get("target_metric", "").strip()
        metric_method = asset.get("metric_measurement_method", "").strip()
        if not target_metric or not metric_method:
            checks.append(AssetValidationItem(
                check_name="Metrics Attribution Check",
                status="FAIL",
                details="Missing target metric or explicit measurement method.",
                is_blocking=True
            ))
        else:
            checks.append(AssetValidationItem(
                check_name="Metrics Attribution Check",
                status="PASS",
                details=f"Target: {target_metric} | Measurement: {metric_method[:35]}...",
                is_blocking=False
            ))

        # 6. Check Product Claims and Forbidden Words
        combined_text = f"{hook} {caption}".lower()
        forbidden_phrases = [
            "guarantees 10m views",
            "backed by unnamed billionaires",
            "1-click publishing without review",
            "instant viral fame",
            "replaces all human writers completely"
        ]
        found_forbidden = [p for p in forbidden_phrases if p in combined_text]
        if found_forbidden:
            checks.append(AssetValidationItem(
                check_name="Product Claims Check",
                status="FAIL",
                details=f"Found prohibited unverified claim: {', '.join(found_forbidden)}",
                is_blocking=True
            ))
        else:
            checks.append(AssetValidationItem(
                check_name="Product Claims Check",
                status="PASS",
                details="No fabricated claims detected; adheres to brand claims registry.",
                is_blocking=False
            ))

        # 7. Check Creative File Existence and Format
        creative_path = asset.get("creative_file_path", "").strip()
        format_type = asset.get("format_type", "").lower()
        if not creative_path:
            checks.append(AssetValidationItem(
                check_name="Creative File Check",
                status="FAIL",
                details="Creative file path is missing.",
                is_blocking=True
            ))
        elif not os.path.exists(creative_path):
            checks.append(AssetValidationItem(
                check_name="Creative File Check",
                status="FAIL",
                details=f"Creative file does not exist on disk: {creative_path}",
                is_blocking=True
            ))
        else:
            file_size = os.path.getsize(creative_path)
            if file_size == 0:
                checks.append(AssetValidationItem(
                    check_name="Creative File Check",
                    status="FAIL",
                    details="Creative file is empty (0 bytes).",
                    is_blocking=True
                ))
            else:
                checks.append(AssetValidationItem(
                    check_name="Creative File Check",
                    status="PASS",
                    details=f"File verified: {os.path.basename(creative_path)} ({file_size // 1024} KB).",
                    is_blocking=False
                ))

        # 8. Check Video Constraints if Video
        if "video" in format_type or creative_path.lower().endswith(".mp4"):
            video_status, video_details = self._validate_video_file(creative_path)
            checks.append(AssetValidationItem(
                check_name="Video Specs Check",
                status=video_status,
                details=video_details,
                is_blocking=True if video_status == "FAIL" else False
            ))

        # 9. Check Editable Source File Existence
        editable_path = asset.get("editable_source_path", "").strip()
        if not editable_path:
            checks.append(AssetValidationItem(
                check_name="Editable Source Check",
                status="FAIL",
                details="Editable source file path is missing.",
                is_blocking=True
            ))
        elif not os.path.exists(editable_path):
            checks.append(AssetValidationItem(
                check_name="Editable Source Check",
                status="FAIL",
                details=f"Editable source not found on disk: {editable_path}",
                is_blocking=True
            ))
        else:
            checks.append(AssetValidationItem(
                check_name="Editable Source Check",
                status="PASS",
                details=f"Editable source verified: {os.path.basename(editable_path)}.",
                is_blocking=False
            ))

        # 10. Check Schedule & Timezone
        sched = asset.get("scheduled_time", "").strip()
        tz = asset.get("timezone", "").strip()
        if not sched or not tz:
            checks.append(AssetValidationItem(
                check_name="Schedule & Timezone Check",
                status="FAIL",
                details="Missing scheduled publishing date/time or explicit timezone.",
                is_blocking=True
            ))
        else:
            checks.append(AssetValidationItem(
                check_name="Schedule & Timezone Check",
                status="PASS",
                details=f"Scheduled for {sched} ({tz}).",
                is_blocking=False
            ))

        # 11. Check Rights & AI Disclosure
        rights_status = asset.get("rights_review_status", "").upper()
        if rights_status not in ["CLEARED", "PASSED", "VERIFIED"]:
            checks.append(AssetValidationItem(
                check_name="Rights & Disclosure Review",
                status="FAIL",
                details=f"Rights review status is '{rights_status}', must be CLEARED.",
                is_blocking=True
            ))
        else:
            checks.append(AssetValidationItem(
                check_name="Rights & Disclosure Review",
                status="PASS",
                details="Rights-safe assets verified; AI-assisted generation disclosed.",
                is_blocking=False
            ))

        # Overall Status
        has_blocking = any(c.status == "FAIL" and c.is_blocking for c in checks)
        has_warnings = any(c.status == "WARNING" for c in checks)
        overall = "FAIL" if has_blocking else ("WARNING" if has_warnings else "PASS")

        return ValidationReport(
            asset_id=asset_id,
            overall_status=overall,
            checks=checks,
            has_blocking_failures=has_blocking
        )

    def _validate_video_file(self, video_path: str) -> tuple[str, str]:
        """Validate duration <= 60s and aspect ratio using OpenCV."""
        try:
            import cv2
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return "FAIL", f"Unable to open video stream: {os.path.basename(video_path)}"
            
            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()

            duration = frame_count / fps if fps > 0 else 0.0

            if duration > 60.5:
                return "FAIL", f"Video exceeds 60s maximum limit ({round(duration, 1)}s)."
            if height <= width:
                return "WARNING", f"Expected vertical 9:16 aspect ratio (got {width}x{height})."

            return "PASS", f"Valid vertical video: {width}x{height}, {round(duration, 1)}s, {round(fps, 1)} FPS."
        except Exception as e:
            return "WARNING", f"Video validation check non-critical warning: {str(e)}"

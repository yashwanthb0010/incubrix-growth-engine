"""
IncuBrix Audit Module
Conducts a reproducible random audit of 20 assets against the full assessment criteria.
Produces individual pass/fail results with evidence, requiring >= 85% passing rate.
"""

import csv
import random
from pathlib import Path
from typing import List, Dict, Any, Tuple
from src.validation import QualityValidator


class AuditRunner:
    def __init__(self, validator: QualityValidator):
        self.validator = validator

    def run_reproducible_audit(
        self,
        assets: List[Dict[str, Any]],
        sample_size: int = 20,
        random_seed: int = 42,
        output_csv: str = "output/reports/audit_report.csv"
    ) -> Dict[str, Any]:
        """
        Selects a random sample of assets using a fixed seed for reproducibility.
        Evaluates each asset against all 12 criteria, compiling evidence.
        """
        if not assets:
            return {
                "sample_size": 0,
                "passed_count": 0,
                "failed_count": 0,
                "pass_rate_pct": 0.0,
                "meets_target": False,
                "report_path": "",
                "details": []
            }

        rng = random.Random(random_seed)
        actual_sample_size = min(sample_size, len(assets))
        sampled_assets = rng.sample(assets, actual_sample_size)

        audit_results = []
        passed_count = 0
        failed_count = 0

        for a in sampled_assets:
            report = self.validator.validate_asset(a)
            is_pass = (report.overall_status in ["PASS", "WARNING"] and not report.has_blocking_failures)
            
            if is_pass:
                passed_count += 1
            else:
                failed_count += 1

            # Compile evidence summary
            evidence_items = [f"[{c.check_name}: {c.status}] {c.details}" for c in report.checks]
            audit_results.append({
                "asset_id": a.get("asset_id"),
                "platform": a.get("platform"),
                "format_type": a.get("format_type"),
                "content_pillar": a.get("content_pillar"),
                "overall_audit_status": "PASS" if is_pass else "FAIL",
                "blocking_failure": report.has_blocking_failures,
                "checks_count": len(report.checks),
                "passed_checks": sum(1 for c in report.checks if c.status == "PASS"),
                "warning_checks": sum(1 for c in report.checks if c.status == "WARNING"),
                "failed_checks": sum(1 for c in report.checks if c.status == "FAIL"),
                "evidence_trail": " | ".join(evidence_items)
            })

        pass_rate = round((passed_count / actual_sample_size) * 100.0, 1)
        meets_target = (pass_rate >= 85.0)

        # Write audit_report.csv
        Path(output_csv).parent.mkdir(parents=True, exist_ok=True)
        fieldnames = [
            "asset_id", "platform", "format_type", "content_pillar",
            "overall_audit_status", "blocking_failure", "checks_count",
            "passed_checks", "warning_checks", "failed_checks", "evidence_trail"
        ]
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(audit_results)

        return {
            "sample_size": actual_sample_size,
            "random_seed": random_seed,
            "passed_count": passed_count,
            "failed_count": failed_count,
            "pass_rate_pct": pass_rate,
            "meets_target": meets_target,
            "report_path": output_csv,
            "details": audit_results
        }

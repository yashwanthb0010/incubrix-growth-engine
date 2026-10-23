"""
Test Suite for Validation and Quality Assurance
Covers: Missing required fields, invalid destination URLs, invalid UTM parameters, product claims checking.
"""

from src.validation import QualityValidator
from src.tracking import build_utm_url, validate_utm_url


def test_utm_validation():
    # Valid UTM
    valid_url = build_utm_url("https://incubrix.com", source="linkedin", medium="organic_social", campaign="incubrix_growth_2027", content="li_post_001")
    res = validate_utm_url(valid_url)
    assert res["valid"] is True
    assert res["params"]["utm_source"] == "linkedin"
    assert res["params"]["utm_content"] == "li_post_001"

    # Missing parameter
    bad_url = "https://incubrix.com?utm_source=linkedin&utm_medium=organic_social"
    res_bad = validate_utm_url(bad_url)
    assert res_bad["valid"] is False
    assert "Missing required UTM parameters" in res_bad["reason"]


def test_validator_detects_missing_fields():
    validator = QualityValidator()
    incomplete_asset = {
        "asset_id": "TEST_FAIL_001",
        "hook": "",  # Empty hook
        "caption": "",  # Empty caption
        "cta": "",
        "destination_url": "",
        "utm_url": "",
        "target_metric": "",
        "metric_measurement_method": "",
        "rights_review_status": "PENDING"
    }
    report = validator.validate_asset(incomplete_asset)
    assert report.overall_status == "FAIL"
    assert report.has_blocking_failures is True

    failed_checks = [c.check_name for c in report.checks if c.status == "FAIL"]
    assert "Hook Check" in failed_checks
    assert "Caption Check" in failed_checks
    assert "CTA Check" in failed_checks
    assert "Metrics Attribution Check" in failed_checks


def test_validator_flags_unsupported_product_claims():
    validator = QualityValidator()
    fabricated_asset = {
        "asset_id": "TEST_CLAIM_001",
        "hook": "IncuBrix guarantees 10M views overnight!",
        "caption": "Our AI replaces all human writers completely and is backed by unnamed billionaires.",
        "cta": "Click here",
        "destination_url": "https://incubrix.com",
        "utm_url": "https://incubrix.com?utm_source=ig&utm_medium=social&utm_campaign=c1&utm_content=a1",
        "target_metric": "Views",
        "metric_measurement_method": "Native Analytics",
        "creative_file_path": "nonexistent.mp4",
        "editable_source_path": "nonexistent.json",
        "scheduled_time": "2026-11-01 10:00:00",
        "timezone": "UTC",
        "rights_review_status": "CLEARED"
    }
    report = validator.validate_asset(fabricated_asset)
    claim_check = next((c for c in report.checks if c.check_name == "Product Claims Check"), None)
    assert claim_check is not None
    assert claim_check.status == "FAIL"
    assert "Found prohibited unverified claim" in claim_check.details


def test_validator_checks_destination_url():
    validator = QualityValidator()
    bad_domain_asset = {
        "asset_id": "TEST_URL_001",
        "hook": "Valid hook for digital creators looking to scale.",
        "caption": "Detailed valid caption describing how to multiply content effectively.",
        "cta": "Visit random domain",
        "destination_url": "https://unverified-scam-domain.com",
        "utm_url": "https://unverified-scam-domain.com?utm_source=ig&utm_medium=social&utm_campaign=c1&utm_content=a1",
        "target_metric": "Engagement",
        "metric_measurement_method": "Platform Analytics",
        "rights_review_status": "CLEARED"
    }
    report = validator.validate_asset(bad_domain_asset)
    url_check = next((c for c in report.checks if c.check_name == "Destination URL Check"), None)
    assert url_check is not None
    assert url_check.status == "WARNING"
    assert "does not match official brand domain" in url_check.details

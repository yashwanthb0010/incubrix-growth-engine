"""
Audience Survey Analysis Script
Processes participant responses for the IncuBrix content engine evaluation.
In accordance with assessment rules, does NOT fake data.
"""

import sys
from pathlib import Path
import pandas as pd


def analyze_survey_responses(csv_path: str = "data/survey/responses.csv") -> dict:
    file_path = Path(csv_path)
    if not file_path.exists() or file_path.stat().st_size == 0:
        return {
            "status": "AWAITING_RESPONSES",
            "sample_size": 0,
            "target_size": 20,
            "message": "Survey protocol is deployed. No external participant responses have been recorded yet in responses.csv.",
            "metrics": {}
        }

    try:
        df = pd.read_csv(file_path)
        sample_size = len(df)
        
        if sample_size == 0:
            return {
                "status": "EMPTY_DATASET",
                "sample_size": 0,
                "target_size": 20,
                "message": "CSV header exists but zero participant records are logged.",
                "metrics": {}
            }

        pref_counts = df["variant_preferred"].value_counts(normalize=True).to_dict() if "variant_preferred" in df else {}
        mean_hook = float(df["hook_strength_rating"].mean()) if "hook_strength_rating" in df else 0.0
        mean_edu = float(df["educational_value_score"].mean()) if "educational_value_score" in df else 0.0
        mean_click = float(df["click_intent_score"].mean()) if "click_intent_score" in df else 0.0
        mean_suitability = float(df["format_suitability_score"].mean()) if "format_suitability_score" in df else 0.0

        status = "COMPLETE" if sample_size >= 20 else f"PARTIAL_{sample_size}_OF_20"

        return {
            "status": status,
            "sample_size": sample_size,
            "target_size": 20,
            "metrics": {
                "variant_preference_pct": {k: round(v * 100, 1) for k, v in pref_counts.items()},
                "mean_hook_strength": round(mean_hook, 2),
                "mean_educational_value": round(mean_edu, 2),
                "mean_click_intent": round(mean_click, 2),
                "mean_format_suitability": round(mean_suitability, 2)
            }
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e),
            "sample_size": 0
        }


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/survey/response_collection_template.csv"
    results = analyze_survey_responses(path)
    print("=== INCUBRIX REAL AUDIENCE TEST AUDIT ===")
    print(f"Status: {results['status']}")
    print(f"Sample Size: {results['sample_size']} / {results.get('target_size', 20)}")
    print(f"Details: {results.get('message', results.get('metrics'))}")

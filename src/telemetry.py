"""
IncuBrix Telemetry Module
Tracks runtime execution, resource consumption, token metrics, and cost estimates.
Clearly separates measured values from mathematical estimates.
"""

import time
from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel, Field


class ExecutionTelemetry(BaseModel):
    run_id: str
    model_name: str
    provider: str
    is_demo_mode: bool
    input_word_count: int
    requested_assets: int
    successful_assets: int = 0
    failed_assets: int = 0
    start_time: str = Field(default_factory=lambda: datetime.now().isoformat())
    end_time: str = ""
    wall_clock_seconds: float = 0.0
    retry_count: int = 0
    measured_tokens: int = 0
    estimated_ai_cost_usd: float = 0.0
    estimated_render_cost_usd: float = 0.0
    cost_estimation_method: str = "Standard industry benchmark (Token/1k pricing + Render compute)"
    is_cost_measured: bool = False  # Explicitly distinguished: costs are estimated, runtime is measured!


class TelemetryTracker:
    def __init__(self, run_id: str, model_name: str, provider: str, is_demo_mode: bool, input_words: int, requested_count: int):
        self.telemetry = ExecutionTelemetry(
            run_id=run_id,
            model_name=model_name,
            provider=provider,
            is_demo_mode=is_demo_mode,
            input_word_count=input_words,
            requested_assets=requested_count
        )
        self._start_perf = time.perf_counter()

    def record_retry(self):
        self.telemetry.retry_count += 1

    def finalize(self, successful: int, failed: int, token_count: int = 0) -> ExecutionTelemetry:
        elapsed = time.perf_counter() - self._start_perf
        self.telemetry.end_time = datetime.now().isoformat()
        self.telemetry.wall_clock_seconds = round(elapsed, 2)
        self.telemetry.successful_assets = successful
        self.telemetry.failed_assets = failed
        self.telemetry.measured_tokens = token_count

        # Estimate AI cost based on model tiers ($0.15 / 1M input, $0.60 / 1M output for lightweight models)
        if self.telemetry.is_demo_mode:
            self.telemetry.estimated_ai_cost_usd = 0.0000
        else:
            # Approx $0.0015 per 1,000 tokens for standard mid-tier models
            self.telemetry.estimated_ai_cost_usd = round((token_count / 1000.0) * 0.0015, 4)

        # Estimate local rendering compute cost (~$0.0002 per rendered asset on standard cloud VM)
        self.telemetry.estimated_render_cost_usd = round(successful * 0.0002, 4)

        return self.telemetry

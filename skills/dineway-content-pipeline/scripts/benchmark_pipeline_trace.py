#!/usr/bin/env python3
"""Validate a completed native Pipeline trace and compare elapsed publish time."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


STANDARD_STAGES = ("research", "brief", "writer", "optimization")
STANDARD_LIFECYCLE_CALL_BUDGET = 9


class BenchmarkTraceError(ValueError):
    """Raised when the optimized trace cannot support a valid comparison."""


def _stage_and_status(entry: Any) -> tuple[str | None, str | None]:
    if not isinstance(entry, dict):
        return None, None
    job = entry.get("job")
    if isinstance(job, dict):
        return job.get("stage"), job.get("status")
    return entry.get("stage"), entry.get("status")


def benchmark_trace(
    status: dict[str, Any],
    baseline_publish_seconds: float,
    target_publish_seconds: float = 25 * 60,
) -> dict[str, Any]:
    if baseline_publish_seconds <= 0 or target_publish_seconds <= 0:
        raise BenchmarkTraceError("Baseline and target durations must be positive")

    timing = status.get("timing")
    jobs = status.get("jobs")
    if not isinstance(timing, dict) or not isinstance(jobs, list):
        raise BenchmarkTraceError("Trace must include native timing and Job snapshots")
    elapsed_ms = timing.get("elapsedMs")
    if not isinstance(elapsed_ms, (int, float)) or elapsed_ms <= 0:
        raise BenchmarkTraceError("Trace timing.elapsedMs must be a positive number")

    stage_states = [_stage_and_status(entry) for entry in jobs]
    standard_states = [state for state in stage_states if state[0] in STANDARD_STAGES]
    if standard_states != [(stage, "completed") for stage in STANDARD_STAGES]:
        raise BenchmarkTraceError(
            "Trace must contain one completed Research, Brief, Writer, and Optimization Job in order"
        )

    structural_calls = 1 + 2 * len(standard_states)
    optimized_seconds = elapsed_ms / 1000
    saved_seconds = baseline_publish_seconds - optimized_seconds
    reduction_fraction = saved_seconds / baseline_publish_seconds
    return {
        "baselinePublishSeconds": baseline_publish_seconds,
        "optimizedPublishSeconds": optimized_seconds,
        "savedSeconds": saved_seconds,
        "reductionPercent": round(reduction_fraction * 100, 2),
        "targetPublishSeconds": target_publish_seconds,
        "targetMet": optimized_seconds <= target_publish_seconds,
        "structuralLifecycleCalls": structural_calls,
        "structuralCallBudget": STANDARD_LIFECYCLE_CALL_BUDGET,
        "structuralCallBudgetMet": structural_calls <= STANDARD_LIFECYCLE_CALL_BUDGET,
        "stages": list(STANDARD_STAGES),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--optimized-status", required=True, type=Path)
    parser.add_argument("--baseline-publish-seconds", required=True, type=float)
    parser.add_argument("--target-publish-seconds", type=float, default=25 * 60)
    parser.add_argument("--require-target", action="store_true")
    args = parser.parse_args()

    try:
        status = json.loads(args.optimized_status.read_text(encoding="utf-8"))
        result = benchmark_trace(
            status,
            args.baseline_publish_seconds,
            args.target_publish_seconds,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, BenchmarkTraceError) as error:
        parser.error(str(error))

    print(json.dumps(result, indent=2, sort_keys=True))
    if args.require_target and not (result["targetMet"] and result["structuralCallBudgetMet"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

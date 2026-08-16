#!/usr/bin/env python3
"""Validate complete-session Dineway Content Pipeline performance evidence."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
from typing import Any


STANDARD_STAGES = ("research", "brief", "writer", "optimization")
STANDARD_LIFECYCLE_WRITES = (
    "run_start",
    "research_begin",
    "research_complete",
    "brief_begin",
    "brief_complete",
    "writer_begin",
    "writer_complete",
    "optimization_begin",
    "optimization_complete",
)
REQUIRED_DURATION_KEYS = (
    "humanApprovalWait",
    "toolExecution",
    "agentReasoning",
    "orchestration",
    "qa",
)
REQUIRED_SCOPE = {
    "comparisonBasis": "four_stage_article",
}
QUALITY_GATE_TARGET_SECONDS = 15 * 60
TOOL_ROUND_TRIP_BUDGET = 50
TOOL_OUTPUT_BYTE_BUDGET = 400 * 1024


class BenchmarkTraceError(ValueError):
    """Raised when a trace cannot support an authoritative comparison."""


def _stage_and_status(entry: Any) -> tuple[str | None, str | None]:
    if not isinstance(entry, dict):
        return None, None
    job = entry.get("job")
    if isinstance(job, dict):
        return job.get("stage"), job.get("status")
    return entry.get("stage"), entry.get("status")


def _mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise BenchmarkTraceError(f"Trace must include {name}")
    return value


def _list(value: Any, name: str) -> list[Any]:
    if not isinstance(value, list):
        raise BenchmarkTraceError(f"Trace must include {name} as a list")
    return value


def _instant(value: Any, name: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise BenchmarkTraceError(f"Trace must include milestone {name}")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise BenchmarkTraceError(f"Milestone {name} must be an ISO-8601 instant") from error


def _elapsed_seconds(start: datetime, end: datetime, name: str) -> float:
    seconds = (end - start).total_seconds()
    if seconds < 0:
        raise BenchmarkTraceError(f"Milestone {name} cannot precede requestedAt")
    return seconds


def benchmark_trace(
    trace: dict[str, Any],
    baseline_quality_gate_seconds: float,
) -> dict[str, Any]:
    if baseline_quality_gate_seconds <= 0:
        raise BenchmarkTraceError("Baseline quality-gate duration must be positive")

    scope = _mapping(trace.get("scope"), "comparable scope")
    if scope.get("comparable") is not True:
        raise BenchmarkTraceError("Trace scope must be explicitly comparable")
    for key, expected in REQUIRED_SCOPE.items():
        if scope.get(key) != expected:
            raise BenchmarkTraceError(f"Trace scope requires {key}={expected}")
    for key in ("contentType", "locale"):
        if not isinstance(scope.get(key), str) or not scope[key].strip():
            raise BenchmarkTraceError(f"Trace scope requires {key}")

    milestones = _mapping(trace.get("milestones"), "session milestones")
    requested_at = _instant(milestones.get("requestedAt"), "requestedAt")
    quality_gate_at = _instant(milestones.get("qualityGateCompletedAt"), "qualityGateCompletedAt")
    quality_gate_seconds = _elapsed_seconds(
        requested_at, quality_gate_at, "qualityGateCompletedAt"
    )
    review_ready_seconds = None
    review_ready_value = milestones.get("reviewReadyAt")
    if review_ready_value is not None:
        review_ready_at = _instant(review_ready_value, "reviewReadyAt")
        if review_ready_at < quality_gate_at:
            raise BenchmarkTraceError("reviewReadyAt cannot precede qualityGateCompletedAt")
        review_ready_seconds = _elapsed_seconds(requested_at, review_ready_at, "reviewReadyAt")
    published_at_value = milestones.get("publishedAt")
    optional_publish_seconds = None
    if published_at_value is not None:
        published_at = _instant(published_at_value, "publishedAt")
        if published_at < quality_gate_at:
            raise BenchmarkTraceError("publishedAt cannot precede qualityGateCompletedAt")
        optional_publish_seconds = _elapsed_seconds(requested_at, published_at, "publishedAt")

    durations = _mapping(trace.get("durationsMs"), "duration breakdown")
    duration_seconds: dict[str, float] = {}
    for key in REQUIRED_DURATION_KEYS:
        value = durations.get(key)
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
            raise BenchmarkTraceError(f"Trace duration {key} must be a nonnegative number")
        duration_seconds[key] = value / 1000

    jobs = _list(trace.get("jobs"), "Job snapshots")
    standard_states = [
        state for state in (_stage_and_status(entry) for entry in jobs) if state[0] in STANDARD_STAGES
    ]
    if standard_states != [(stage, "completed") for stage in STANDARD_STAGES]:
        raise BenchmarkTraceError(
            "Trace must contain one completed Research, Brief, Writer, and Optimization Job in order"
        )

    operations = _mapping(trace.get("operations"), "operation evidence")
    lifecycle_writes = _list(operations.get("lifecycleWrites"), "lifecycleWrites")
    if lifecycle_writes != list(STANDARD_LIFECYCLE_WRITES):
        raise BenchmarkTraceError("Trace must contain the exact nine-write lifecycle in order")
    tool_round_trips = _list(operations.get("toolRoundTrips"), "toolRoundTrips")
    retries = _list(operations.get("retries"), "retries")
    browser_qa_calls = _list(operations.get("browserQaCalls"), "browserQaCalls")
    rebinding_jobs = _list(operations.get("rebindingJobs"), "rebindingJobs")
    late_attestation_failures = _list(
        operations.get("lateAttestationFailures"), "lateAttestationFailures"
    )
    tool_output_bytes = operations.get("toolOutputBytes")
    cms_draft_writes = operations.get("cmsDraftWrites")
    writer_source_submissions = operations.get("writerSourceSubmissions")
    if not isinstance(tool_output_bytes, int) or isinstance(tool_output_bytes, bool):
        raise BenchmarkTraceError("Trace operations.toolOutputBytes must be an integer")
    if tool_output_bytes < 0:
        raise BenchmarkTraceError("Trace operations.toolOutputBytes cannot be negative")
    if cms_draft_writes != 1:
        raise BenchmarkTraceError("Clean trace must contain exactly one CMS Draft write")
    if writer_source_submissions != 1:
        raise BenchmarkTraceError("Trace must contain exactly one Writer source submission")
    context_compactions = operations.get("contextCompactions")
    if not isinstance(context_compactions, int) or isinstance(context_compactions, bool):
        raise BenchmarkTraceError("Trace operations.contextCompactions must be an integer")
    if context_compactions < 0:
        raise BenchmarkTraceError("Trace operations.contextCompactions cannot be negative")

    quality_gate_target_met = quality_gate_seconds <= QUALITY_GATE_TARGET_SECONDS
    lifecycle_budget_met = len(lifecycle_writes) <= len(STANDARD_LIFECYCLE_WRITES)
    tool_round_trip_budget_met = len(tool_round_trips) <= TOOL_ROUND_TRIP_BUDGET
    tool_output_budget_met = tool_output_bytes <= TOOL_OUTPUT_BYTE_BUDGET
    no_context_compaction = context_compactions == 0
    no_browser_qa = len(browser_qa_calls) == 0
    no_rebinding_jobs = len(rebinding_jobs) == 0
    no_late_attestation_failure = len(late_attestation_failures) == 0
    target_met = all(
        (
            quality_gate_target_met,
            lifecycle_budget_met,
            tool_round_trip_budget_met,
            tool_output_budget_met,
            no_context_compaction,
            no_browser_qa,
            no_rebinding_jobs,
            no_late_attestation_failure,
        )
    )

    reduction_fraction = (
        baseline_quality_gate_seconds - quality_gate_seconds
    ) / baseline_quality_gate_seconds
    return {
        "scope": scope,
        "baselineQualityGateSeconds": baseline_quality_gate_seconds,
        "qualityGateSeconds": quality_gate_seconds,
        "reviewReadySeconds": review_ready_seconds,
        "optionalPublishSeconds": optional_publish_seconds,
        "qualityGateReductionPercent": round(reduction_fraction * 100, 2),
        "durationsSeconds": duration_seconds,
        "qualityGateTargetSeconds": QUALITY_GATE_TARGET_SECONDS,
        "qualityGateTargetMet": quality_gate_target_met,
        "lifecycleWrites": len(lifecycle_writes),
        "lifecycleWriteBudget": len(STANDARD_LIFECYCLE_WRITES),
        "lifecycleWriteBudgetMet": lifecycle_budget_met,
        "toolRoundTrips": len(tool_round_trips),
        "toolRoundTripBudget": TOOL_ROUND_TRIP_BUDGET,
        "toolRoundTripBudgetMet": tool_round_trip_budget_met,
        "toolOutputBytes": tool_output_bytes,
        "toolOutputByteBudget": TOOL_OUTPUT_BYTE_BUDGET,
        "toolOutputBudgetMet": tool_output_budget_met,
        "cmsDraftWrites": cms_draft_writes,
        "writerSourceSubmissions": writer_source_submissions,
        "retries": len(retries),
        "contextCompactions": context_compactions,
        "noContextCompaction": no_context_compaction,
        "noBrowserQa": no_browser_qa,
        "noRebindingJobs": no_rebinding_jobs,
        "noLateAttestationFailure": no_late_attestation_failure,
        "targetMet": target_met,
        "stages": list(STANDARD_STAGES),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session-trace", required=True, type=Path)
    parser.add_argument("--baseline-quality-gate-seconds", type=float, default=36 * 60 + 59)
    parser.add_argument("--require-target", action="store_true")
    args = parser.parse_args()

    try:
        trace = json.loads(args.session_trace.read_text(encoding="utf-8"))
        result = benchmark_trace(trace, args.baseline_quality_gate_seconds)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, BenchmarkTraceError) as error:
        parser.error(str(error))

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not args.require_target or result["targetMet"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

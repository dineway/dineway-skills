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
    "comparisonBasis": "workflow_artifacts_fields",
    "researchContract": "research-v2",
    "briefContract": "brief-v2",
}
CONTENT_READY_TARGET_SECONDS = 18 * 60
REVIEW_READY_TARGET_SECONDS = 22 * 60
HARD_CEILING_SECONDS = 25 * 60
EXTERNAL_CALL_BUDGET = 50


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
    baseline_review_seconds: float,
) -> dict[str, Any]:
    if baseline_review_seconds <= 0:
        raise BenchmarkTraceError("Baseline Review-ready duration must be positive")

    protocol = _mapping(trace.get("protocol"), "protocol identity")
    if protocol.get("version") != 2 or protocol.get("resultContractVersion") != 2:
        raise BenchmarkTraceError("Trace requires Pipeline protocol 2 and Result contract 2")

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
    content_ready_at = _instant(milestones.get("contentReadyAt"), "contentReadyAt")
    review_ready_at = _instant(milestones.get("reviewReadyAt"), "reviewReadyAt")
    benchmark_completed_at = _instant(
        milestones.get("benchmarkCompletedAt"), "benchmarkCompletedAt"
    )
    if not requested_at <= content_ready_at <= review_ready_at <= benchmark_completed_at:
        raise BenchmarkTraceError(
            "Milestones must be ordered requested -> content-ready -> review-ready -> benchmark-complete"
        )
    content_ready_seconds = _elapsed_seconds(requested_at, content_ready_at, "contentReadyAt")
    review_ready_seconds = _elapsed_seconds(requested_at, review_ready_at, "reviewReadyAt")
    benchmark_seconds = _elapsed_seconds(
        requested_at, benchmark_completed_at, "benchmarkCompletedAt"
    )
    published_at_value = milestones.get("publishedAt")
    optional_publish_seconds = None
    if published_at_value is not None:
        published_at = _instant(published_at_value, "publishedAt")
        if published_at < review_ready_at:
            raise BenchmarkTraceError("publishedAt cannot precede reviewReadyAt")
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
    external_calls = _list(operations.get("externalCalls"), "externalCalls")
    retries = _list(operations.get("retries"), "retries")
    legacy_fallbacks = _list(operations.get("legacyFallbacks"), "legacyFallbacks")
    browser_qa_calls = _list(operations.get("browserQaCalls"), "browserQaCalls")
    context_compactions = operations.get("contextCompactions")
    if not isinstance(context_compactions, int) or isinstance(context_compactions, bool):
        raise BenchmarkTraceError("Trace operations.contextCompactions must be an integer")
    if context_compactions < 0:
        raise BenchmarkTraceError("Trace operations.contextCompactions cannot be negative")

    content_target_met = content_ready_seconds <= CONTENT_READY_TARGET_SECONDS
    review_target_met = review_ready_seconds <= REVIEW_READY_TARGET_SECONDS
    hard_ceiling_met = benchmark_seconds <= HARD_CEILING_SECONDS
    lifecycle_budget_met = len(lifecycle_writes) <= len(STANDARD_LIFECYCLE_WRITES)
    external_call_budget_met = len(external_calls) <= EXTERNAL_CALL_BUDGET
    no_context_compaction = context_compactions == 0
    no_legacy_fallback = len(legacy_fallbacks) == 0
    no_browser_qa = len(browser_qa_calls) == 0
    target_met = all(
        (
            content_target_met,
            review_target_met,
            hard_ceiling_met,
            lifecycle_budget_met,
            external_call_budget_met,
            no_context_compaction,
            no_legacy_fallback,
            no_browser_qa,
        )
    )

    reduction_fraction = (baseline_review_seconds - review_ready_seconds) / baseline_review_seconds
    return {
        "protocolVersion": protocol["version"],
        "resultContractVersion": protocol["resultContractVersion"],
        "scope": scope,
        "baselineReviewReadySeconds": baseline_review_seconds,
        "contentReadySeconds": content_ready_seconds,
        "reviewReadySeconds": review_ready_seconds,
        "benchmarkSeconds": benchmark_seconds,
        "optionalPublishSeconds": optional_publish_seconds,
        "reviewReadyReductionPercent": round(reduction_fraction * 100, 2),
        "durationsSeconds": duration_seconds,
        "contentReadyTargetSeconds": CONTENT_READY_TARGET_SECONDS,
        "reviewReadyTargetSeconds": REVIEW_READY_TARGET_SECONDS,
        "hardCeilingSeconds": HARD_CEILING_SECONDS,
        "contentReadyTargetMet": content_target_met,
        "reviewReadyTargetMet": review_target_met,
        "hardCeilingMet": hard_ceiling_met,
        "lifecycleWrites": len(lifecycle_writes),
        "lifecycleWriteBudget": len(STANDARD_LIFECYCLE_WRITES),
        "lifecycleWriteBudgetMet": lifecycle_budget_met,
        "externalCalls": len(external_calls),
        "externalCallBudget": EXTERNAL_CALL_BUDGET,
        "externalCallBudgetMet": external_call_budget_met,
        "retries": len(retries),
        "contextCompactions": context_compactions,
        "noContextCompaction": no_context_compaction,
        "noLegacyFallback": no_legacy_fallback,
        "noBrowserQa": no_browser_qa,
        "targetMet": target_met,
        "stages": list(STANDARD_STAGES),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session-trace", required=True, type=Path)
    parser.add_argument("--baseline-review-seconds", type=float, default=18 * 60)
    parser.add_argument("--require-target", action="store_true")
    args = parser.parse_args()

    try:
        trace = json.loads(args.session_trace.read_text(encoding="utf-8"))
        result = benchmark_trace(trace, args.baseline_review_seconds)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, BenchmarkTraceError) as error:
        parser.error(str(error))

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not args.require_target or result["targetMet"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

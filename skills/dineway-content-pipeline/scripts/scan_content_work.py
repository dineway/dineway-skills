#!/usr/bin/env python3
"""Derive a local Pipeline Run view from authoritative Dineway state and cached artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


CONTRACT_VERSION = 5
IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
STAGE_ARTIFACTS = {
    "research": ("research/evidence.json", "research/findings.md"),
    "brief": ("brief/brief.md",),
    "writer": ("cms/draft-receipt.json",),
    "optimization": ("optimize/report.json",),
    "geo_optimization": ("geo/report.json",),
    "competition": ("competition/report.json",),
    "ai_visibility": ("ai-visibility/report.json",),
    "atomization": ("atomization/manifest.json",),
    "site_analysis": ("site-analysis/report.json",),
    "monitor": ("monitor/evidence.json",),
    "fix": ("cms/draft-receipt.json",),
}
def read_json(path: Path, errors: list[str]) -> Any:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        errors.append(f"{path.relative_to(path.parents[1])}: {error}")
        return None


def nonempty(path: Path) -> bool:
    try:
        return path.is_file() and bool(path.read_text(encoding="utf-8").strip())
    except (OSError, UnicodeDecodeError):
        return False


def file_receipt(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    data = path.read_bytes()
    return {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def artifact_receipts(job_dir: Path, stage_name: str) -> dict[str, dict[str, Any]]:
    return {
        relative: receipt
        for relative in STAGE_ARTIFACTS.get(stage_name, ())
        if (receipt := file_receipt(job_dir / relative)) is not None
    }


def stage_artifacts_complete(job_dir: Path, stage_name: str) -> bool:
    required = STAGE_ARTIFACTS.get(stage_name, ())
    return bool(required) and all(nonempty(job_dir / relative) for relative in required)


def exact_draft_matches(result: Any, content: Any) -> bool:
    if not isinstance(result, dict) or not isinstance(content, dict):
        return False
    return (
        result.get("collection") == content.get("collection")
        and result.get("contentId") == content.get("id")
        and result.get("draftRevisionId") == content.get("draftRevisionId")
    )


def scan(run_dir: Path) -> dict[str, Any]:
    errors: list[str] = []
    native = read_json(run_dir / "native-state.json", errors)
    native_status = native.get("status") if isinstance(native, dict) else None
    if not isinstance(native_status, dict):
        native_status = native if isinstance(native, dict) else None
    native_run = native_status.get("run") if isinstance(native_status, dict) else None
    native_jobs = native_status.get("jobs") if isinstance(native_status, dict) else None
    native_current_stage = (
        native_status.get("currentStage") if isinstance(native_status, dict) else None
    )
    native_next_action = (
        native_status.get("nextAction") if isinstance(native_status, dict) else None
    )
    native_timing = native_status.get("timing") if isinstance(native_status, dict) else None
    content = native.get("content") if isinstance(native, dict) else None
    calendar = native.get("calendar") if isinstance(native, dict) else None
    review = native.get("review") if isinstance(native, dict) else None
    release_readiness = native.get("releaseReadiness") if isinstance(native, dict) else None

    if not isinstance(native_run, dict) or native_run.get("id") != run_dir.name:
        errors.append("Native Pipeline Run identity does not match the local run directory.")
    if not isinstance(native_jobs, list):
        native_jobs = []
        errors.append("Native Pipeline Job state is unavailable.")

    job_views: list[dict[str, Any]] = []
    recovery_action: tuple[str, str, str | None] | None = None
    for entry in native_jobs:
        if not isinstance(entry, dict) or not isinstance(entry.get("job"), dict):
            errors.append("A native Job snapshot is malformed.")
            continue
        job = entry["job"]
        job_id = job.get("id")
        stage_name = job.get("stage")
        if not isinstance(job_id, str) or not isinstance(stage_name, str):
            errors.append("A native Job is missing its ID or stage.")
            continue
        job_dir = run_dir / "jobs" / job_id
        local_result = read_json(job_dir / "result-receipt.json", errors)
        accepted_result = entry.get("acceptedResult")
        candidate_result = entry.get("candidateResult")
        active_assignment = entry.get("activeAssignment")
        pending_handoff = entry.get("pendingHandoff")
        result_current = accepted_result is None or local_result == accepted_result
        artifacts_complete = stage_artifacts_complete(job_dir, stage_name)
        revision_current = True
        revision_bound = stage_name in {"writer", "optimization", "geo_optimization", "atomization", "fix"}
        if revision_bound and isinstance(accepted_result, dict):
            revision_current = exact_draft_matches(accepted_result, content)
            if not revision_current:
                errors.append(f"Job {job_id} Result does not reference the current CMS Draft Revision.")
        if accepted_result is not None and not result_current:
            errors.append(f"Job {job_id} local Result receipt differs from authoritative state.")

        if isinstance(pending_handoff, dict):
            assignment_id = active_assignment.get("id") if isinstance(active_assignment, dict) else None
            if (
                pending_handoff.get("jobId") != job_id
                or pending_handoff.get("fromAssignmentId") != assignment_id
            ):
                recovery_action = (stage_name, "refresh_native_handoff", job_id)
                errors.append(f"Job {job_id} Handoff does not match its active Assignment.")
            elif recovery_action is None:
                recovery_action = (stage_name, "accept_or_reject_handoff", job_id)
        elif isinstance(active_assignment, dict) and active_assignment.get("status") == "expired":
            recovery_action = recovery_action or (stage_name, "reacquire_assignment", job_id)
        elif job.get("status") == "failed":
            recovery_action = recovery_action or (stage_name, "retry_stage", job_id)

        job_views.append(
            {
                "jobId": job_id,
                "stage": stage_name,
                "status": job.get("status"),
                "version": job.get("version"),
                "assignmentId": (
                    active_assignment.get("id") if isinstance(active_assignment, dict) else None
                ),
                "acceptedResultId": (
                    accepted_result.get("id") if isinstance(accepted_result, dict) else None
                ),
                "candidateResultId": (
                    candidate_result.get("id") if isinstance(candidate_result, dict) else None
                ),
                "artifactsComplete": artifacts_complete,
                "resultReceiptCurrent": result_current,
                "draftRevisionCurrent": revision_current,
                "artifacts": artifact_receipts(job_dir, stage_name),
            }
        )

    current_stage = native_current_stage if isinstance(native_current_stage, str) else "research"
    next_action = native_next_action if isinstance(native_next_action, str) else "begin_research"
    current_job_id: str | None = None
    if not isinstance(native_current_stage, str) or not isinstance(native_next_action, str):
        errors.append("Native Pipeline status is missing currentStage or nextAction.")
    overdue = isinstance(calendar, dict) and calendar.get("assignmentStatus") == "overdue"
    if recovery_action is not None:
        current_stage, next_action, current_job_id = recovery_action
    elif overdue:
        current_stage, next_action = "calendar", "reevaluate_overdue"
    elif job_views:
        current = job_views[-1]
        current_job_id = current["jobId"]
        if current["acceptedResultId"]:
            if not current["resultReceiptCurrent"]:
                next_action = "refresh_result_receipt"
            elif not current["artifactsComplete"]:
                next_action = "refresh_derived_artifacts"
            elif not current["draftRevisionCurrent"]:
                next_action = "refresh_current_draft_and_retry"

    draft_revision_id = content.get("draftRevisionId") if isinstance(content, dict) else None
    review_current = (
        isinstance(review, dict)
        and review.get("status") == "approved"
        and review.get("draftRevisionId") == draft_revision_id
    )
    release_current = isinstance(release_readiness, dict) and release_readiness.get("ready") is True

    return {
        "contractVersion": CONTRACT_VERSION,
        "runId": run_dir.name,
        "runStatus": native_run.get("status") if isinstance(native_run, dict) else None,
        "runVersion": native_run.get("version") if isinstance(native_run, dict) else None,
        "currentStage": current_stage,
        "currentJobId": current_job_id,
        "nextAction": next_action,
        "timing": native_timing if isinstance(native_timing, dict) else None,
        "cms": {
            "collection": content.get("collection") if isinstance(content, dict) else None,
            "contentId": content.get("id") if isinstance(content, dict) else None,
            "draftRevisionId": draft_revision_id,
            "reviewCurrent": review_current,
            "releaseCurrent": release_current,
        },
        "jobs": job_views,
        "errors": errors,
    }


def write_status(run_dir: Path, result: dict[str, Any]) -> None:
    target = run_dir / "status.json"
    temporary = run_dir / ".status.json.tmp"
    temporary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(target)


def run_directories(root: Path, run_id: str | None) -> list[Path]:
    if run_id is not None:
        if not IDENTIFIER.fullmatch(run_id):
            raise ValueError("Invalid Pipeline Run ID")
        return [root / run_id]
    if not root.is_dir():
        return []
    return sorted(path for path in root.iterdir() if path.is_dir() and IDENTIFIER.fullmatch(path.name))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default=".", help="Dineway site workspace root")
    parser.add_argument("--run", help="Scan only this authoritative Pipeline Run ID")
    parser.add_argument("--write", action="store_true", help="Write derived status.json files")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    root = Path(args.workspace).resolve() / ".dineway" / "content" / "runs"
    try:
        directories = run_directories(root, args.run)
    except ValueError as error:
        parser.error(str(error))

    results = []
    for run_dir in directories:
        result = scan(run_dir)
        if args.write:
            run_dir.mkdir(parents=True, exist_ok=True)
            write_status(run_dir, result)
        results.append(result)

    print(
        json.dumps(
            {"contractVersion": CONTRACT_VERSION, "items": results},
            indent=2 if args.pretty else None,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

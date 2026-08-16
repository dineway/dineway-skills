import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("benchmark_pipeline_trace.py")
MODULE_SPEC = importlib.util.spec_from_file_location("benchmark_pipeline_trace", MODULE_PATH)
if MODULE_SPEC is None or MODULE_SPEC.loader is None:
    raise RuntimeError("Unable to load benchmark_pipeline_trace.py")
MODULE = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(MODULE)
BenchmarkTraceError = MODULE.BenchmarkTraceError
benchmark_trace = MODULE.benchmark_trace


STANDARD_WRITES = [
    "run_start",
    "research_begin",
    "research_complete",
    "brief_begin",
    "brief_complete",
    "writer_begin",
    "writer_complete",
    "optimization_begin",
    "optimization_complete",
]


def completed_trace() -> dict:
    return {
        "scope": {
            "comparable": True,
            "comparisonBasis": "four_stage_article",
            "contentType": "article",
            "locale": "en-SG",
        },
        "milestones": {
            "requestedAt": "2026-08-13T00:00:00Z",
            "qualityGateCompletedAt": "2026-08-13T00:14:00Z",
            "reviewReadyAt": "2026-08-13T00:18:00Z",
            "publishedAt": "2026-08-13T00:25:00Z",
        },
        "durationsMs": {
            "humanApprovalWait": 60_000,
            "toolExecution": 420_000,
            "agentReasoning": 540_000,
            "orchestration": 120_000,
            "qa": 60_000,
        },
        "operations": {
            "lifecycleWrites": list(STANDARD_WRITES),
            "toolRoundTrips": [f"call-{index}" for index in range(42)],
            "toolOutputBytes": 320_000,
            "cmsDraftWrites": 1,
            "writerSourceSubmissions": 1,
            "retries": [],
            "contextCompactions": 0,
            "browserQaCalls": [],
            "rebindingJobs": [],
            "lateAttestationFailures": [],
        },
        "jobs": [
            {"job": {"stage": stage, "status": "completed"}}
            for stage in ("research", "brief", "writer", "optimization")
        ],
    }


class BenchmarkPipelineTraceTest(unittest.TestCase):
    def test_reports_quality_gate_and_keeps_review_and_publication_separate(self) -> None:
        result = benchmark_trace(completed_trace(), baseline_quality_gate_seconds=36 * 60 + 59)

        self.assertEqual(result["qualityGateSeconds"], 14 * 60)
        self.assertEqual(result["reviewReadySeconds"], 18 * 60)
        self.assertEqual(result["optionalPublishSeconds"], 25 * 60)
        self.assertTrue(result["qualityGateTargetMet"])
        self.assertTrue(result["targetMet"])
        self.assertEqual(result["lifecycleWrites"], 9)
        self.assertEqual(result["toolRoundTrips"], 42)
        self.assertEqual(result["toolOutputBytes"], 320_000)
        self.assertAlmostEqual(result["qualityGateReductionPercent"], 62.15, places=2)

    def test_rejects_missing_scope_milestones_or_standard_stages(self) -> None:
        for mutation in ("scope", "milestone", "stage"):
            trace = completed_trace()
            if mutation == "scope":
                trace["scope"]["comparable"] = False
            elif mutation == "milestone":
                del trace["milestones"]["qualityGateCompletedAt"]
            else:
                trace["jobs"] = list(reversed(trace["jobs"]))
            with self.subTest(mutation=mutation), self.assertRaises(BenchmarkTraceError):
                benchmark_trace(trace, baseline_quality_gate_seconds=36 * 60 + 59)

    def test_fails_targets_for_time_call_or_forbidden_path_regressions(self) -> None:
        trace = completed_trace()
        trace["milestones"].update(
            {
                "qualityGateCompletedAt": "2026-08-13T00:16:00Z",
                "reviewReadyAt": "2026-08-13T00:23:00Z",
            }
        )
        trace["operations"]["toolRoundTrips"] = [f"call-{index}" for index in range(51)]
        trace["operations"]["toolOutputBytes"] = 409_601
        trace["operations"]["contextCompactions"] = 1
        trace["operations"]["browserQaCalls"] = ["screenshot"]
        trace["operations"]["rebindingJobs"] = ["writer-rebind"]
        trace["operations"]["lateAttestationFailures"] = ["missing-fingerprint"]

        result = benchmark_trace(trace, baseline_quality_gate_seconds=36 * 60 + 59)

        self.assertFalse(result["qualityGateTargetMet"])
        self.assertFalse(result["toolRoundTripBudgetMet"])
        self.assertFalse(result["toolOutputBudgetMet"])
        self.assertFalse(result["noContextCompaction"])
        self.assertFalse(result["noBrowserQa"])
        self.assertFalse(result["noRebindingJobs"])
        self.assertFalse(result["noLateAttestationFailure"])
        self.assertFalse(result["targetMet"])

    def test_rejects_missing_duration_or_structural_operation_evidence(self) -> None:
        for mutation in ("duration", "write", "operations"):
            trace = completed_trace()
            if mutation == "duration":
                del trace["durationsMs"]["qa"]
            elif mutation == "write":
                trace["operations"]["lifecycleWrites"].pop()
            else:
                del trace["operations"]["toolRoundTrips"]
            with self.subTest(mutation=mutation), self.assertRaises(BenchmarkTraceError):
                benchmark_trace(trace, baseline_quality_gate_seconds=36 * 60 + 59)


if __name__ == "__main__":
    unittest.main()

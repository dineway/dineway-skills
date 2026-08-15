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
        "protocol": {"version": 2, "resultContractVersion": 2},
        "scope": {
            "comparable": True,
            "comparisonBasis": "workflow_artifacts_fields",
            "contentType": "article",
            "locale": "en-SG",
            "researchContract": "research-v2",
            "briefContract": "brief-v2",
        },
        "milestones": {
            "requestedAt": "2026-08-13T00:00:00Z",
            "contentReadyAt": "2026-08-13T00:16:00Z",
            "reviewReadyAt": "2026-08-13T00:20:00Z",
            "benchmarkCompletedAt": "2026-08-13T00:23:00Z",
            "publishedAt": "2026-08-13T00:27:00Z",
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
            "externalCalls": [f"call-{index}" for index in range(42)],
            "retries": [],
            "contextCompactions": 0,
            "legacyFallbacks": [],
            "browserQaCalls": [],
        },
        "jobs": [
            {"job": {"stage": stage, "status": "completed"}}
            for stage in ("research", "brief", "writer", "optimization")
        ],
    }


class BenchmarkPipelineTraceTest(unittest.TestCase):
    def test_reports_two_time_gates_and_keeps_publication_separate(self) -> None:
        result = benchmark_trace(completed_trace(), baseline_review_seconds=18 * 60)

        self.assertEqual(result["contentReadySeconds"], 16 * 60)
        self.assertEqual(result["reviewReadySeconds"], 20 * 60)
        self.assertEqual(result["benchmarkSeconds"], 23 * 60)
        self.assertEqual(result["optionalPublishSeconds"], 27 * 60)
        self.assertTrue(result["contentReadyTargetMet"])
        self.assertTrue(result["reviewReadyTargetMet"])
        self.assertTrue(result["hardCeilingMet"])
        self.assertTrue(result["targetMet"])
        self.assertEqual(result["lifecycleWrites"], 9)
        self.assertEqual(result["externalCalls"], 42)
        self.assertAlmostEqual(result["reviewReadyReductionPercent"], -11.11, places=2)

    def test_rejects_missing_protocol_scope_milestones_or_standard_stages(self) -> None:
        for mutation in ("protocol", "scope", "milestone", "stage"):
            trace = completed_trace()
            if mutation == "protocol":
                trace["protocol"]["resultContractVersion"] = 1
            elif mutation == "scope":
                trace["scope"]["comparable"] = False
            elif mutation == "milestone":
                del trace["milestones"]["contentReadyAt"]
            else:
                trace["jobs"] = list(reversed(trace["jobs"]))
            with self.subTest(mutation=mutation), self.assertRaises(BenchmarkTraceError):
                benchmark_trace(trace, baseline_review_seconds=18 * 60)

    def test_fails_targets_for_time_call_or_forbidden_path_regressions(self) -> None:
        trace = completed_trace()
        trace["milestones"].update(
            {
                "contentReadyAt": "2026-08-13T00:19:00Z",
                "reviewReadyAt": "2026-08-13T00:23:00Z",
                "benchmarkCompletedAt": "2026-08-13T00:26:00Z",
            }
        )
        trace["operations"]["externalCalls"] = [f"call-{index}" for index in range(51)]
        trace["operations"]["contextCompactions"] = 1
        trace["operations"]["legacyFallbacks"] = ["granular_result_record"]
        trace["operations"]["browserQaCalls"] = ["screenshot"]

        result = benchmark_trace(trace, baseline_review_seconds=18 * 60)

        self.assertFalse(result["contentReadyTargetMet"])
        self.assertFalse(result["reviewReadyTargetMet"])
        self.assertFalse(result["hardCeilingMet"])
        self.assertFalse(result["externalCallBudgetMet"])
        self.assertFalse(result["noContextCompaction"])
        self.assertFalse(result["noLegacyFallback"])
        self.assertFalse(result["noBrowserQa"])
        self.assertFalse(result["targetMet"])

    def test_rejects_missing_duration_or_structural_operation_evidence(self) -> None:
        for mutation in ("duration", "write", "operations"):
            trace = completed_trace()
            if mutation == "duration":
                del trace["durationsMs"]["qa"]
            elif mutation == "write":
                trace["operations"]["lifecycleWrites"].pop()
            else:
                del trace["operations"]["externalCalls"]
            with self.subTest(mutation=mutation), self.assertRaises(BenchmarkTraceError):
                benchmark_trace(trace, baseline_review_seconds=18 * 60)


if __name__ == "__main__":
    unittest.main()

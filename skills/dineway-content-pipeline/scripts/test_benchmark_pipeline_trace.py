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


def completed_trace(elapsed_ms: int = 20 * 60 * 1000) -> dict:
    return {
        "timing": {
            "elapsedMs": elapsed_ms,
            "agentWorkMs": 18 * 60 * 1000,
            "orchestrationMs": 2 * 60 * 1000,
        },
        "jobs": [
            {"job": {"stage": stage, "status": "completed"}}
            for stage in ("research", "brief", "writer", "optimization")
        ],
    }


class BenchmarkPipelineTraceTest(unittest.TestCase):
    def test_reports_target_and_structural_budget_for_equivalent_trace(self) -> None:
        result = benchmark_trace(completed_trace(), baseline_publish_seconds=54 * 60 + 9)

        self.assertEqual(result["optimizedPublishSeconds"], 20 * 60)
        self.assertEqual(result["structuralLifecycleCalls"], 9)
        self.assertTrue(result["structuralCallBudgetMet"])
        self.assertTrue(result["targetMet"])
        self.assertAlmostEqual(result["reductionPercent"], 63.07, places=2)

    def test_rejects_missing_or_out_of_order_standard_stages(self) -> None:
        trace = completed_trace()
        trace["jobs"] = list(reversed(trace["jobs"]))

        with self.assertRaises(BenchmarkTraceError):
            benchmark_trace(trace, baseline_publish_seconds=54 * 60 + 9)

    def test_can_fail_the_elapsed_target_without_invalidating_the_trace(self) -> None:
        result = benchmark_trace(
            completed_trace(elapsed_ms=30 * 60 * 1000),
            baseline_publish_seconds=54 * 60 + 9,
        )

        self.assertFalse(result["targetMet"])
        self.assertTrue(result["structuralCallBudgetMet"])


if __name__ == "__main__":
    unittest.main()

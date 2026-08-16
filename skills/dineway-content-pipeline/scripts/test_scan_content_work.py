import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("scan_content_work.py")
MODULE_SPEC = importlib.util.spec_from_file_location("scan_content_work", MODULE_PATH)
if MODULE_SPEC is None or MODULE_SPEC.loader is None:
    raise RuntimeError("Unable to load scan_content_work.py")
MODULE = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(MODULE)
scan = MODULE.scan


class ScanContentWorkTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.run_dir = Path(self.temporary.name) / "run-1"
        self.run_dir.mkdir()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_json(self, relative: str, value: object) -> None:
        target = self.run_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(value), encoding="utf-8")

    def write_text(self, relative: str, value: str) -> None:
        target = self.run_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(value, encoding="utf-8")

    def result(self, kind: str, job_id: str, draft_revision_id: str | None = None) -> dict:
        return {
            "id": f"result-{job_id}",
            "jobId": job_id,
            "kind": kind,
            "collection": "posts" if draft_revision_id else None,
            "contentId": "post-1" if draft_revision_id else None,
            "draftRevisionId": draft_revision_id,
        }

    def state(
        self,
        entries: list[dict],
        *,
        current_stage: str = "research",
        next_action: str = "begin_research",
    ) -> dict:
        return {
            "status": {
                "run": {"id": "run-1", "status": "active", "version": 4},
                "jobs": entries,
                "currentStage": current_stage,
                "nextAction": next_action,
                "timing": {
                    "elapsedMs": 480000,
                    "agentWorkMs": 300000,
                    "orchestrationMs": 180000,
                },
            },
            "content": {
                "collection": "posts",
                "id": "post-1",
                "draftRevisionId": "draft-2",
            },
            "calendar": {"assignmentStatus": "scheduled"},
            "review": None,
            "release": None,
        }

    def job_entry(
        self,
        stage: str,
        job_id: str,
        *,
        accepted: dict | None = None,
        candidate: dict | None = None,
        status: str = "completed",
        assignment: dict | None = None,
        handoff: dict | None = None,
    ) -> dict:
        return {
            "job": {"id": job_id, "stage": stage, "status": status, "version": 3},
            "activeAssignment": assignment,
            "pendingHandoff": handoff,
            "acceptedResult": accepted,
            "candidateResult": candidate,
        }

    def test_starts_with_research_from_authoritative_run_identity(self) -> None:
        self.write_json("native-state.json", self.state([]))
        result = scan(self.run_dir)
        self.assertEqual(result["nextAction"], "begin_research")
        self.assertEqual(result["runId"], "run-1")
        self.assertEqual(result["timing"]["orchestrationMs"], 180000)

    def test_requires_human_approval_for_candidate_brief(self) -> None:
        candidate = self.result("brief", "job-brief")
        self.write_json(
            "native-state.json",
            self.state(
                [self.job_entry("brief", "job-brief", candidate=candidate)],
                current_stage="brief",
                next_action="confirm_brief",
            ),
        )
        self.write_text("jobs/job-brief/brief/brief.md", "# Brief")
        result = scan(self.run_dir)
        self.assertEqual(result["nextAction"], "confirm_brief")

    def test_refreshes_a_result_receipt_that_differs_from_authority(self) -> None:
        accepted = self.result("research", "job-research")
        self.write_json(
            "native-state.json",
            self.state([self.job_entry("research", "job-research", accepted=accepted)]),
        )
        self.write_json("jobs/job-research/result-receipt.json", {"id": "stale"})
        self.write_json("jobs/job-research/research/evidence.json", {"sources": []})
        self.write_text("jobs/job-research/research/findings.md", "Findings")
        result = scan(self.run_dir)
        self.assertEqual(result["nextAction"], "refresh_result_receipt")
        self.assertTrue(any("differs" in error for error in result["errors"]))

    def test_rejects_a_revision_bound_result_for_an_old_draft(self) -> None:
        accepted = self.result("optimization", "job-optimize", "draft-1")
        self.write_json(
            "native-state.json",
            self.state([self.job_entry("optimization", "job-optimize", accepted=accepted)]),
        )
        self.write_json("jobs/job-optimize/result-receipt.json", accepted)
        self.write_json("jobs/job-optimize/optimize/report.json", {"score": 70})
        result = scan(self.run_dir)
        self.assertEqual(result["nextAction"], "refresh_current_draft_and_retry")
        self.assertFalse(result["jobs"][0]["draftRevisionCurrent"])

    def test_handoff_recovery_precedes_stage_execution(self) -> None:
        assignment = {"id": "assignment-1", "status": "active"}
        handoff = {
            "id": "handoff-1",
            "jobId": "job-research",
            "fromAssignmentId": "assignment-1",
        }
        self.write_json(
            "native-state.json",
            self.state(
                [
                    self.job_entry(
                        "research",
                        "job-research",
                        status="running",
                        assignment=assignment,
                        handoff=handoff,
                    )
                ]
            ),
        )
        result = scan(self.run_dir)
        self.assertEqual(result["nextAction"], "accept_or_reject_handoff")

    def test_overdue_calendar_work_requires_reevaluation(self) -> None:
        state = self.state([])
        state["calendar"] = {"assignmentStatus": "overdue"}
        self.write_json("native-state.json", state)
        result = scan(self.run_dir)
        self.assertEqual(result["nextAction"], "reevaluate_overdue")

    def test_skips_optional_deep_geo_without_run_policy(self) -> None:
        accepted = self.result("optimization", "job-optimize", "draft-2")
        self.write_json(
            "native-state.json",
            self.state(
                [self.job_entry("optimization", "job-optimize", accepted=accepted)],
                current_stage="release_readiness",
                next_action="inspect_release_readiness",
            ),
        )
        self.write_json("jobs/job-optimize/result-receipt.json", accepted)
        self.write_json("jobs/job-optimize/optimize/report.json", {"score": 80})
        result = scan(self.run_dir)
        self.assertEqual(result["nextAction"], "inspect_release_readiness")

    def test_runs_deep_geo_when_enabled_by_run_policy(self) -> None:
        accepted = self.result("optimization", "job-optimize", "draft-2")
        state = self.state(
            [self.job_entry("optimization", "job-optimize", accepted=accepted)],
            current_stage="geo_optimization",
            next_action="begin_geo_optimization",
        )
        state["status"]["run"]["metadata"] = {"deepGeoEnabled": True}
        self.write_json("native-state.json", state)
        self.write_json("jobs/job-optimize/result-receipt.json", accepted)
        self.write_json("jobs/job-optimize/optimize/report.json", {"score": 80})
        result = scan(self.run_dir)
        self.assertEqual(result["nextAction"], "begin_geo_optimization")


if __name__ == "__main__":
    unittest.main()

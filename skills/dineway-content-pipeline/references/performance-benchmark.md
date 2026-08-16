# Content Pipeline Complete-session Performance Benchmark

Benchmark the workflow through Team Review, not publication. Record optional
publication separately. The trace is authoritative only when it covers comparable workflow steps,
artifact outlines, and field contracts; topic and slug may differ.

## Required trace

Write one session trace with:

- comparable four-stage article scope;
- request, quality-gate, optional Review-ready, and optional publish instants;
- human-approval wait, tool execution, Agent reasoning, orchestration, and QA durations;
- the exact nine lifecycle writes in order;
- every Agent-to-tool round trip, total tool-output bytes, retry, browser-QA call, and
  context-compaction count;
- exactly one Writer source submission and one clean-path CMS Draft write, with no rebinding Job or
  late Attestation failure; and
- exactly one completed Research, Brief, Writer, and Optimization Job in order.

Example skeleton:

```json
{
  "scope": {
    "comparable": true,
    "comparisonBasis": "four_stage_article",
    "contentType": "article",
    "locale": "en-SG"
  },
  "milestones": {
    "requestedAt": "2026-08-13T00:00:00Z",
    "qualityGateCompletedAt": "2026-08-13T00:14:00Z",
    "reviewReadyAt": null,
    "publishedAt": null
  },
  "durationsMs": {
    "humanApprovalWait": 60000,
    "toolExecution": 420000,
    "agentReasoning": 540000,
    "orchestration": 120000,
    "qa": 60000
  },
  "operations": {
    "lifecycleWrites": [
      "run_start",
      "research_begin",
      "research_complete",
      "brief_begin",
      "brief_complete",
      "writer_begin",
      "writer_complete",
      "optimization_begin",
      "optimization_complete"
    ],
    "toolRoundTrips": [],
    "toolOutputBytes": 0,
    "cmsDraftWrites": 1,
    "writerSourceSubmissions": 1,
    "retries": [],
    "contextCompactions": 0,
    "browserQaCalls": [],
    "rebindingJobs": [],
    "lateAttestationFailures": []
  },
  "jobs": [
    { "job": { "stage": "research", "status": "completed" } },
    { "job": { "stage": "brief", "status": "completed" } },
    { "job": { "stage": "writer", "status": "completed" } },
    { "job": { "stage": "optimization", "status": "completed" } }
  ]
}
```

Run:

```bash
python3 skills/dineway-content-pipeline/scripts/benchmark_pipeline_trace.py \
  --session-trace .dineway/content/runs/<run-id>/session-trace.json \
  --baseline-quality-gate-seconds 2219 \
  --require-target
```

The benchmark fails closed when comparable scope, milestones, duration categories,
operation evidence, or ordered Jobs are missing. `--require-target` returns nonzero unless all gates
pass:

- quality-gate completion at or before 15 minutes;
- exactly nine lifecycle writes;
- no more than 50 Agent-to-tool round trips;
- no more than 400 KB total tool output;
- exactly one Writer source submission and one clean-path CMS Draft write;
- zero rebinding Jobs and zero late Attestation failures;
- zero context compactions;
- zero browser-QA calls.

Retries are counted and reported but are not an independent failure when every mandatory gate still
passes. Treat output as measured only for a completed equivalent article session; otherwise label it
a fixture or projection.

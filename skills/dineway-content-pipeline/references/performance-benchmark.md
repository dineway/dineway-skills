# Content Pipeline Complete-session Performance Benchmark

Benchmark the workflow through Team Review, not publication. Record optional
publication separately. The trace is authoritative only when it covers comparable workflow steps,
artifact outlines, and field contracts; topic and slug may differ.

## Required trace

Write one session trace with:

- protocol version 2 and Result contract version 2;
- comparable scope using `workflow_artifacts_fields`, `research-v2`, and `brief-v2`;
- request, Content-ready, Review-ready, benchmark-complete, and optional publish instants;
- human-approval wait, tool execution, Agent reasoning, orchestration, and QA durations;
- the exact nine lifecycle writes in order;
- every external call, retry, legacy fallback, browser-QA call, and context-compaction count; and
- exactly one completed Research, Brief, Writer, and Optimization Job in order.

Example skeleton:

```json
{
  "protocol": { "version": 2, "resultContractVersion": 2 },
  "scope": {
    "comparable": true,
    "comparisonBasis": "workflow_artifacts_fields",
    "contentType": "article",
    "locale": "en-SG",
    "researchContract": "research-v2",
    "briefContract": "brief-v2"
  },
  "milestones": {
    "requestedAt": "2026-08-13T00:00:00Z",
    "contentReadyAt": "2026-08-13T00:16:00Z",
    "reviewReadyAt": "2026-08-13T00:20:00Z",
    "benchmarkCompletedAt": "2026-08-13T00:23:00Z",
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
    "externalCalls": [],
    "retries": [],
    "contextCompactions": 0,
    "legacyFallbacks": [],
    "browserQaCalls": []
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
  --baseline-review-seconds 1080 \
  --require-target
```

The benchmark fails closed when protocol identity, comparable scope, milestones, duration categories,
operation evidence, or ordered Jobs are missing. `--require-target` returns nonzero unless all gates
pass:

- Content-ready at or before 18 minutes;
- Review-ready at or before 22 minutes;
- benchmark completion at or before the 25-minute hard ceiling;
- exactly nine lifecycle writes;
- no more than 50 external calls;
- zero context compactions;
- zero legacy fallbacks; and
- zero browser-QA calls.

Retries are counted and reported but are not an independent failure when every mandatory gate still
passes. Treat output as measured only for a completed equivalent article session; otherwise label it
a fixture or projection.

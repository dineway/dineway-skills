# Content Pipeline Performance Benchmark

Use the native Run status timing after final publication verification. The standard workflow must
contain exactly one completed `research`, `brief`, `writer`, and `optimization` Job in that order.
Optional deep GEO is reported separately and does not change the standard nine-call lifecycle budget:
one Run Start, four Stage Begin calls, and four Stage Complete calls.

The reference ausfoodtrip trace published in 54 minutes 9 seconds. Compare an equivalent optimized
trace without rewriting or hand-authoring timing data:

```bash
python3 skills/dineway-content-pipeline/scripts/benchmark_pipeline_trace.py \
  --optimized-status .dineway/content/runs/<run-id>/status.json \
  --baseline-publish-seconds 3249 \
  --target-publish-seconds 1500 \
  --require-target
```

The command fails closed when native timing is absent, the four standard Jobs are missing or reordered,
or `--require-target` is set and either the 25-minute elapsed target or nine-call structural budget is
missed. Treat the reported reduction as measured only when the optimized status comes from a completed
equivalent article Run; otherwise label it a projection or harness result.

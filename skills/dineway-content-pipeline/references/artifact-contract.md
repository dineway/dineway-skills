# Pipeline Local Artifact Contract

`.dineway/content/` is reconstructable Agent working memory. Native Pipeline/CMS state is the
authority. Local files never grant permission to mutate, approve, attest, schedule, or publish.

## Layout

```text
.dineway/content/runs/<run-id>/
├── native-state.json
├── status.json
├── publication-receipt.json
└── jobs/<job-id>/
    ├── result-receipt.json
    ├── research/{evidence.json,findings.md}
    ├── brief/brief.md
    ├── cms/draft-receipt.json
    ├── optimize/report.json
    ├── geo/report.json
    └── <optional-stage>/<artifact>
```

Use native Run and Job IDs as directory names. Never use title, keyword, slug, URL, or opportunity
name as identity. Do not commit site-specific artifacts unless that site repository permits it.

## Native snapshot version 5

Cache the exact `content_pipeline_status_get` response under `status`, then add current CMS and
read-only release data without rewriting the status fields:

```json
{
	"contractVersion": 5,
	"observedAt": "2026-08-14T00:08:00Z",
	"status": {
		"run": { "id": "run-id", "status": "active", "version": 5 },
		"currentStage": "quality_attestation",
		"nextAction": "derive_quality_attestation",
		"timing": {
			"startedAt": "2026-08-14T00:00:00Z",
			"generatedAt": "2026-08-14T00:08:00Z",
			"elapsedMs": 480000,
			"agentWorkMs": 300000,
			"orchestrationMs": 180000
		},
		"jobs": []
	},
	"content": {
		"collection": "posts",
		"id": "post-id",
		"draftRevisionId": "draft-revision-id",
		"liveRevisionId": "live-revision-id"
	},
	"releaseReadiness": {
		"ready": false,
		"nextAction": "fix_release_blockers",
		"blockers": []
	}
}
```

The scanner projects native `currentStage`, `nextAction`, and timing. It may override the displayed
next action only for authoritative recovery or a corrupt/missing local cache artifact.

## Stage Complete and Result receipts

Pass a typed stage payload to `content_pipeline_stage_complete`. For Research and Brief, the server
first renders the canonical artifacts from that validated payload. For other stages, pass canonical
artifact content with the typed payload. The server derives the artifact reference, SHA-256, UTF-8
byte count, provenance receipt, immutable typed Result, acceptance state, and next action in one
boundary. Callers must not precompute or duplicate these fields in `evidence.json`, a Result
envelope, or a separate wrapper.

Store the returned Result object unchanged as `jobs/<job-id>/result-receipt.json` when a local cache
is useful. It is replaceable from native status. Never edit it to make local state appear current.

Canonical stage artifacts are:

- Research: `research/evidence.json` and `research/findings.md`;
- Brief: `brief/brief.md`;
- Writer/Fix: `cms/draft-receipt.json`;
- Optimization: `optimize/report.json`;
- optional deep GEO: `geo/report.json`; and
- optional stages: their typed Result artifacts.

Research is a full SERP-first bundle for every Research type. It preserves required coverage,
normalized sources, availability, timestamps, persisted observations, facts, numeric keyword
metrics, search intent, SERP competitors, relevant/rejected questions, gaps, topic directions,
subtopics, clusters, and bounded lineage. Missing metrics remain `null`; unavailable sources are
explicit. The server deterministically projects `research/evidence.json` and
`research/findings.md`; callers never submit those wrappers.

Brief preserves the accepted Research Result and evidence in one Writer-ready structure:
primary/secondary keywords and intent, audience/voice/guardrails, internal links and media intent,
CMS binding, and an ordered outline with direct answer, at-a-glance, one section per subject,
methodology, optional approved-question FAQ, CTA, Observation-linked key points, and bounded word
budgets. The server deterministically projects `brief/brief.md`; callers never submit its wrapper.

The Draft receipt contains native identity, never a second article body. Optimization includes
exact Draft identity, suggestion decisions, score history, one native content-QA report, and
evidence IDs. Content QA never includes browser, screenshot, lazy-loading, responsive-layout, or
interaction/rendering checks.

## Identity and invalidation

Optimization, GEO, Atomization, and Fix Results are current only when collection, content ID, and
Draft Revision ID exactly match the CMS Draft. A later Draft invalidates old optimization,
Attestation, Review, and release readiness even if visible text looks unchanged. Schema, media,
policy, accepted-Result, or evidence changes can also invalidate Attestation/readiness.

## Publication receipt

On successful publish, save the server-returned `publicationReceipt` directly to
`publication-receipt.json`. It is derived from the consumed durable release grant. Never create a
second local receipt, calculate its action hash, or delay completion for receipt assembly.

## Safety

- Keep secrets, cookies, API keys, unredacted PII, and full private analytics exports out of this
  tree.
- Preserve bounded raw evidence outside public copy and reference it from immutable provenance.
- If local and native state disagree, preserve useful artifacts, refresh native state, and follow
  native status/readiness.

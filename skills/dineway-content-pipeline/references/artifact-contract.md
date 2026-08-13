# Pipeline Local Artifact Contract

`.dineway/content/` is derived, inspectable Agent working memory. The Pipeline plugin and Dineway
CMS are the authorities. Another machine must be able to reconstruct this tree from native state
and immutable Result provenance.

## Layout

```text
.dineway/content/
├── runs/
│   └── <pipeline-run-id>/
│       ├── native-state.json
│       ├── status.json
│       └── jobs/
│           └── <pipeline-job-id>/
│               ├── attempt-notes.md
│               ├── result-receipt.json
│               ├── research/{evidence.json,findings.md}
│               ├── brief/brief.md
│               ├── cms/draft-receipt.json
│               ├── optimize/report.json
│               ├── geo/report.json
│               ├── competition/report.json
│               ├── ai-visibility/report.json
│               ├── atomization/manifest.json
│               └── monitor/evidence.json
└── site-analysis/
    └── <analysis-key>/
        ├── evidence.json
        └── report.md
```

Use immutable native Run and Job IDs as directory names. Do not use title, keyword, slug, URL, or
opportunity name as identity.

## Native snapshot

Refresh `native-state.json` at session entry, before every state-changing command, after every
Result selection or CMS write, and at exit. It is a cache, never an authorization receipt.

```json
{
	"contractVersion": 4,
	"observedAt": "2026-08-13T00:00:00Z",
	"run": { "id": "run-id", "status": "active", "version": 4 },
	"jobs": [
		{
			"job": {
				"id": "job-id",
				"stage": "optimization",
				"status": "completed",
				"version": 6,
				"acceptedResultId": "result-id",
				"acceptedResultVersion": 2
			},
			"activeAssignment": null,
			"pendingHandoff": null,
			"candidateResult": null,
			"acceptedResult": {
				"id": "result-id",
				"jobId": "job-id",
				"kind": "optimization",
				"resultVersion": 2,
				"collection": "posts",
				"contentId": "post-id",
				"draftRevisionId": "draft-revision-id"
			}
		}
	],
	"content": {
		"collection": "posts",
		"id": "post-id",
		"revision": "opaque-revision-token",
		"draftRevisionId": "draft-revision-id",
		"liveRevisionId": "live-revision-id",
		"status": "draft"
	},
	"collectionSchema": {
		"slug": "posts",
		"schemaFingerprint": "64-character-sha256"
	},
	"calendar": { "assignmentStatus": "scheduled" },
	"qualityPolicy": { "id": "policy-id", "version": 2 },
	"qualityAttestation": null,
	"review": null,
	"release": null
}
```

`candidateResult` is the latest unselected Result when present. Valid Research submission is
auto-selected by the plugin; Brief and other reviewable stages remain candidates until accepted.
`acceptedResult` must be the exact
object returned by the plugin. Enrich the Run status response with pending Handoff and CMS reads;
do not infer them from prior sessions.

## Result receipt

Write the authoritative Result object unchanged to `jobs/<job-id>/result-receipt.json` after every
refresh. The scanner uses exact logical equality. Do not edit a receipt to make it look current.
When the accepted Result changes, preserve working artifacts but replace the derived receipt from
the native read.

## Result provenance

Every specialist Result uses the same strict provenance object: `skill`, nullable `skillVersion`,
`agentClient` (`codex`, `claude`, or `other`), nullable `model`, `collector` (`local`, `browser`,
`forgeway`, `dineway`, or `user`), `sourceTimestamps`, and `artifactReceipts`. Each source timestamp
records source kind, collection time, nullable validity deadline, and availability. Each artifact
receipt records the exact artifact ref, SHA-256, and positive byte count. Unknown provider fields
belong in bounded raw evidence, not in the normalized provenance object.

## Specialist artifacts

- Research `evidence.json` contains source records, availability, timestamps, bounded raw artifact
  references, claims, keywords, SERP competitors, gaps, topic directions, and clusters. It maps
  losslessly to the canonical Research Result where fields are normalized.
- Research `findings.md` explains intent, audience, differentiation, risky claims, internal-link
  candidates, and conclusions. It is not the authoritative Result.
- `brief.md` preserves the accepted Research Result ID/version, topic, keywords, content type,
  intent, target length, source-aligned outline fields, competitor URLs, questions, unique angle,
  audience context, guardrails, Dineway link/image plans, and exclusions.
- `draft-receipt.json` is the CMS response for the exact Draft write. Never store the article body
  in a Pipeline Result receipt.
- Optimize `report.json` contains SEO/GEO inputs, public score basis and coverage, breakdowns,
  suggestions with apply/dismiss decisions, score history, exact Draft revisions, evidence IDs,
  mandatory gates, and artifact references.
- Deep GEO `report.json` contains its independent score basis and coverage, four dimensions,
  per-platform observations, citation gaps, suggestions, and history.
- Competition, AI Visibility, Atomization, Site Analysis, and Monitor artifacts preserve the typed
  fields defined by their Result contracts plus bounded evidence references.

## Fingerprints and revision identity

Use SHA-256 of raw artifact bytes when a Result records a content/artifact fingerprint. Do not
canonicalize Markdown or JSON silently. An Optimize/GEO/Atomization/Fix Result is current only when
its top-level `collection`, `contentId`, and `draftRevisionId` match the current CMS Draft exactly.
A later Draft invalidates earlier revision-bound readiness even when the visible text appears
unchanged.

## Derived scanner

`scripts/scan_content_work.py` reads the native snapshot and cached artifacts and writes
`status.json`. It prioritizes Handoff recovery, expired Assignment recovery, retry, overdue calendar
reevaluation, Result receipt refresh, missing derived artifacts, and Draft drift before normal
stage routing. `status.json` never grants permission to mutate, accept, approve, schedule, or
publish.

## Safety

- Keep secrets, session cookies, API keys, unredacted PII, and full private analytics exports out
  of this tree.
- Preserve bounded raw evidence outside public copy and reference it from immutable provenance.
- Do not commit site-specific artifacts unless the site repository explicitly permits it.
- If local and native state disagree, preserve useful evidence, refresh native state, and follow
  the authoritative lifecycle.

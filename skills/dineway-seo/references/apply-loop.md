# Dineway SEO Apply Loop

Use this whenever recommendations become actual changes.

## Loop

1. `Findings`: summarize evidence, current state, and problem.
2. `Proposed Changes`: list exact Dineway writes or code edits.
3. `Apply`: use the narrowest write path.
4. `Verify`: inspect content/API/rendered output and run relevant checks.
5. `Report`: separate applied, skipped, and risky changes.

## Preferred Apply Paths

- Content CRUD for page/post/menu/news/review/gallery drafts.
- SEO metadata fields for title, description, canonical, OG, noindex, and robots.
- Media paths for image upload, alt text, captions, and public URLs.
- Site settings/HITL for global SEO defaults and brand context.
- Schema contributors/SEO Graph for JSON-LD.
- Astro code patch only for rendering gaps.

## Safety

- Preserve existing slugs unless redirect handling is planned.
- Do not publish risky or unsupported claims.
- Do not overwrite user edits without reading current revisions.
- Use source-backed schema only.
- Keep provider output and internal notes out of visitor-facing copy.
- Record skipped changes when data is missing.

## Verification

Check:

- content item fields and revisions;
- rendered title/meta/canonical/robots/OG;
- one H1 where applicable;
- JSON-LD parses and matches visible facts;
- links are crawlable;
- images resolve and have dimensions/alt text;
- no internal-rule/provenance phrases are visible;
- provider status/request identifiers and request limits were recorded when useful.

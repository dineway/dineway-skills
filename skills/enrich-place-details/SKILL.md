---
name: enrich-place-details
description: Fetch enriched restaurant place details from the hosted Dineway API. Use when the user provides a restaurant name and city, optionally with a Google placeId, and Codex needs to create a shadow user, search Dineway places, select the correct match, re-bind auth to the final place id, save the full place details JSON to the current workspace, and return the saved file path.
---

# Enrich Place Details

Use `scripts/enrich_place_details.js` to fetch restaurant details from the hosted Dineway API.

## Required Inputs

The user must provide both:

- restaurant name
- city or city/country

If either is missing, ask for the missing value and stop the skill. Do not run the script with incomplete inputs.

`placeId` is optional. If the user provides a valid place id, pass it with `--place-id` and treat it as authoritative. If no valid place id is provided, the script uses a temporary bootstrap place id only to create the first shadow user, searches by restaurant name and city, then creates a new shadow user bound to the selected place id before fetching details.

## Workflow

Run the script from the workspace where the place JSON should be saved. By default it creates `places/${placeId}.json` under the current directory and prints only a short summary.

```bash
node "$SKILL_ROOT/scripts/enrich_place_details.js" \
  --name "Peace Harmony" \
  --city "Sydney, Australia"
```

With a user-provided place id:

```bash
node "$SKILL_ROOT/scripts/enrich_place_details.js" \
  --name "Peace Harmony" \
  --city "Sydney, Australia" \
  --place-id "ChIJs5ydyTiuEmsR0fRSlU0C7k0"
```

Inspect candidates when matching is ambiguous:

```bash
node "$SKILL_ROOT/scripts/enrich_place_details.js" \
  --name "Peace Harmony" \
  --city "Sydney, Australia" \
  --include-candidates
```

## Result

Read `placeDetailsPath` from stdout and use that file for downstream site generation. The saved file contains the full payload by default: `query`, `authFlow`, `search`, `selectedPlace`, and `placeDetails`. The script never prints access or refresh tokens.

Stdout is intentionally compact:

```json
{
  "placeId": "ChIJs5ydyTiuEmsR0fRSlU0C7k0",
  "placeDetailsPath": "places/ChIJs5ydyTiuEmsR0fRSlU0C7k0.json",
  "savedPayload": "fullPayload",
  "selectedPlace": { "...": "selected place summary" },
  "search": { "...": "candidate count, selected candidate, match score, and match reason" }
}
```

Use `--output-dir DIR` only when a different destination is explicitly needed. Use `--details-only` only when the saved JSON should be the detail endpoint response instead of the full skill payload.

## Matching Rules

- Prefer the user-provided place id when supplied.
- Otherwise score search candidates by Unicode-normalized name, location, food-related type, business status, rating, and review count.
- Name matching reads `displayName.text`, `name`, `businessName`, and `title`.
- Location matching reads `formattedAddress`, `shortFormattedAddress`, `address`, `vicinity`, `plusCode`, and `addressComponents`; city/country input is split into parts so `Sydney, Australia` can still match an address that only includes Sydney.
- Rating and review count are tie-breakers, capped so they do not override strong name/location evidence.
- Use `id` or `placeId` from the selected search result as the final Dineway detail lookup id.
- If the final id differs from the initial bootstrap id, or the initial id was only a bootstrap fallback, create a new shadow user for the final id before fetching details.
- When matching is ambiguous, rerun with `--include-candidates` and inspect `matchScore` and `matchReason` in each candidate summary.

## Resources

- `scripts/enrich_place_details.js`: Node.js implementation of the shadow-user, search, rebind, refresh, and detail flow.
- `references/api.md`: Observed hosted API response fields and endpoint notes.

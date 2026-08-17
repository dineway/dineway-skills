#!/usr/bin/env python3
"""Fail-closed validation for generated dineway-building-clone agent files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


REQUIRED_HEADINGS = (
	"## Original Request",
	"## Clone Brief",
	"## Source URLs and One-Hop Discovery",
	"## Route and Artifact Plan",
	"## Source Data Layer Audit",
	"### Source Page Content Closure",
	"### Source Field Inventory",
	"### Source Record Inventory",
	"## Dineway CMS Content Model",
	"### Source Record Binding Plan",
	"## Data Naming Contract",
	"## Change Budget",
	"## Engineering Constraints and Verification",
	"## Required Skills",
	"### Brainstorming",
	"### Frontend Design — Source-Fidelity Mode",
	"### Dineway Site Construction",
	"### Planning and Progress Tracking",
	"## Commit and PR Discipline",
	"## Hard Failure Gates",
	"### Plan Gate",
	"### Discovery Gate",
	"### Evidence Gate",
	"### Data Model Gate",
	"### Foundation Gate",
	"### Specification Gate",
	"### Integration Gate",
	"### Visual QA Gate",
	"### Dineway QA Gate",
	"### Completion Gate",
	"## Execution Contract",
	"## Scope Defaults",
	"## URL Discovery, Output Isolation, and Route Preservation",
	"## Pre-Flight",
	"## Guiding Principles",
	"## Phase 1: Reconnaissance",
	"## Phase 2: Dineway Foundation Build",
	"## Phase 3: Component Specification and Dispatch",
	"## Phase 4: Page Assembly",
	"## Phase 5: Visual and Dineway QA",
	"## Pre-Dispatch Checklist",
	"## What Not to Do",
	"## Completion Report",
	"## Done Definition",
)

REQUIRED_PHRASES = (
	"$dineway-brainstorming",
	"$dineway-frontend-design",
	"$dineway-planning-with-files",
	"$dineway-building-site",
	"one same-origin link layer",
	"SOURCE_API_AUDIT.md",
	"SOURCE_API_AUDIT.json",
	"SOURCE_DOCUMENT_SNAPSHOT.json",
	"SOURCE_ENTITY_MODEL.md",
	"FIELD_MAPPING.md",
	"FIELD_MAPPING.json",
	"SETTINGS_MEDIA_PROOF.json",
	"RUNTIME_CONTENT_PROOF.json",
	"capture-source-screenshots.mjs",
	"stitch-browser-screenshots.py",
	"loadedImageElements === renderedImageElements",
	"failedImages",
	"documentHeightStable",
	"validate_data_model_artifacts.py",
	"--settings-media-proof",
	"--document-snapshot",
	"--runtime-content-proof",
	"--site-root",
	"--explicit-url",
	"--clone-url",
	"--phase foundation",
	"--phase completion",
	"document/hydration",
	"JSON-LD",
	"XHR/fetch",
	"REST",
	"GraphQL",
	"canonical camelCase",
	"runtime storageSlug",
	"runtimeReadPath",
	"mediaProof",
	"relationships/cardinality",
	"private PII",
	"anonymous public reads",
	"inline `<svg>`",
	"batched parallel downloads (4 at a time)",
	"`aria` labels",
	"element.textContent",
	"TreeWalker",
	"ATLASCLOUD_API_KEY",
	"https://api.atlascloud.ai/api/v1/models",
	"https://api.atlascloud.ai/api/v1/model/generateImage",
	"https://api.atlascloud.ai/api/v1/model/prediction/<id>",
	"source maps",
	"Do not automatically retry",
	"every 3 seconds for at most 40 attempts",
	"parallel (recommended when resources allow) or sequentially",
	"supports: [\"seo\"]",
	"Astro.cache.set(cacheHint)",
	"DinewayHead",
	"DinewayBodyStart",
	"DinewayBodyEnd",
	"$media",
	"dineway/ui",
	"src/pages/",
	"public/sites/",
	"pnpm typecheck",
	"pnpm build",
	"npx dineway seed seed/seed.json --validate",
	"robots.txt",
	"sitemap.xml",
	"schemamap.xml",
	"1440px",
	"768px",
	"390px",
	"deviceScaleFactor: 1",
	"SSIM >= 0.98",
	"changed-pixel ratio `<= 2%`",
	"critical geometry may differ by at most 2 CSS px",
	"planned component ownership rows == component spec files == dispatched ownership units",
	"extract → spec → dispatch → merge",
	"## Computed Styles (exact values from getComputedStyle)",
	"### Hover states",
	"## Per-State Content (if applicable)",
	"source text is verbatim",
)

FORBIDDEN_NEXT_ASSUMPTIONS = (
	"src/app/",
	"page.tsx",
	"next/font",
	"shadcn",
	"npm run build",
	"npx tsc --noEmit",
)

PLACEHOLDER_PATTERN = re.compile(r"\{\{[A-Z][A-Z0-9_]*\}\}")
HTTP_URL_PATTERN = re.compile(r"https?://[^\s)>`|]+")
CAMEL_CASE_PATTERN = re.compile(r"^[a-z][A-Za-z0-9]*$")
STORAGE_SLUG_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
SYSTEM_STORAGE_PATTERN = re.compile(r"^system:([a-z][a-z0-9_]*)$")
RESERVED_FIELD_SLUGS = {
	"id",
	"slug",
	"status",
	"author_id",
	"primary_byline_id",
	"created_at",
	"updated_at",
	"published_at",
	"scheduled_at",
	"deleted_at",
	"version",
	"live_revision_id",
	"draft_revision_id",
	"terms",
	"bylines",
	"byline",
}
DINEWAY_FIELD_TYPES = {
	"string",
	"text",
	"url",
	"number",
	"integer",
	"boolean",
	"datetime",
	"select",
	"multiSelect",
	"portableText",
	"image",
	"file",
	"reference",
	"json",
	"slug",
	"repeater",
}
DINEWAY_OWNER_KINDS = {"collection", "settings", "menu", "section", "taxonomy"}
SENSITIVE_DATA_PATTERN = re.compile(
	r'''(?im)["']?\b(authorization|proxy-authorization|cookie|set-cookie|x-api-key|password)["']?\s*:\s*(?!["']?(?:<?redacted>?|\[redacted\]))["']?\S+|["']?(api[_-]?key|access[_-]?token|refresh[_-]?token|token|session|client[_-]?secret|private[_-]?key|x-amz-credential|x-amz-signature|x-goog-credential|x-goog-signature)["']?\s*[=:]\s*(?!["']?(?:<?redacted>?|\[redacted\]))["']?\S+|[?&](?:x-amz-credential|x-amz-signature|x-amz-security-token|x-goog-credential|x-goog-signature|signature|sig|key-pair-id|auth|token|access_token|api[_-]?key)=[^&#\s"']+|https?://[^/\s:@]+:[^@\s/]+@|(?:^|\s)-u\s+\S+:\S+|\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----''',
)
PRIVATE_PII_PATTERN = re.compile(
	r"(?i)\b(?:personal|private|customer|user|member|guest|subscriber|account|billing)(?:[._/-][A-Za-z0-9_-]+)*[._-]?(?:email|phone|address|name)\b",
)
EVIDENCE_PATH_PATTERN = re.compile(r"(?:^|[/\\])[A-Za-z0-9_.@/-]+\.md(?:#[^\s|]+)?$")
OBSERVED_TYPES = {"string", "integer", "number", "boolean", "array", "object", "null"}
PUBLIC_DATA_CLASSES = {"public-content", "public-business-contact", "public-identifier", "public-media"}
READ_OPERATION_TYPES = {
	"get": {"read", "query"},
	"head": {"read", "query"},
	"embedded": {"embedded", "read"},
	"n/a": {"no-public-data"},
}
SURFACE_KINDS = {"html", "hydration", "json-ld", "xhr", "fetch", "rest", "graphql", "no-public-data"}


def valid_evidence_path(value: str) -> bool:
	return EVIDENCE_PATH_PATTERN.search(value.strip()) is not None


def decoded_for_security_scan(value: str) -> str:
	decoded = value
	for _ in range(10):
		next_value = unquote(decoded)
		if next_value == decoded:
			break
		decoded = next_value
	return decoded


def valid_public_url(value: str) -> bool:
	parsed = urlsplit(value)
	return (
		parsed.scheme in {"http", "https"}
		and bool(parsed.netloc)
		and parsed.username is None
		and SENSITIVE_DATA_PATTERN.search(decoded_for_security_scan(value)) is None
	)


def section(text: str, heading: str) -> str:
	start = text.find(heading)
	if start < 0:
		return ""
	match = re.search(r"\n##?\s+", text[start + len(heading) :])
	if match is None:
		return text[start:]
	return text[start : start + len(heading) + match.start()]


def markdown_table_rows(text: str, header_prefix: str) -> list[list[str]]:
	lines = text.splitlines()
	for index, line in enumerate(lines):
		if not line.strip().startswith(header_prefix):
			continue
		rows: list[list[str]] = []
		for row in lines[index + 2 :]:
			if not row.strip().startswith("|"):
				break
			cells: list[str] = []
			current: list[str] = []
			characters = row.strip().strip("|")
			position = 0
			while position < len(characters):
				character = characters[position]
				if character == "\\" and position + 1 < len(characters) and characters[position + 1] == "|":
					current.append("|")
					position += 2
					continue
				if character == "|":
					cells.append("".join(current).strip().strip("`"))
					current = []
				else:
					current.append(character)
				position += 1
			cells.append("".join(current).strip().strip("`"))
			if cells:
				rows.append(cells)
		return rows
	return []


def matches_template_shape(template_text: str, generated_text: str, agent_slug: str) -> bool:
	pattern_parts: list[str] = []
	cursor = 0
	for match in PLACEHOLDER_PATTERN.finditer(template_text):
		pattern_parts.append(re.escape(template_text[cursor : match.start()]))
		placeholder_name = match.group(0)[2:-2]
		if placeholder_name == "CLONE_SLUG":
			pattern_parts.append(re.escape(agent_slug))
		else:
			pattern_parts.append(r".+?")
		cursor = match.end()
	pattern_parts.append(re.escape(template_text[cursor:]))
	return re.fullmatch("".join(pattern_parts), generated_text, re.DOTALL) is not None


def validate(path: Path, *, template: bool) -> list[str]:
	errors: list[str] = []
	try:
		text = path.read_text(encoding="utf-8")
	except OSError as error:
		return [f"cannot read {path}: {error}"]

	if not text.startswith("---\n"):
		errors.append("missing opening YAML frontmatter delimiter")
	if text.count("---\n") < 2:
		errors.append("missing closing YAML frontmatter delimiter")

	name_match = re.search(r"^name:\s*([^\n]+)$", text, re.MULTILINE)
	if name_match is None:
		errors.append("missing frontmatter name")
	elif template:
		if name_match.group(1).strip() != "agent-{{CLONE_SLUG}}":
			errors.append("template name must be agent-{{CLONE_SLUG}}")
	elif re.fullmatch(r"agent-[a-z0-9]+(?:-[a-z0-9]+)*", name_match.group(1).strip()) is None:
		errors.append("frontmatter name must be agent-<kebab-case-slug>")

	heading_cursor = 0
	for heading in REQUIRED_HEADINGS:
		if heading not in text:
			errors.append(f"missing required heading: {heading}")
			continue
		heading_position = text.find(heading, heading_cursor)
		if heading_position < 0:
			errors.append(f"required heading is out of order: {heading}")
		else:
			heading_cursor = heading_position + len(heading)

	for phrase in REQUIRED_PHRASES:
		if phrase.casefold() not in text.casefold():
			errors.append(f"missing required contract phrase: {phrase}")

	for phrase in FORBIDDEN_NEXT_ASSUMPTIONS:
		if phrase in text:
			errors.append(f"forbidden Next.js assumption remains: {phrase}")

	if not template:
		placeholders = sorted(set(PLACEHOLDER_PATTERN.findall(text)))
		if placeholders:
			errors.append(f"unresolved template placeholders: {', '.join(placeholders)}")

		urls = HTTP_URL_PATTERN.findall(text)
		if not urls:
			errors.append("no explicit HTTP(S) source URL found")

		source_rows = markdown_table_rows(
			text,
			"| Source URL | Scope | Explicit parent | Preserved state |",
		)
		if not source_rows or not any(len(row) >= 2 and row[1].casefold() == "explicit" for row in source_rows):
			errors.append("source URL plan must contain at least one concrete explicit URL row")
		for row_number, row in enumerate(source_rows, start=1):
			if len(row) != 6 or not valid_public_url(row[0]):
				errors.append(f"source URL plan row {row_number} must contain all 6 concrete columns")
		if len([row[0] for row in source_rows if row]) != len({row[0] for row in source_rows if row}):
			errors.append("source URL plan contains duplicate URL rows")

		route_rows = markdown_table_rows(
			text,
			"| Source URL | Scope | Explicit parent | Destination route |",
		)
		if not route_rows:
			errors.append("route and artifact plan must contain a concrete per-URL Markdown table")
		for row_number, row in enumerate(route_rows, start=1):
			if len(row) != 13 or not valid_public_url(row[0]):
				errors.append(f"route and artifact row {row_number} must contain all 13 concrete columns")
		if len([row[0] for row in route_rows if row]) != len({row[0] for row in route_rows if row}):
			errors.append("route and artifact plan contains duplicate source URL rows")
		if source_rows and route_rows and len(source_rows) != len(route_rows):
			errors.append("source URL and route/artifact plans must contain the same number of rows")

		change_budget = section(text, "## Change Budget")
		if "approved" not in change_budget.lower() or "protected" not in change_budget.lower():
			errors.append("change budget must record both approved changes and protected invariants")

		data_audit = section(text, "## Source Data Layer Audit")
		data_audit_markers = ("http", "json-ld", "hydration", "xhr", "fetch", "no-public-data")
		if not any(marker in data_audit.lower() for marker in data_audit_markers):
			errors.append(
				"source data layer audit must identify public endpoint/payload evidence or a concrete no-public-data finding",
			)
		if "skipped" in data_audit.casefold() or "visual-only" in data_audit.casefold():
			errors.append("source data layer audit may not be skipped or reduced to visual-only cloning")
		if SENSITIVE_DATA_PATTERN.search(decoded_for_security_scan(text)):
			errors.append("agent contains an unredacted credential, cookie, token, signed URL, or private key")
		if PRIVATE_PII_PATTERN.search(decoded_for_security_scan(text)):
			errors.append("agent contains private personal/account data")

		data_rows = markdown_table_rows(
			text,
			"| Page URL | Surface | Location/endpoint | Transport method |",
		)
		if not data_rows:
			errors.append("source data layer audit must contain at least one concrete evidence row")
		for row_number, row in enumerate(data_rows, start=1):
			if len(row) != 12 or not valid_public_url(row[0]):
				errors.append(f"source data layer row {row_number} must contain all 12 concrete columns")
				continue
			if not valid_public_url(row[2]):
				errors.append(f"source data layer row {row_number} location must be a public HTTP(S) URL")
			transport_method = row[3].casefold()
			operation_type = row[4].casefold()
			kind = row[1].casefold()
			if kind not in SURFACE_KINDS:
				errors.append(f"source data layer row {row_number} uses an unsupported surface kind")
			allowed_operation_types = READ_OPERATION_TYPES.get(transport_method, set())
			is_graphql_query = (
				transport_method == "post"
				and operation_type == "query"
				and kind == "graphql"
				and re.fullmatch(
					r"operationName=(?:[_A-Za-z][_0-9A-Za-z]*|anonymous); documentSha256=[0-9a-f]{64}",
					row[6],
				)
				is not None
			)
			if operation_type not in allowed_operation_types and not is_graphql_query:
				errors.append(
					f"source data layer row {row_number} is not an anonymous read or GraphQL query: {row[3]} {row[4]}",
				)
			if row[5].casefold() != "anonymous-public":
				errors.append(f"source data layer row {row_number} access must be anonymous-public")
			if not valid_evidence_path(row[11]):
				errors.append(f"source data layer row {row_number} evidence must be a concrete Markdown path")
		data_row_keys = [tuple(row[:10]) for row in data_rows if len(row) == 12]
		if len(data_row_keys) != len(set(data_row_keys)):
			errors.append("source data layer audit contains duplicate surface rows")
		planned_urls = {row[0] for row in route_rows if row}
		covered_urls = {row[0] for row in data_rows if row}
		missing_data_urls = sorted(planned_urls - covered_urls)
		if missing_data_urls:
			errors.append(
				"source data layer audit lacks a data or no-public-data row for: " + ", ".join(missing_data_urls),
			)

		document_rows = markdown_table_rows(text, "| Page URL | HTML document surface |")
		if not document_rows:
			errors.append("source data layer audit must contain a per-page visible document closure")
		document_urls: list[str] = []
		for row_number, row in enumerate(document_rows, start=1):
			if len(row) != 7 or any(not cell for cell in row):
				errors.append(f"page content closure row {row_number} must contain all 7 concrete columns")
				continue
			document_urls.append(row[0])
			if row[0] not in planned_urls or row[1] != row[0]:
				errors.append(f"page content closure row {row_number} must bind its planned HTML URL")
			if not valid_evidence_path(row[6]):
				errors.append(f"page content closure row {row_number} evidence must be a concrete Markdown path")
		missing_document_urls = sorted(planned_urls - set(document_urls))
		if missing_document_urls:
			errors.append("page content closure lacks planned pages: " + ", ".join(missing_document_urls))

		source_field_rows = markdown_table_rows(text, "| Source field ref | Source entity |")
		if not source_field_rows:
			errors.append("source data layer audit must contain a concrete source field inventory")
		inventory_refs: list[str] = []
		for row_number, row in enumerate(source_field_rows, start=1):
			if len(row) != 14 or any(not cell for cell in row):
				errors.append(f"source field inventory row {row_number} must contain all 14 concrete columns")
				continue
			inventory_refs.append(row[0])
			if row[4].casefold() not in {"true", "false"}:
				errors.append(f"source field inventory row {row_number} nullable must be true or false")
			if row[5].casefold() not in PUBLIC_DATA_CLASSES:
				errors.append(f"source field inventory row {row_number} must use an allowed public data class")
			observed_types = {
				item.strip().casefold()
				for item in re.split(r"[,/]", row[3])
				if item.strip()
			}
			if not observed_types or not observed_types.issubset(OBSERVED_TYPES):
				errors.append(f"source field inventory row {row_number} uses unsupported observed types")
			if not valid_evidence_path(row[13]):
				errors.append(f"source field inventory row {row_number} evidence must be a concrete Markdown path")
		if len(inventory_refs) != len(set(inventory_refs)):
			errors.append("source field inventory contains duplicate field refs")

		record_rows = markdown_table_rows(text, "| Source entity | Source record ID |")
		if not record_rows:
			errors.append("source data layer audit must contain a concrete source record inventory")
		record_keys: list[tuple[str, str]] = []
		for row_number, row in enumerate(record_rows, start=1):
			if len(row) != 5 or any(not cell for cell in row):
				errors.append(f"source record inventory row {row_number} must contain all 5 concrete columns")
				continue
			record_keys.append((row[0], row[1]))
			try:
				values = json.loads(row[2], parse_constant=lambda constant: (_ for _ in ()).throw(ValueError(constant)))
			except (json.JSONDecodeError, ValueError):
				errors.append(f"source record inventory row {row_number} field tuple must be strict compact JSON")
			else:
				if not isinstance(values, dict) or not values:
					errors.append(f"source record inventory row {row_number} field tuple must be a non-empty object")
			if not valid_evidence_path(row[4]):
				errors.append(f"source record inventory row {row_number} evidence must be a concrete Markdown path")
		if len(record_keys) != len(set(record_keys)):
			errors.append("source record inventory contains duplicate entity/record IDs")

		entity_rows = markdown_table_rows(text, "| Source entity | Source location/API |")
		if not entity_rows:
			errors.append("Dineway CMS content model must contain at least one concrete entity mapping row")
		entity_owner_keys: list[tuple[str, str, str]] = []
		surface_locations = {row[2] for row in data_rows if len(row) == 12}
		for row_number, row in enumerate(entity_rows, start=1):
			if len(row) != 6 or any(not cell for cell in row):
				errors.append(f"entity mapping row {row_number} must contain all 6 concrete columns")
				continue
			location_urls = HTTP_URL_PATTERN.findall(row[1])
			if len(location_urls) != 1 or location_urls[0] not in surface_locations:
				errors.append(f"entity mapping row {row_number} source location must match a public data surface")
			if row[2].casefold() not in DINEWAY_OWNER_KINDS:
				errors.append(f"entity mapping row {row_number} has unsupported owner kind")
			if not valid_evidence_path(row[5]):
				errors.append(f"entity mapping row {row_number} evidence must be a concrete Markdown path")
			entity_owner_keys.append((row[0], row[2].casefold(), row[3]))
		if len(entity_owner_keys) != len(set(entity_owner_keys)):
			errors.append("Dineway entity mapping contains duplicate source owner rows")
		entity_ids = {row[0] for row in entity_rows if len(row) == 6}
		for row_number, row in enumerate(data_rows, start=1):
			if len(row) != 12:
				continue
			response_entity = row[9]
			if response_entity.casefold() == "none":
				if row[1].casefold() != "no-public-data" or row[4].casefold() != "no-public-data":
					errors.append(f"source data layer row {row_number} may use response entity none only for no-public-data")
			elif response_entity not in entity_ids:
				errors.append(f"source data layer row {row_number} response entity has no entity mapping")

		field_rows = markdown_table_rows(text, "| Source field ref/path |")
		if not field_rows:
			errors.append("Dineway CMS content model must contain at least one concrete field mapping row")
		seen_targets: set[tuple[str, str, str]] = set()
		seen_names: set[tuple[str, str, str]] = set()
		seen_storage: set[tuple[str, str, str]] = set()
		mapping_refs: list[str] = []
		for row_number, row in enumerate(field_rows, start=1):
			if len(row) != 14 or any(not cell for cell in row):
				errors.append(f"field mapping row {row_number} must contain all 14 concrete columns")
				continue
			mapping_refs.append(row[0])
			owner_kind = row[1].casefold()
			owner_key = row[2]
			target_path = row[3]
			canonical_name = row[4]
			storage_slug = row[5]
			field_type = row[6]
			if owner_kind not in DINEWAY_OWNER_KINDS:
				errors.append(f"field mapping row {row_number} has unsupported owner kind: {owner_kind}")
			if CAMEL_CASE_PATTERN.fullmatch(canonical_name) is None:
				errors.append(
					f"field mapping row {row_number} canonical Dineway field must be lower camelCase: {canonical_name}",
				)
			system_match = SYSTEM_STORAGE_PATTERN.fullmatch(storage_slug)
			if system_match is not None and system_match.group(1) not in RESERVED_FIELD_SLUGS:
				errors.append(
					f"field mapping row {row_number} declares an unknown system storageSlug: {storage_slug}",
				)
			elif storage_slug in RESERVED_FIELD_SLUGS:
				errors.append(
					f"field mapping row {row_number} uses reserved storageSlug {storage_slug}; mark it as system:{storage_slug} or map a custom field",
				)
			elif (
				storage_slug.casefold() not in {"n/a", "none"}
				and system_match is None
				and STORAGE_SLUG_PATTERN.fullmatch(storage_slug) is None
			):
				errors.append(
					f"field mapping row {row_number} runtime storageSlug must be lower_snake_case or N/A: {storage_slug}",
				)
			elif system_match is None and len(storage_slug) > 63:
				errors.append(
					f"field mapping row {row_number} runtime storageSlug exceeds 63 characters: {storage_slug}",
				)
			if field_type not in DINEWAY_FIELD_TYPES:
				errors.append(f"field mapping row {row_number} uses unsupported Dineway type: {field_type}")
			if not valid_evidence_path(row[13]):
				errors.append(f"field mapping row {row_number} evidence must be a concrete Markdown path")
			target_key = (owner_kind, owner_key.casefold(), target_path.casefold())
			if target_key in seen_targets:
				errors.append(
					f"field mapping row {row_number} duplicates Dineway target: {owner_kind}.{owner_key}.{target_path}",
				)
			seen_targets.add(target_key)
			name_key = (owner_kind, owner_key.casefold(), canonical_name.casefold())
			if name_key in seen_names:
				errors.append(
					f"field mapping row {row_number} duplicates Dineway owner/name: {owner_key}.{canonical_name}",
				)
			seen_names.add(name_key)
			if storage_slug.casefold() not in {"n/a", "none"}:
				storage_key = (owner_kind, owner_key.casefold(), storage_slug.casefold())
				if storage_key in seen_storage:
					errors.append(f"field mapping row {row_number} duplicates owner/storageSlug: {owner_key}.{storage_slug}")
				seen_storage.add(storage_key)
		if set(inventory_refs) != set(mapping_refs):
			missing_refs = sorted(set(inventory_refs) - set(mapping_refs))
			extra_refs = sorted(set(mapping_refs) - set(inventory_refs))
			details: list[str] = []
			if missing_refs:
				details.append("unmapped: " + ", ".join(missing_refs))
			if extra_refs:
				details.append("without source evidence: " + ", ".join(extra_refs))
			errors.append("source field inventory and Dineway mappings differ (" + "; ".join(details) + ")")
		if len(mapping_refs) != len(set(mapping_refs)):
			errors.append("Dineway field mapping contains duplicate source refs")
		inventory_entities = {row[0]: row[1] for row in source_field_rows if len(row) == 14}
		expected_entity_owner_keys = {
			(inventory_entities[row[0]], row[1].casefold(), row[2])
			for row in field_rows
			if len(row) == 14 and row[0] in inventory_entities
		}
		if set(entity_owner_keys) != expected_entity_owner_keys:
			errors.append("Dineway entity mappings do not match source field owners")

		binding_rows = markdown_table_rows(text, "| Source entity | Source record ID | Owner kind |")
		if not binding_rows:
			errors.append("Dineway CMS content model must contain a concrete source record binding plan")
		binding_keys: list[tuple[str, str, str, str]] = []
		for row_number, row in enumerate(binding_rows, start=1):
			if len(row) != 6 or any(not cell for cell in row):
				errors.append(f"source record binding row {row_number} must contain all 6 concrete columns")
				continue
			if row[2].casefold() not in DINEWAY_OWNER_KINDS:
				errors.append(f"source record binding row {row_number} has unsupported owner kind")
			if not row[4].startswith("/"):
				errors.append(f"source record binding row {row_number} must contain an RFC 6901 JSON Pointer")
			if not valid_evidence_path(row[5]):
				errors.append(f"source record binding row {row_number} evidence must be a concrete Markdown path")
			binding_keys.append((row[0], row[1], row[2].casefold(), row[3]))
		if len(binding_keys) != len(set(binding_keys)):
			errors.append("source record binding plan contains duplicate source owner bindings")

		template_path = Path(__file__).resolve().parent.parent / "references" / "clone-agent-template.md"
		try:
			template_text = template_path.read_text(encoding="utf-8")
		except OSError as error:
			errors.append(f"cannot read normative clone agent template: {error}")
		else:
			execution_heading = "## Execution Contract"
			template_contract = template_text[template_text.index(execution_heading) :]
			generated_contract = text[text.index(execution_heading) :] if execution_heading in text else ""
			agent_slug = name_match.group(1).strip().removeprefix("agent-") if name_match else ""
			if not matches_template_shape(template_text, text, agent_slug):
				errors.append(
					"agent differs from the normative template outside resolved placeholders",
				)
			expected_contract = template_contract.replace("{{CLONE_SLUG}}", agent_slug)
			if generated_contract != expected_contract:
				errors.append(
					"execution contract differs from the normative template; restore every original step and item",
				)

	return errors


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("agent_file", type=Path)
	parser.add_argument(
		"--template",
		action="store_true",
		help="validate the bundled template while allowing unresolved placeholders",
	)
	args = parser.parse_args()

	errors = validate(args.agent_file, template=args.template)
	if errors:
		print(f"INVALID: {args.agent_file}", file=sys.stderr)
		for error in errors:
			print(f"- {error}", file=sys.stderr)
		return 1

	mode = "template" if args.template else "agent"
	print(f"VALID {mode}: {args.agent_file}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

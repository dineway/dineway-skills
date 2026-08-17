#!/usr/bin/env python3
"""Regression tests for clone data-model artifact closure."""

from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
	"validate_data_model_artifacts",
	SCRIPT_DIR / "validate_data_model_artifacts.py",
)
if SPEC is None or SPEC.loader is None:
	raise RuntimeError("Unable to load validate_data_model_artifacts.py")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def valid_artifacts() -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
	evidence_root = "docs/research/example/SOURCE_API_AUDIT.md"
	audit: dict[str, object] = {
		"version": "1",
		"pages": [
			{
				"url": "https://example.com/",
				"document": {
					"surfaceLocation": "https://example.com/",
					"visibleEntities": [
						{
							"responseEntity": "Organization",
							"visibleFieldRefs": ["Organization.logo.url"],
							"visibleRecordIds": ["organization:example"],
							"selectors": ["header img"],
						},
					],
					"evidence": [f"{evidence_root}#organization"],
				},
				"surfaces": [
					{
						"kind": "html",
						"location": "https://example.com/",
						"transportMethod": "embedded",
						"operationType": "embedded",
						"access": "anonymous-public",
						"parameters": "initial load",
						"pagination": "none",
						"filtering": "none",
						"ordering": "none",
						"responseEntity": "Organization",
						"uiConsumers": ["Header"],
						"evidence": [f"{evidence_root}#organization"],
					},
					{
						"kind": "json-ld",
						"location": "https://example.com/#organization",
						"transportMethod": "embedded",
						"operationType": "embedded",
						"access": "anonymous-public",
						"parameters": "initial load",
						"pagination": "none",
						"filtering": "none",
						"ordering": "none",
						"responseEntity": "Organization",
						"uiConsumers": ["Header"],
						"evidence": [f"{evidence_root}#organization"],
					},
				],
			},
		],
		"entities": [
			{
				"id": "Organization",
				"sourceLocation": "https://example.com/#organization",
				"records": [
					{
						"recordId": "organization:example",
						"values": {"Organization.logo.url": "https://example.com/logo.png"},
						"uiConsumers": ["Header"],
						"evidence": [f"{evidence_root}#organization-logo"],
					},
				],
				"fields": [
					{
						"ref": "Organization.logo.url",
						"path": "logo.url",
						"observedTypes": ["string"],
						"dataClass": "public-media",
						"nullable": True,
						"observedValues": ["https://example.com/logo.png"],
						"identifierRole": "none",
						"enumDateSemantics": "URL",
						"relationshipCardinality": "none",
						"localeStatus": "public/default",
						"mediaShape": "image URL",
						"uiConsumers": ["Header"],
						"evidence": [f"{evidence_root}#organization-logo"],
					},
				],
			},
		],
	}
	mapping: dict[str, object] = {
		"version": "1",
		"entityMappings": [
			{
				"sourceEntity": "Organization",
				"sourceLocation": "https://example.com/#organization",
				"ownerKind": "collection",
				"ownerKey": "organizations",
				"renderConsumers": ["src/pages/index.astro"],
				"evidence": [f"{evidence_root}#organization"],
			},
		],
		"recordBindings": [
			{
				"sourceEntity": "Organization",
				"sourceRecordId": "organization:example",
				"ownerKind": "collection",
				"ownerKey": "organizations",
				"targetPointer": "/content/organizations/0",
				"evidence": [f"{evidence_root}#organization-logo"],
			},
		],
		"fields": [
			{
				"sourceRef": "Organization.logo.url",
				"sourceEntity": "Organization",
				"sourcePath": "logo.url",
				"sourceDataClass": "public-media",
				"ownerKind": "collection",
				"ownerKey": "organizations",
				"targetPath": "featured_image",
				"canonicalName": "featuredImage",
				"storageSlug": "featured_image",
				"runtimeReadPath": "data.featured_image",
				"type": "image",
				"required": False,
				"nullable": True,
				"validation": {},
				"options": {},
				"relationship": {"cardinality": "none", "targetOwner": None},
				"localeBehavior": "public/default",
				"statusBehavior": "published",
				"mediaOwnership": "cms",
				"seedConsumers": ["seed/seed.json#content.organizations"],
				"renderConsumers": ["src/pages/index.astro"],
				"evidence": [f"{evidence_root}#organization-logo"],
			},
		],
	}
	seed: dict[str, object] = {
		"version": "1",
		"collections": [
			{
				"slug": "organizations",
				"label": "Organizations",
				"fields": [
					{
						"slug": "featured_image",
						"label": "featuredImage",
						"type": "image",
					},
				],
			},
		],
		"content": {
			"organizations": [
				{
					"id": "organization:example",
					"slug": "example",
					"status": "published",
					"data": {"featured_image": {"$media": {"url": "https://example.com/logo.png"}}},
				},
			],
		},
	}
	return audit, mapping, seed


def markdown_row(values: tuple[object, ...]) -> str:
	cells = [str(value).replace("|", "\\|") for value in values]
	return "| " + " | ".join(cells) + " |"


class ValidateDataModelArtifactsTests(unittest.TestCase):
	def validate_values(
		self,
		audit: dict[str, object],
		mapping: dict[str, object],
		seed: dict[str, object],
		settings_media_proof: dict[str, object] | None = None,
		document_snapshot: dict[str, object] | None = None,
		runtime_content_proof: dict[str, object] | None = None,
		agent_replacements: tuple[tuple[str, str], ...] = (),
		synchronize_entity_mappings: bool = True,
		trusted_explicit_urls: list[str] | None = None,
		render_source: str | None = None,
		create_route_files: bool = True,
		clone_url: str = "http://127.0.0.1:4321/",
	) -> list[str]:
		with tempfile.TemporaryDirectory() as directory:
			seed_fragments = {
				"settings": "settings",
				"menu": "menus",
				"section": "sections",
				"taxonomy": "taxonomies",
			}
			for field in mapping.get("fields", []):
				owner_kind = field.get("ownerKind")
				owner_key = field.get("ownerKey")
				fragment = (
					f"content.{owner_key}"
					if owner_kind == "collection"
					else seed_fragments.get(str(owner_kind), str(owner_kind))
				)
				field["seedConsumers"] = [f"seed/seed.json#{fragment}"]
			if synchronize_entity_mappings:
				entity_locations = {
					entity.get("id"): entity.get("sourceLocation")
					for entity in audit.get("entities", [])
					if isinstance(entity, dict)
				}
				mapping_evidence = mapping.get("entityMappings", [{}])[0].get("evidence", [])
				mapping["entityMappings"] = [
					{
						"sourceEntity": field.get("sourceEntity"),
						"sourceLocation": entity_locations.get(field.get("sourceEntity")),
						"ownerKind": field.get("ownerKind"),
						"ownerKey": field.get("ownerKey"),
						"renderConsumers": field.get("renderConsumers", []),
						"evidence": mapping_evidence,
					}
					for field in mapping.get("fields", [])[:1]
				]
			root = Path(directory)
			research_root = root / "docs" / "research" / "example"
			research_root.mkdir(parents=True)
			(root / "seed").mkdir()
			(root / "clone-agents").mkdir()
			(root / "src" / "pages").mkdir(parents=True)
			render_lines: list[str] = []
			for field in mapping.get("fields", []):
				owner_kind = field.get("ownerKind")
				owner_key = field.get("ownerKey")
				target = str(field.get("runtimeReadPath") or field.get("storageSlug") or field.get("targetPath")).rsplit(".", 1)[-1]
				if owner_kind == "collection":
					render_lines.append(
						f'const {{ entries, cacheHint }} = await getDinewayCollection("{owner_key}"); Astro.cache.set(cacheHint); const value = entries[0]?.data?.{target};',
					)
				elif owner_kind == "settings":
					render_lines.append(f"const settings = await getSiteSettings(); const value = settings.{target};")
				elif owner_kind == "menu":
					render_lines.append(f'const menu = await getMenu("{owner_key}"); const value = menu?.items[0]?.{target};')
				elif owner_kind == "section":
					render_lines.append(f'const section = await getSection("{owner_key}"); const value = section?.{target};')
				elif owner_kind == "taxonomy":
					render_lines.append(
						f'const terms = await getTaxonomyTerms("{owner_key}"); const value = terms[0]?.{str(target).removeprefix("terms.")};',
					)
			page_source = (
				render_source
				or '---\nimport { getDinewayCollection, getMenu, getSection, getSiteSettings, getTaxonomyTerms } from "dineway";\n'
				+ "\n".join(render_lines)
				+ "\n---\n<div>{value}</div>\n"
			)
			(root / "src" / "pages" / "index.astro").write_text(page_source, encoding="utf-8")
			for collection in seed.get("collections", []) if create_route_files else []:
				url_pattern = collection.get("urlPattern") if isinstance(collection, dict) else None
				if isinstance(url_pattern, str) and "{slug}" in url_pattern:
					route_file = root / "src" / "pages" / f'{url_pattern.lstrip("/").replace("{slug}", "[slug]")}.astro'
					route_file.parent.mkdir(parents=True, exist_ok=True)
					route_file.write_text(page_source, encoding="utf-8")
			paths = [
				research_root / "SOURCE_API_AUDIT.json",
				research_root / "SOURCE_DOCUMENT_SNAPSHOT.json",
				research_root / "FIELD_MAPPING.json",
				root / "seed" / "seed.json",
				research_root / "SETTINGS_MEDIA_PROOF.json",
				research_root / "RUNTIME_CONTENT_PROOF.json",
			]
			(research_root / "SOURCE_API_AUDIT.md").write_text(
				'# Organization\n\nhttps://example.com/#organization\n\n## Organization logo\n\norganization:example\nOrganization.logo.url\nhttps://example.com/logo.png\n01ARZ3NDEKTSV4RRFFQ69G5FAV\n{"Organization.logo.url":"https://example.com/logo.png"}\n/content/organizations/0\n/settings\n\n## 组织标志\n\n'
				+ json.dumps(audit, ensure_ascii=False, separators=(",", ":"))
				+ "\n"
				+ json.dumps(mapping, ensure_ascii=False, separators=(",", ":"))
				+ "\n"
				+ "\n".join(
					json.dumps(record.get("values"), sort_keys=True, ensure_ascii=False, separators=(",", ":"))
					for entity in audit.get("entities", [])
					for record in entity.get("records", [])
				),
				encoding="utf-8",
			)
			proof = settings_media_proof or {"version": "1", "proofs": []}
			if document_snapshot is None:
				snapshot_pages: list[dict[str, object]] = []
				for page in audit.get("pages", []):
					items: list[dict[str, object]] = []
					for visible_entity in page.get("document", {}).get("visibleEntities", []):
						entity = next(
							candidate
							for candidate in audit.get("entities", [])
							if candidate.get("id") == visible_entity.get("responseEntity")
						)
						for source_ref in visible_entity.get("visibleFieldRefs", []):
							record = next(
								(
									candidate
									for candidate in entity.get("records", [])
									if candidate.get("recordId") in visible_entity.get("visibleRecordIds", [])
									and source_ref in candidate.get("values", {})
								),
								None,
							)
							field = next(
								(candidate for candidate in entity.get("fields", []) if candidate.get("ref") == source_ref),
								{},
							)
							for selector_index, selector in enumerate(visible_entity.get("selectors", [])):
								items.append(
									{
										"itemId": f"{source_ref}:{selector_index}",
										"kind": "media" if field.get("dataClass") == "public-media" else "visible-text",
										"selector": selector,
										"sourceEntity": visible_entity.get("responseEntity"),
										"sourceRef": source_ref,
										"sourceRecordId": record.get("recordId") if isinstance(record, dict) else str(visible_entity.get("visibleRecordIds", [""])[0]),
										"value": record.get("values", {}).get(source_ref) if isinstance(record, dict) else None,
									}
								)
					snapshot_pages.append(
						{
							"url": page.get("url"),
							"capturedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
							"items": items,
						},
					)
				document_snapshot = {"version": "1", "pages": snapshot_pages}
			if runtime_content_proof is None:
				proofs: list[dict[str, object]] = []
				mappings_by_ref = {field.get("sourceRef"): field for field in mapping.get("fields", [])}
				audit_fields_by_ref = {
					field.get("ref"): field
					for entity in audit.get("entities", [])
					for field in entity.get("fields", [])
				}
				for page in document_snapshot.get("pages", []):
					for item in page.get("items", []):
						source_ref = item.get("sourceRef")
						field = mappings_by_ref.get(source_ref, {})
						source_value = item.get("value")
						before_value = source_value
						sentinel_value = f"{before_value}__dineway_probe__"
						media_proof: dict[str, object] | None = None
						if audit_fields_by_ref.get(source_ref, {}).get("dataClass") == "public-media":
							source_bytes = b"source-logo"
							sentinel_bytes = b"sentinel-logo"
							source_hash = "sha1:" + hashlib.sha1(source_bytes).hexdigest()
							sentinel_hash = "sha1:" + hashlib.sha1(sentinel_bytes).hexdigest()
							before_value = clone_url.rstrip("/") + "/_dineway/media/source.png"
							sentinel_value = clone_url.rstrip("/") + "/_dineway/media/sentinel.png"
							media_proof = {
								"sourceSnapshot": "docs/research/example/runtime-source-logo.bin",
								"sourceContentHash": source_hash,
								"before": {
									"mediaId": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
									"resolvedUrl": before_value,
									"contentHash": source_hash,
									"mimeType": "image/png",
								},
								"sentinel": {
									"mediaId": "01ARZ3NDEKTSV4RRFFQ69G5FAW",
									"resolvedUrl": sentinel_value,
									"contentHash": sentinel_hash,
									"mimeType": "image/png",
								},
								"restore": {
									"mediaId": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
									"resolvedUrl": before_value,
									"contentHash": source_hash,
									"mimeType": "image/png",
								},
							}
						for render_consumer in field.get("renderConsumers", []):
							proofs.append(
								{
									"pageUrl": page.get("url"),
									"snapshotItemId": item.get("itemId"),
									"sourceEntity": item.get("sourceEntity"),
									"sourceRecordId": item.get("sourceRecordId"),
									"sourceRef": source_ref,
									"sourceValue": source_value,
									"ownerKind": field.get("ownerKind"),
									"ownerKey": field.get("ownerKey"),
									"runtimeReadPath": field.get("runtimeReadPath"),
									"renderConsumer": render_consumer,
									"selector": item.get("selector"),
									"cloneUrl": clone_url,
									"capturedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
									"mediaProof": media_proof,
									"before": {"liveReadStatus": 200, "ssrStatus": 200, "observedValue": before_value},
									"sentinel": {
										"value": sentinel_value,
										"writeStatus": 200,
										"liveReadStatus": 200,
										"ssrStatus": 200,
										"observedValue": sentinel_value,
									},
									"restore": {
										"writeStatus": 200,
										"liveReadStatus": 200,
										"ssrStatus": 200,
										"observedValue": before_value,
									},
								},
							)
				runtime_content_proof = {"version": "1", "proofs": proofs}
			for proof_row in proof.get("proofs", []):
				if isinstance(proof_row, dict) and isinstance(proof_row.get("sourceSnapshot"), str):
					snapshot_path = root / proof_row["sourceSnapshot"]
					snapshot_path.parent.mkdir(parents=True, exist_ok=True)
					snapshot_path.write_bytes(b"source-logo")
			for proof_row in runtime_content_proof.get("proofs", []):
				media_proof = proof_row.get("mediaProof") if isinstance(proof_row, dict) else None
				if isinstance(media_proof, dict) and isinstance(media_proof.get("sourceSnapshot"), str):
					snapshot_path = root / media_proof["sourceSnapshot"]
					snapshot_path.parent.mkdir(parents=True, exist_ok=True)
					snapshot_path.write_bytes(b"source-logo")
			for path, value in zip(
				paths,
				(audit, document_snapshot, mapping, seed, proof, runtime_content_proof),
				strict=True,
			):
				path.write_text(json.dumps(value), encoding="utf-8")
			agent_path = root / "clone-agents" / "agent.md"
			source_rows = "\n".join(
				f"| {page['url']} | explicit | N/A | none | / | include |"
				for page in audit.get("pages", [])
			)
			data_rows = "\n".join(
				markdown_row(
					(
						page["url"],
						surface["kind"],
						surface["location"],
						surface["transportMethod"],
						surface["operationType"],
						surface["access"],
						surface["parameters"],
						surface["pagination"],
						f"filter={surface['filtering']}; sort={surface['ordering']}",
						surface["responseEntity"],
						", ".join(surface["uiConsumers"]),
						", ".join(surface["evidence"]),
					),
				)
				for page in audit.get("pages", [])
				for surface in page.get("surfaces", [])
			)
			document_rows = "\n".join(
				markdown_row(
					(
						page["url"],
						page["document"]["surfaceLocation"],
						visible_entity["responseEntity"],
						", ".join(visible_entity["visibleFieldRefs"]),
						", ".join(visible_entity["visibleRecordIds"]),
						", ".join(visible_entity["selectors"]),
						", ".join(page["document"]["evidence"]),
					),
				)
				for page in audit.get("pages", [])
				if isinstance(page.get("document"), dict)
				for visible_entity in page["document"].get("visibleEntities", [])
			)
			inventory_rows = "\n".join(
				markdown_row(
					(
						str(field["ref"]),
						str(entity["id"]),
						str(field["path"]),
						"/".join(field.get("observedTypes", [])),
						str(field["nullable"]).lower(),
						str(field.get("dataClass")),
						json.dumps(field.get("observedValues"), separators=(",", ":")),
						str(field.get("identifierRole")),
						str(field.get("enumDateSemantics")),
						str(field.get("relationshipCardinality")),
						str(field.get("localeStatus")),
						str(field.get("mediaShape")),
						", ".join(field.get("uiConsumers", [])),
						", ".join(field.get("evidence", [])),
					),
				)
				for entity in audit.get("entities", [])
				for field in entity.get("fields", [])
			)
			mapping_rows = "\n".join(
				markdown_row(
					(
						str(field["sourceRef"]),
						str(field["ownerKind"]),
						str(field["ownerKey"]),
						str(field["targetPath"]),
						str(field["canonicalName"]),
						"N/A" if field.get("storageSlug") is None else str(field["storageSlug"]),
						str(field["type"]),
						f"required={str(field.get('required')).lower()}; nullable={str(field.get('nullable')).lower()}",
						f"validation={json.dumps(field.get('validation'), sort_keys=True, separators=(',', ':'))}; options={json.dumps(field.get('options'), sort_keys=True, separators=(',', ':'))}",
						json.dumps(field.get("relationship"), sort_keys=True, separators=(",", ":")),
						f"locale={field.get('localeBehavior')}; status={field.get('statusBehavior')}",
						str(field.get("mediaOwnership"))
						+ (f"; source={field.get('mediaSourceUrl')}" if field.get("mediaSourceUrl") is not None else "")
						+ (
							f"; metadata={json.dumps(field.get('mediaMetadata'), sort_keys=True, separators=(',', ':'))}"
							if field.get("mediaMetadata") is not None
							else ""
						),
						f"seed={', '.join(field.get('seedConsumers', []))}; render={', '.join(field.get('renderConsumers', []))}",
						", ".join(field.get("evidence", [])),
					),
				)
				for field in mapping.get("fields", [])
			)
			entity_mapping_rows = "\n".join(
				markdown_row(
					(
						str(entity_mapping["sourceEntity"]),
						str(entity_mapping["sourceLocation"]),
						str(entity_mapping["ownerKind"]),
						str(entity_mapping["ownerKey"]),
						", ".join(entity_mapping.get("renderConsumers", [])),
						", ".join(entity_mapping.get("evidence", [])),
					),
				)
				for entity_mapping in mapping.get("entityMappings", [])
			)
			record_rows = "\n".join(
				markdown_row(
					(
						str(entity["id"]),
						str(record["recordId"]),
						json.dumps(record.get("values"), sort_keys=True, separators=(",", ":")),
						", ".join(record.get("uiConsumers", [])),
						", ".join(record.get("evidence", [])),
					),
				)
				for entity in audit.get("entities", [])
				for record in entity.get("records", [])
			)
			binding_rows = "\n".join(
				markdown_row(
					(
						str(binding["sourceEntity"]),
						str(binding["sourceRecordId"]),
						str(binding["ownerKind"]),
						str(binding["ownerKey"]),
						str(binding["targetPointer"]),
						", ".join(binding.get("evidence", [])),
					),
				)
				for binding in mapping.get("recordBindings", [])
			)
			agent_text = f"""| Source URL | Scope | Explicit parent | Preserved state | Destination route | Decision |
| --- | --- | --- | --- | --- | --- |
{source_rows}

| Page URL | Surface | Location/endpoint | Transport method | Operation type | Access | Parameters/state | Pagination | Filter/sort | Response entity | UI consumer | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
{data_rows}

| Page URL | HTML document surface | Visible entity | Visible field refs | Visible record IDs | Stable selectors | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
{document_rows}

| Source field ref | Source entity | Source path | Observed type | Nullable | Data class | Observed in-scope values | Identifier role | Enum/date semantics | Relationship/cardinality | Locale/status | Media shape | UI consumer | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
{inventory_rows}

| Source entity | Source record ID | Ordered field tuple (compact JSON by sourceRef) | UI consumer | Evidence |
| --- | --- | --- | --- | --- |
{record_rows}

| Source entity | Source location/API | Dineway owner | Collection/section/setting/menu | Route consumer | Evidence |
| --- | --- | --- | --- | --- | --- |
{entity_mapping_rows}

| Source field ref/path | Owner kind | Owner key | Target path | Canonical Dineway CMS field name/label | Runtime storageSlug | Dineway type | Required/nullability | Validation/options | Relationship/cardinality | Locale/status | Media ownership/source | Seed/render consumer | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
{mapping_rows}

| Source entity | Source record ID | Owner kind | Owner key | Seed JSON Pointer | Evidence |
| --- | --- | --- | --- | --- | --- |
{binding_rows}
"""
			for old, new in agent_replacements:
				agent_text = agent_text.replace(old, new)
			agent_path.write_text(agent_text, encoding="utf-8")
			return VALIDATOR.validate_artifacts(
				*paths,
				agent_path,
				root,
				trusted_explicit_urls or ["https://example.com/"],
				clone_url,
			)

	def test_accepts_closed_source_mapping_and_seed(self) -> None:
		audit, mapping, seed = valid_artifacts()
		self.assertEqual(self.validate_values(audit, mapping, seed), [])

	def test_accepts_escaped_gfm_pipe_in_source_values(self) -> None:
		audit, mapping, seed = valid_artifacts()
		value = "Lunch | Dinner"
		audit_field = audit["entities"][0]["fields"][0]
		audit_field.update(
			{
				"dataClass": "public-content",
				"observedValues": [value],
				"enumDateSemantics": "none",
				"mediaShape": "none",
			}
		)
		audit["entities"][0]["records"][0]["values"]["Organization.logo.url"] = value
		field = mapping["fields"][0]
		field.update({"type": "string", "mediaOwnership": "none", "sourceDataClass": "public-content"})
		seed["collections"][0]["fields"][0]["type"] = "string"
		seed["content"]["organizations"][0]["data"]["featured_image"] = value
		self.assertEqual(self.validate_values(audit, mapping, seed), [])

	def test_accepts_compact_multivalue_array_evidence(self) -> None:
		audit, mapping, seed = valid_artifacts()
		value = ["id-a", "id-b"]
		audit_field = audit["entities"][0]["fields"][0]
		audit_field.update(
			{
				"dataClass": "public-content",
				"observedTypes": ["array"],
				"observedValues": [value],
				"enumDateSemantics": "none",
				"mediaShape": "none",
			}
		)
		audit["entities"][0]["records"][0]["values"]["Organization.logo.url"] = value
		field = mapping["fields"][0]
		field.update({"type": "json", "mediaOwnership": "none", "sourceDataClass": "public-content"})
		seed["collections"][0]["fields"][0]["type"] = "json"
		seed["content"]["organizations"][0]["data"]["featured_image"] = value
		self.assertEqual(self.validate_values(audit, mapping, seed), [])

	def test_rejects_unmapped_source_field(self) -> None:
		audit, mapping, seed = valid_artifacts()
		mapping["fields"] = []
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("unmapped public source fields" in error for error in errors))

	def test_rejects_seed_field_that_does_not_match_mapping(self) -> None:
		audit, mapping, seed = valid_artifacts()
		broken_seed = copy.deepcopy(seed)
		broken_seed["collections"][0]["fields"][0]["label"] = "Featured image"
		errors = self.validate_values(audit, mapping, broken_seed)
		self.assertTrue(any("seed label must equal canonicalName" in error for error in errors))

	def test_rejects_seed_fields_and_records_without_source_bindings(self) -> None:
		audit, mapping, seed = valid_artifacts()
		seed["collections"][0]["fields"].append(
			{"slug": "invented_copy", "label": "inventedCopy", "type": "string"},
		)
		seed["content"]["organizations"][0]["data"]["invented_copy"] = "not observed"
		seed["content"]["organizations"].append(
			{
				"id": "organization:invented",
				"slug": "invented",
				"status": "published",
				"data": {"featured_image": {"$media": {"url": "https://example.com/invented.png"}}},
			},
		)
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("seed custom fields without source mappings" in error for error in errors))
		self.assertTrue(any("seed content entries without source record bindings" in error for error in errors))

	def test_rejects_reverse_closure_bypass_with_only_system_mapping(self) -> None:
		audit, mapping, seed = valid_artifacts()
		audit_field = audit["entities"][0]["fields"][0]
		audit_field.update(
			{
				"dataClass": "public-content",
				"observedValues": ["published"],
				"mediaShape": "none",
			}
		)
		audit["entities"][0]["records"][0]["values"]["Organization.logo.url"] = "published"
		field = mapping["fields"][0]
		field.update(
			{
				"targetPath": "status",
				"canonicalName": "status",
				"storageSlug": "system:status",
				"type": "select",
				"validation": {"options": ["published", "draft"]},
				"mediaOwnership": "none",
				"sourceDataClass": "public-content",
			}
		)
		seed["collections"][0]["fields"] = [
			{"slug": "invented_copy", "label": "inventedCopy", "type": "string"},
		]
		seed["content"]["organizations"][0]["data"] = {"invented_copy": "not observed"}
		seed["content"]["organizations"].append(
			{
				"id": "organization:invented",
				"slug": "invented",
				"status": "draft",
				"data": {"invented_copy": "also not observed"},
			},
		)
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("seed custom fields without source mappings" in error for error in errors))
		self.assertTrue(any("seed content entries without source record bindings" in error for error in errors))

	def test_rejects_unredacted_secrets(self) -> None:
		audit, mapping, seed = valid_artifacts()
		audit["pages"][0]["surfaces"][0]["Authorization"] = "Bearer secret-token-value"
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("unredacted credential" in error for error in errors))

	def test_accepts_anonymous_graphql_query_over_post(self) -> None:
		audit, mapping, seed = valid_artifacts()
		surface = audit["pages"][0]["surfaces"][1]
		document = "query OrganizationQuery { organization { logo { url } } }"
		document_hash = hashlib.sha256(document.encode()).hexdigest()
		surface.update(
			{
				"kind": "graphql",
				"location": "https://example.com/graphql",
				"transportMethod": "POST",
				"operationType": "query",
				"operationName": "OrganizationQuery",
				"requestDocument": document,
				"requestDocumentHash": document_hash,
				"parameters": f"operationName=OrganizationQuery; documentSha256={document_hash}",
			}
		)
		audit["entities"][0]["sourceLocation"] = "https://example.com/graphql"
		self.assertEqual(self.validate_values(audit, mapping, seed), [])

	def test_rejects_graphql_mutation_and_authenticated_access(self) -> None:
		audit, mapping, seed = valid_artifacts()
		surface = audit["pages"][0]["surfaces"][0]
		surface["kind"] = "graphql"
		surface["transportMethod"] = "POST"
		surface["operationType"] = "mutation"
		surface["access"] = "authenticated"
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("not a read operation" in error for error in errors))
		self.assertTrue(any("access must be anonymous-public" in error for error in errors))

	def test_rejects_self_approved_field_exclusion(self) -> None:
		audit, mapping, seed = valid_artifacts()
		field = mapping["fields"][0]
		field["approvedExclusion"] = "not needed"
		field["approvedExclusionEvidence"] = ["self-approved"]
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("self-approved exclusion" in error for error in errors))

	def test_rejects_invalid_media_seed_shape(self) -> None:
		audit, mapping, seed = valid_artifacts()
		seed["content"]["organizations"][0]["data"]["featured_image"] = {
			"$media": "https://example.com/logo.png",
		}
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("incompatible with Dineway type image" in error for error in errors))

	def test_rejects_cms_media_downgraded_to_plain_string(self) -> None:
		audit, mapping, seed = valid_artifacts()
		field = mapping["fields"][0]
		field.update({"type": "string", "mediaOwnership": "none"})
		seed["collections"][0]["fields"][0]["type"] = "string"
		seed["content"]["organizations"][0]["data"]["featured_image"] = "https://example.com/logo.png"
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("public media must use a Dineway image/file" in error for error in errors))

	def test_rejects_validly_typed_but_wrong_source_value(self) -> None:
		audit, mapping, seed = valid_artifacts()
		seed["content"]["organizations"][0]["data"]["featured_image"] = {
			"$media": {"url": "https://example.com/wrong.png"},
		}
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("public source values absent from seed" in error for error in errors))

	def test_rejects_agent_and_execution_artifact_drift(self) -> None:
		audit, mapping, seed = valid_artifacts()
		errors = self.validate_values(
			audit,
			mapping,
			seed,
			agent_replacements=(("https://example.com/logo.png", "https://example.com/planned.png"),),
		)
		self.assertTrue(any("source field inventory" in error for error in errors))
		self.assertTrue(any("source record inventory" in error for error in errors))

	def test_rejects_agent_entity_mapping_drift(self) -> None:
		audit, mapping, seed = valid_artifacts()
		errors = self.validate_values(
			audit,
			mapping,
			seed,
			agent_replacements=(
				(
					"| Organization | https://example.com/#organization | collection | organizations | src/pages/index.astro |",
					"| Organization | https://example.com/#organization | settings | wrongOwner | src/pages/wrong.astro |",
				),
			),
		)
		self.assertTrue(any("entity mapping table" in error for error in errors))

	def test_rejects_unknown_operation_type_on_get(self) -> None:
		audit, mapping, seed = valid_artifacts()
		surface = audit["pages"][0]["surfaces"][0]
		surface["transportMethod"] = "GET"
		surface["operationType"] = "delete"
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("not a read operation" in error for error in errors))

	def test_rejects_unsafe_surface_location(self) -> None:
		audit, mapping, seed = valid_artifacts()
		audit["pages"][0]["surfaces"][0]["location"] = "javascript:deleteAll()"
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("unsafe/non-public location" in error for error in errors))

	def test_rejects_unsafe_or_unbound_entity_source_location(self) -> None:
		for location in (
			"file:///private/customer.db",
			"javascript:readPrivate()",
			"https://example.com/unobserved-api",
		):
			with self.subTest(location=location):
				audit, mapping, seed = valid_artifacts()
				audit["entities"][0]["sourceLocation"] = location
				errors = self.validate_values(audit, mapping, seed)
				self.assertTrue(any("sourceLocation" in error for error in errors))

	def test_rejects_missing_surface_entity_and_evidence(self) -> None:
		audit, mapping, seed = valid_artifacts()
		audit["pages"][0]["surfaces"][0]["responseEntity"] = "MissingEntity"
		audit["pages"][0]["surfaces"][0]["evidence"] = ["does-not-exist.md"]
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("responseEntity is absent" in error for error in errors))
		self.assertTrue(any("evidence file does not exist" in error for error in errors))

	def test_rejects_missing_evidence_anchor(self) -> None:
		audit, mapping, seed = valid_artifacts()
		audit["entities"][0]["fields"][0]["evidence"] = [
			"docs/research/example/SOURCE_API_AUDIT.md#invented-anchor",
		]
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("evidence anchor does not exist" in error for error in errors))

	def test_accepts_repository_relative_evidence_and_unicode_gfm_anchor(self) -> None:
		audit, mapping, seed = valid_artifacts()
		audit["entities"][0]["fields"][0]["evidence"] = [
			"docs/research/example/SOURCE_API_AUDIT.md#组织标志",
		]
		self.assertEqual(self.validate_values(audit, mapping, seed), [])

	def test_rejects_private_or_mismatched_data_class(self) -> None:
		audit, mapping, seed = valid_artifacts()
		audit["entities"][0]["fields"][0]["dataClass"] = "private-account"
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("allowed public classification" in error for error in errors))
		self.assertTrue(any("sourceDataClass does not match" in error for error in errors))

	def test_rejects_contact_data_misclassified_as_generic_public_content(self) -> None:
		audit, mapping, seed = valid_artifacts()
		field = audit["entities"][0]["fields"][0]
		field.update(
			{
				"ref": "Organization.email",
				"path": "email",
				"dataClass": "public-content",
				"observedValues": ["alice.private@example.net"],
				"enumDateSemantics": "none",
				"mediaShape": "none",
				"uiConsumers": ["Footer contact"],
			}
		)
		audit["entities"][0]["records"][0]["values"] = {
			"Organization.email": "alice.private@example.net",
		}
		mapping_field = mapping["fields"][0]
		mapping_field.update(
			{
				"sourceRef": "Organization.email",
				"sourcePath": "email",
				"sourceDataClass": "public-content",
				"targetPath": "email",
				"canonicalName": "email",
				"storageSlug": "email",
				"type": "string",
				"mediaOwnership": "none",
			}
		)
		seed["collections"][0]["fields"][0].update(
			{"slug": "email", "label": "email", "type": "string"},
		)
		seed["content"]["organizations"][0]["data"] = {"email": "alice.private@example.net"}
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("contact data must use public-business-contact" in error for error in errors))

	def test_rejects_record_count_or_cross_field_mismatch(self) -> None:
		audit, mapping, seed = valid_artifacts()
		entity = audit["entities"][0]
		entity["records"].append(copy.deepcopy(entity["records"][0]))
		entity["records"][1]["recordId"] = "organization:duplicate"
		entity["fields"][0]["observedValues"].append("https://example.com/logo.png")
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("without Dineway target bindings" in error for error in errors))

	def test_rejects_incompatible_observed_type(self) -> None:
		audit, mapping, seed = valid_artifacts()
		field = audit["entities"][0]["fields"][0]
		field["observedTypes"] = ["integer"]
		field["observedValues"] = [7]
		audit["entities"][0]["records"][0]["values"]["Organization.logo.url"] = 7
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("incompatible with observed types" in error for error in errors))

	def test_rejects_reserved_or_oversized_collection_slug(self) -> None:
		for slug in ("content", "a" * 64):
			with self.subTest(slug=slug):
				audit, mapping, seed = valid_artifacts()
				seed["collections"][0]["slug"] = slug
				errors = self.validate_values(audit, mapping, seed)
				self.assertTrue(any("seed collection" in error and "slug" in error for error in errors))

	def test_rejects_signed_urls_and_private_account_pii(self) -> None:
		for value in (
			"https://example.com/logo.png?X-Amz-Signature=secret",
			"https://example.com/logo.png?sig=secret",
			"https://example.com/logo.png?Signature=secret&Key-Pair-Id=key",
			"https://example.com/logo.png?auth=secret",
			"https://example.com/logo.png?X%2dAmz%2dSignature=secret",
			"https://example.com/logo.png?signature%3dsecret",
			"https://example.com/logo.png?signature%2525253dsecret",
			"Account.personalEmail",
			"customerEmail",
		):
			with self.subTest(value=value):
				audit, mapping, seed = valid_artifacts()
				audit["entities"][0]["fields"][0]["path"] = value
				errors = self.validate_values(audit, mapping, seed)
				self.assertTrue(any("signed URL" in error or "personal/account" in error for error in errors))

	def test_rejects_invalid_media_url(self) -> None:
		audit, mapping, seed = valid_artifacts()
		seed["content"]["organizations"][0]["data"]["featured_image"] = {
			"$media": {"url": "not-a-public-url"},
		}
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("incompatible with Dineway type image" in error for error in errors))

	def test_rejects_invalid_url_field_value(self) -> None:
		audit, mapping, seed = valid_artifacts()
		audit_field = audit["entities"][0]["fields"][0]
		audit_field.update(
			{
				"dataClass": "public-content",
				"observedValues": ["not-a-url"],
				"mediaShape": "none",
			}
		)
		audit["entities"][0]["records"][0]["values"]["Organization.logo.url"] = "not-a-url"
		field = mapping["fields"][0]
		field.update({"type": "url", "mediaOwnership": "none", "sourceDataClass": "public-content"})
		seed["collections"][0]["fields"][0]["type"] = "url"
		seed["content"]["organizations"][0]["data"]["featured_image"] = "not-a-url"
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("incompatible with Dineway type url" in error for error in errors))

	def test_rejects_select_value_outside_validation_options(self) -> None:
		audit, mapping, seed = valid_artifacts()
		audit_field = audit["entities"][0]["fields"][0]
		audit_field.update(
			{
				"dataClass": "public-content",
				"observedValues": ["green"],
				"mediaShape": "none",
			}
		)
		audit["entities"][0]["records"][0]["values"]["Organization.logo.url"] = "green"
		field = mapping["fields"][0]
		field.update(
			{
				"type": "select",
				"mediaOwnership": "none",
				"sourceDataClass": "public-content",
				"validation": {"options": ["red", "blue"]},
			}
		)
		seed_field = seed["collections"][0]["fields"][0]
		seed_field.update({"type": "select", "validation": {"options": ["red", "blue"]}})
		seed["content"]["organizations"][0]["data"]["featured_image"] = "green"
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("incompatible with Dineway type select" in error for error in errors))

	def test_rejects_unresolved_reference_and_false_many_cardinality(self) -> None:
		audit, mapping, seed = valid_artifacts()
		field = mapping["fields"][0]
		field.update(
			{
				"canonicalName": "relatedOrganizations",
				"storageSlug": "related_organizations",
				"targetPath": "related_organizations",
				"type": "reference",
				"mediaOwnership": "none",
				"options": {"collection": "organizations"},
				"relationship": {"cardinality": "many", "targetOwner": "organizations"},
			}
		)
		seed_field = seed["collections"][0]["fields"][0]
		seed_field.update(
			{
				"slug": "related_organizations",
				"label": "relatedOrganizations",
				"type": "reference",
				"options": {"collection": "organizations"},
			}
		)
		seed["content"]["organizations"][0]["data"] = {"related_organizations": "$ref:missing"}
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("incompatible with Dineway type reference" in error for error in errors))
		self.assertTrue(any("unsupported many-valued" in error for error in errors))
		self.assertTrue(any("unresolved reference" in error for error in errors))

	def test_rejects_settings_media_using_collection_media_shape(self) -> None:
		audit, mapping, seed = valid_artifacts()
		field = mapping["fields"][0]
		field.update(
			{
				"ownerKind": "settings",
				"ownerKey": "settings",
				"targetPath": "logo",
				"canonicalName": "logo",
				"storageSlug": None,
				"runtimeReadPath": "logo",
				"mediaSourceUrl": "https://example.com/logo.png",
			}
		)
		mapping["recordBindings"][0].update(
			{
				"ownerKind": "settings",
				"ownerKey": "settings",
				"targetPointer": "/settings",
			}
		)
		seed["settings"] = {"logo": {"$media": {"url": "https://example.com/logo.png"}}}
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("well-formed mediaId/alt" in error for error in errors))

	def test_rejects_non_ulid_settings_media_id(self) -> None:
		audit, mapping, seed = valid_artifacts()
		field = mapping["fields"][0]
		field.update(
			{
				"ownerKind": "settings",
				"ownerKey": "settings",
				"targetPath": "logo",
				"canonicalName": "logo",
				"storageSlug": None,
				"mediaSourceUrl": "https://example.com/logo.png",
			}
		)
		mapping["recordBindings"][0].update(
			{
				"ownerKind": "settings",
				"ownerKey": "settings",
				"targetPointer": "/settings",
			}
		)
		seed["settings"] = {"logo": {"mediaId": "does-not-exist", "alt": "Example"}}
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("well-formed mediaId/alt" in error for error in errors))

	def test_requires_closed_runtime_proof_for_settings_media(self) -> None:
		audit, mapping, seed = valid_artifacts()
		field = mapping["fields"][0]
		field.update(
			{
				"ownerKind": "settings",
				"ownerKey": "settings",
				"targetPath": "logo",
				"canonicalName": "logo",
				"storageSlug": None,
				"runtimeReadPath": "logo",
				"mediaSourceUrl": "https://example.com/logo.png",
			}
		)
		mapping["recordBindings"][0].update(
			{"ownerKind": "settings", "ownerKey": "settings", "targetPointer": "/settings"},
		)
		media_id = "01ARZ3NDEKTSV4RRFFQ69G5FAV"
		seed["settings"] = {"logo": {"mediaId": media_id, "alt": ""}}
		source_bytes = b"source-logo"
		source_hash = "sha1:" + hashlib.sha1(source_bytes).hexdigest()
		captured_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
		proof = {
			"version": "1",
			"proofs": [
				{
					"sourceRef": "Organization.logo.url",
					"targetPath": "logo",
					"sourceUrl": "https://example.com/logo.png",
					"sourceSnapshot": "docs/research/example/source-logo.bin",
					"mediaId": media_id,
					"capturedAt": captured_at,
					"sourceFetch": {
						"requestedUrl": "https://example.com/logo.png",
						"finalUrl": "https://example.com/logo.png",
						"status": 200,
						"mimeType": "image/png",
						"byteLength": len(source_bytes),
						"contentHash": source_hash,
						"capturedAt": captured_at,
					},
					"mediaGet": {
						"status": 200,
						"item": {
							"id": media_id,
							"status": "ready",
							"mimeType": "image/png",
							"storageKey": "media/example.png",
							"url": "/_dineway/api/media/file/media/example.png",
							"contentHash": source_hash,
						},
					},
					"settingsGet": {
						"status": 200,
						"mediaId": media_id,
						"resolvedUrl": "/_dineway/api/media/file/media/example.png",
						"alt": "",
					},
				},
			],
		}
		self.assertEqual(self.validate_values(audit, mapping, seed, proof), [])
		proof["proofs"][0]["settingsGet"]["mediaId"] = "01ARZ3NDEKTSV4RRFFQ69G5FAW"
		errors = self.validate_values(audit, mapping, seed, proof)
		self.assertTrue(any("settings media proof" in error for error in errors))
		proof["proofs"][0]["settingsGet"]["mediaId"] = media_id
		proof["proofs"][0]["mediaGet"]["item"]["contentHash"] = "sha1:" + "a" * 40
		errors = self.validate_values(audit, mapping, seed, proof)
		self.assertTrue(any("source snapshot content" in error for error in errors))
		proof["proofs"][0]["mediaGet"]["item"]["contentHash"] = source_hash
		seed["settings"]["logo"]["alt"] = "Invented alt"
		errors = self.validate_values(audit, mapping, seed, proof)
		self.assertTrue(any("alt" in error for error in errors))

	def test_rejects_runtime_invalid_field_values_and_constraints(self) -> None:
		cases = (
			("portableText", [{}], {}, "portableText"),
			("datetime", "2026-08-17 12:00:00", {}, "datetime"),
			("string", "a", {"pattern": "(?P<name>a)"}, "validation"),
		)
		for field_type, value, validation, marker in cases:
			with self.subTest(field_type=field_type):
				audit, mapping, seed = valid_artifacts()
				audit_field = audit["entities"][0]["fields"][0]
				audit_field.update(
					{
						"dataClass": "public-content",
						"observedTypes": [VALIDATOR.json_value_type(value)],
						"observedValues": [value],
						"mediaShape": "none",
					},
				)
				audit["entities"][0]["records"][0]["values"]["Organization.logo.url"] = value
				field = mapping["fields"][0]
				field.update(
					{
						"type": field_type,
						"mediaOwnership": "none",
						"sourceDataClass": "public-content",
						"validation": validation,
					},
				)
				seed_field = seed["collections"][0]["fields"][0]
				seed_field.update({"type": field_type, "validation": validation})
				seed["content"]["organizations"][0]["data"]["featured_image"] = value
				errors = self.validate_values(audit, mapping, seed)
				self.assertTrue(any(marker in error for error in errors))

	def test_rejects_validation_shapes_that_break_runtime_manifest(self) -> None:
		for field_type, validation in (
			("string", {"options": [1]}),
			("repeater", {"subFields": [{"slug": "bad-field", "type": "string", "label": "Bad"}]}),
			("image", {"allowedMimeTypes": ["not-a-mime"]}),
		):
			with self.subTest(field_type=field_type):
				audit, mapping, seed = valid_artifacts()
				field = mapping["fields"][0]
				field.update({"type": field_type, "validation": validation})
				seed["collections"][0]["fields"][0].update(
					{"type": field_type, "validation": validation},
				)
				errors = self.validate_values(audit, mapping, seed)
				self.assertTrue(any("invalid Dineway validation definition" in error for error in errors))

	def test_rejects_runtime_invalid_fixed_settings_values(self) -> None:
		for target_path, field_type, value in (
			("postsPerPage", "integer", 0),
			("seo.titleSeparator", "string", "12345678901"),
		):
			with self.subTest(target_path=target_path):
				audit, mapping, seed = valid_artifacts()
				audit_field = audit["entities"][0]["fields"][0]
				audit_field.update(
					{
						"dataClass": "public-content",
						"observedTypes": [VALIDATOR.json_value_type(value)],
						"observedValues": [value],
						"mediaShape": "none",
					},
				)
				audit["entities"][0]["records"][0]["values"]["Organization.logo.url"] = value
				field = mapping["fields"][0]
				field.update(
					{
						"ownerKind": "settings",
						"ownerKey": "settings",
						"targetPath": target_path,
						"canonicalName": target_path.split(".")[-1],
						"storageSlug": None,
						"type": field_type,
						"mediaOwnership": "none",
						"sourceDataClass": "public-content",
					},
				)
				mapping["recordBindings"][0].update(
					{"ownerKind": "settings", "ownerKey": "settings", "targetPointer": "/settings"},
				)
				seed["collections"] = []
				seed["content"] = {}
				if "." in target_path:
					parent, child = target_path.split(".", 1)
					seed["settings"] = {parent: {child: value}}
				else:
					seed["settings"] = {target_path: value}
				errors = self.validate_values(audit, mapping, seed)
				self.assertTrue(any("settings value" in error for error in errors))

	def test_accepts_runtime_menu_css_classes_string(self) -> None:
		audit, mapping, seed = valid_artifacts()
		audit_field = audit["entities"][0]["fields"][0]
		audit_field.update(
			{
				"dataClass": "public-content",
				"observedValues": ["nav-primary"],
				"mediaShape": "none",
			}
		)
		audit["entities"][0]["records"][0]["values"]["Organization.logo.url"] = "nav-primary"
		field = mapping["fields"][0]
		field.update(
			{
				"ownerKind": "menu",
				"ownerKey": "primary",
				"targetPath": "cssClasses",
				"canonicalName": "cssClasses",
				"storageSlug": None,
				"type": "string",
				"mediaOwnership": "none",
				"sourceDataClass": "public-content",
			}
		)
		mapping["recordBindings"][0].update(
			{
				"ownerKind": "menu",
				"ownerKey": "primary",
				"targetPointer": "/menus/0/items/0",
			},
		)
		seed["collections"] = []
		seed["content"] = {}
		seed["menus"] = [
			{
				"name": "primary",
				"items": [{"label": "Home", "url": "/", "cssClasses": "nav-primary"}],
			},
		]
		errors = self.validate_values(audit, mapping, seed)
		self.assertFalse(any("menu path cssClasses cannot use type string" in error for error in errors))
		self.assertFalse(any("menu values are incompatible with type string" in error for error in errors))

	def test_rejects_unbound_seed_records_inside_mapped_fixed_owner(self) -> None:
		audit, mapping, seed = valid_artifacts()
		audit_field = audit["entities"][0]["fields"][0]
		audit_field.update(
			{
				"dataClass": "public-content",
				"observedValues": ["Home"],
				"mediaShape": "none",
			}
		)
		audit["entities"][0]["records"][0]["values"]["Organization.logo.url"] = "Home"
		field = mapping["fields"][0]
		field.update(
			{
				"ownerKind": "menu",
				"ownerKey": "primary",
				"targetPath": "label",
				"canonicalName": "label",
				"storageSlug": None,
				"type": "string",
				"mediaOwnership": "none",
				"sourceDataClass": "public-content",
			}
		)
		mapping["recordBindings"][0].update(
			{
				"ownerKind": "menu",
				"ownerKey": "primary",
				"targetPointer": "/menus/0/items/0",
			},
		)
		seed["menus"] = [
			{
				"name": "primary",
				"items": [
					{"label": "Home", "url": "/"},
					{"label": "Invented", "url": "/invented"},
				],
			},
		]
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("seed menu items without source record bindings" in error for error in errors))

	def test_rejects_unmapped_fields_inside_mapped_settings_and_section_owners(self) -> None:
		for owner_kind, owner_key, target_path, value, target_pointer in (
			("settings", "settings", "title", "Site", "/settings"),
			("section", "hero", "title", "Heading", "/sections/0"),
		):
			with self.subTest(owner_kind=owner_kind):
				audit, mapping, seed = valid_artifacts()
				audit_field = audit["entities"][0]["fields"][0]
				audit_field.update(
					{
						"dataClass": "public-content",
						"observedValues": [value],
						"mediaShape": "none",
					},
				)
				audit["entities"][0]["records"][0]["values"]["Organization.logo.url"] = value
				field = mapping["fields"][0]
				field.update(
					{
						"ownerKind": owner_kind,
						"ownerKey": owner_key,
						"targetPath": target_path,
						"canonicalName": target_path,
						"storageSlug": None,
						"type": "string",
						"mediaOwnership": "none",
						"sourceDataClass": "public-content",
					},
				)
				mapping["recordBindings"][0].update(
					{"ownerKind": owner_kind, "ownerKey": owner_key, "targetPointer": target_pointer},
				)
				if owner_kind == "settings":
					seed["settings"] = {"title": value, "tagline": "Invented"}
				else:
					seed["sections"] = [
						{
							"slug": owner_key,
							"title": value,
							"description": "Invented",
							"content": [{"_type": "block"}],
						},
					]
				errors = self.validate_values(audit, mapping, seed)
				self.assertTrue(any("fields without source mappings" in error for error in errors))

	def test_rejects_unmapped_and_unbound_taxonomy_term_data(self) -> None:
		audit, mapping, seed = valid_artifacts()
		audit_field = audit["entities"][0]["fields"][0]
		audit_field.update(
			{
				"dataClass": "public-content",
				"observedValues": ["Dining"],
				"mediaShape": "none",
			}
		)
		audit["entities"][0]["records"][0]["values"]["Organization.logo.url"] = "Dining"
		field = mapping["fields"][0]
		field.update(
			{
				"ownerKind": "taxonomy",
				"ownerKey": "categories",
				"targetPath": "terms.label",
				"canonicalName": "label",
				"storageSlug": None,
				"type": "string",
				"mediaOwnership": "none",
				"sourceDataClass": "public-content",
			}
		)
		mapping["recordBindings"][0].update(
			{
				"ownerKind": "taxonomy",
				"ownerKey": "categories",
				"targetPointer": "/taxonomies/0/terms/0",
			},
		)
		seed["taxonomies"] = [
			{
				"name": "categories",
				"label": "Categories",
				"hierarchical": False,
				"collections": ["organizations"],
				"terms": [
					{"slug": "dining", "label": "Dining", "description": "Invented"},
					{"slug": "invented", "label": "Invented"},
				],
			},
		]
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("taxonomy term" in error and "without source mappings" in error for error in errors))
		self.assertTrue(any("taxonomy terms without source record bindings" in error for error in errors))

	def test_accepts_required_empty_section_and_taxonomy_metadata_defaults(self) -> None:
		for owner_kind in ("section", "taxonomy"):
			with self.subTest(owner_kind=owner_kind):
				audit, mapping, seed = valid_artifacts()
				audit_field = audit["entities"][0]["fields"][0]
				audit_field.update(
					{
						"dataClass": "public-content",
						"observedValues": ["Heading"],
						"enumDateSemantics": "none",
						"mediaShape": "none",
					},
				)
				audit["entities"][0]["records"][0]["values"]["Organization.logo.url"] = "Heading"
				field = mapping["fields"][0]
				field.update(
					{
						"ownerKind": owner_kind,
						"ownerKey": "hero" if owner_kind == "section" else "categories",
						"targetPath": "title" if owner_kind == "section" else "terms.label",
						"canonicalName": "title" if owner_kind == "section" else "label",
						"storageSlug": None,
						"runtimeReadPath": "title" if owner_kind == "section" else "label",
						"type": "string",
						"mediaOwnership": "none",
						"sourceDataClass": "public-content",
					},
				)
				if owner_kind == "section":
					mapping["recordBindings"][0].update(
						{"ownerKind": "section", "ownerKey": "hero", "targetPointer": "/sections/0"},
					)
					seed["sections"] = [{"slug": "hero", "title": "Heading", "content": []}]
				else:
					mapping["recordBindings"][0].update(
						{
							"ownerKind": "taxonomy",
							"ownerKey": "categories",
							"targetPointer": "/taxonomies/0/terms/0",
						},
					)
					seed["taxonomies"] = [
						{
							"name": "categories",
							"label": "Categories",
							"hierarchical": False,
							"collections": ["organizations"],
							"terms": [{"slug": "heading", "label": "Heading"}],
						},
					]
				self.assertEqual(self.validate_values(audit, mapping, seed), [])

	def test_rejects_fixed_owner_alias_drift(self) -> None:
		audit, mapping, seed = valid_artifacts()
		audit_field = audit["entities"][0]["fields"][0]
		audit_field.update(
			{"dataClass": "public-content", "observedValues": ["Site"], "mediaShape": "none"},
		)
		audit["entities"][0]["records"][0]["values"]["Organization.logo.url"] = "Site"
		field = mapping["fields"][0]
		field.update(
			{
				"ownerKind": "settings",
				"ownerKey": "settings",
				"targetPath": "title",
				"canonicalName": "totallyWrongAlias",
				"storageSlug": None,
				"type": "string",
				"mediaOwnership": "none",
				"sourceDataClass": "public-content",
			}
		)
		mapping["recordBindings"][0].update(
			{"ownerKind": "settings", "ownerKey": "settings", "targetPointer": "/settings"},
		)
		seed["settings"] = {"title": "Site"}
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("canonicalName must match runtime key title" in error for error in errors))

	def test_rejects_nonstandard_nan_json_number(self) -> None:
		audit, mapping, seed = valid_artifacts()
		seed["content"]["organizations"][0]["data"]["featured_image"] = float("nan")
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("invalid seed JSON" in error for error in errors))

	def test_rejects_page_without_visible_document_closure(self) -> None:
		audit, mapping, seed = valid_artifacts()
		del audit["pages"][0]["document"]
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("visible document closure" in error for error in errors))

	def test_rejects_same_line_graphql_mutation_hidden_after_query(self) -> None:
		audit, mapping, seed = valid_artifacts()
		surface = audit["pages"][0]["surfaces"][1]
		document = "query Read { organization { logo { url } } } mutation Delete { deleteAll }"
		document_hash = hashlib.sha256(document.encode()).hexdigest()
		surface.update(
			{
				"kind": "graphql",
				"location": "https://example.com/graphql",
				"transportMethod": "POST",
				"operationType": "query",
				"operationName": "Read",
				"requestDocument": document,
				"requestDocumentHash": document_hash,
				"parameters": f"operationName=Read; documentSha256={document_hash}",
			},
		)
		audit["entities"][0]["sourceLocation"] = "https://example.com/graphql"
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("not a read operation" in error for error in errors))

	def test_rejects_private_network_urls_except_explicit_source_origin(self) -> None:
		for value in (
			"http://127.0.0.1/private",
			"http://169.254.169.254/latest/meta-data",
			"http://localhost/admin",
			"http://service.local/data",
		):
			with self.subTest(value=value):
				self.assertFalse(VALIDATOR.valid_public_url(value))
		self.assertTrue(
			VALIDATOR.valid_public_url(
				"http://127.0.0.1:4322/",
				allowed_private_origins={"http://127.0.0.1:4322"},
			),
		)

	def test_rejects_mobile_contact_misclassified_as_public_content(self) -> None:
		audit, mapping, seed = valid_artifacts()
		field = audit["entities"][0]["fields"][0]
		field.update(
			{
				"ref": "Organization.contactNumber",
				"path": "mobile",
				"dataClass": "public-content",
				"observedValues": ["+65 8123 4567"],
				"enumDateSemantics": "none",
				"mediaShape": "none",
				"uiConsumers": ["Contact"],
			},
		)
		audit["entities"][0]["records"][0]["values"] = {
			"Organization.contactNumber": "+65 8123 4567",
		}
		mapping_field = mapping["fields"][0]
		mapping_field.update(
			{
				"sourceRef": "Organization.contactNumber",
				"sourcePath": "mobile",
				"sourceDataClass": "public-content",
				"targetPath": "contact_number",
				"canonicalName": "contactNumber",
				"storageSlug": "contact_number",
				"type": "string",
				"mediaOwnership": "none",
			},
		)
		seed["collections"][0]["fields"][0].update(
			{"slug": "contact_number", "label": "contactNumber", "type": "string"},
		)
		seed["content"]["organizations"][0]["data"] = {"contact_number": "+65 8123 4567"}
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("contact data must use public-business-contact" in error for error in errors))

	def test_rejects_fake_many_relationship_stored_as_json(self) -> None:
		audit, mapping, seed = valid_artifacts()
		audit_field = audit["entities"][0]["fields"][0]
		audit_field.update(
			{
				"dataClass": "public-content",
				"observedTypes": ["array"],
				"observedValues": [["organization:a"]],
				"relationshipCardinality": "many",
				"enumDateSemantics": "none",
				"mediaShape": "none",
			},
		)
		audit["entities"][0]["records"][0]["values"]["Organization.logo.url"] = ["organization:a"]
		field = mapping["fields"][0]
		field.update(
			{
				"type": "json",
				"mediaOwnership": "none",
				"sourceDataClass": "public-content",
				"relationship": {
					"cardinality": "none",
					"targetOwner": None,
					"sourceCardinality": "many",
					"representation": "link-collection",
				},
			},
		)
		seed["collections"][0]["fields"][0]["type"] = "json"
		seed["content"]["organizations"][0]["data"]["featured_image"] = ["organization:a"]
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("normalize it into source edge records" in error for error in errors))

	def test_rejects_nonconcrete_seed_and_render_consumers(self) -> None:
		audit, mapping, seed = valid_artifacts()
		mapping["fields"][0]["seedConsumers"] = ["N/A"]
		mapping["fields"][0]["renderConsumers"] = ["N/A"]
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("concrete site-root file" in error for error in errors))

	def test_rejects_unmapped_collection_media_metadata(self) -> None:
		audit, mapping, seed = valid_artifacts()
		seed["content"]["organizations"][0]["data"]["featured_image"] = {
			"$media": {"url": "https://example.com/logo.png", "alt": "Invented alt"},
		}
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("media metadata" in error.casefold() for error in errors))

	def test_accepts_source_backed_collection_media_metadata(self) -> None:
		audit, mapping, seed = valid_artifacts()
		alt_ref = "Organization.logo.alt"
		alt_field = {
			"ref": alt_ref,
			"path": "logo.alt",
			"observedTypes": ["string"],
			"dataClass": "public-content",
			"nullable": False,
			"observedValues": ["Example logo"],
			"identifierRole": "none",
			"enumDateSemantics": "none",
			"relationshipCardinality": "none",
			"localeStatus": "public/default",
			"mediaShape": "none",
			"uiConsumers": ["Header"],
			"evidence": ["docs/research/example/SOURCE_API_AUDIT.md#organization-logo"],
		}
		audit["entities"][0]["fields"].append(alt_field)
		audit["entities"][0]["records"][0]["values"][alt_ref] = "Example logo"
		audit["pages"][0]["document"]["visibleEntities"][0]["visibleFieldRefs"].append(alt_ref)
		mapping["fields"][0]["mediaMetadata"] = {"altSourceRef": alt_ref}
		alt_mapping = copy.deepcopy(mapping["fields"][0])
		alt_mapping.update(
			{
				"sourceRef": alt_ref,
				"sourcePath": "logo.alt",
				"sourceDataClass": "public-content",
				"targetPath": "featured_image_alt",
				"canonicalName": "featuredImageAlt",
				"storageSlug": "featured_image_alt",
				"runtimeReadPath": "data.featured_image_alt",
				"type": "string",
				"nullable": False,
				"mediaOwnership": "none",
			},
		)
		alt_mapping.pop("mediaMetadata", None)
		mapping["fields"].append(alt_mapping)
		seed["collections"][0]["fields"].append(
			{"slug": "featured_image_alt", "label": "featuredImageAlt", "type": "string"},
		)
		seed["content"]["organizations"][0]["data"] = {
			"featured_image": {
				"$media": {"url": "https://example.com/logo.png", "alt": "Example logo"},
			},
			"featured_image_alt": "Example logo",
		}
		self.assertEqual(self.validate_values(audit, mapping, seed), [])

	def test_rejects_taxonomy_terms_when_only_taxonomy_metadata_is_mapped(self) -> None:
		audit, mapping, seed = valid_artifacts()
		audit_field = audit["entities"][0]["fields"][0]
		audit_field.update(
			{
				"dataClass": "public-content",
				"observedValues": ["Categories"],
				"enumDateSemantics": "none",
				"mediaShape": "none",
			},
		)
		audit["entities"][0]["records"][0]["values"]["Organization.logo.url"] = "Categories"
		field = mapping["fields"][0]
		field.update(
			{
				"ownerKind": "taxonomy",
				"ownerKey": "categories",
				"targetPath": "label",
				"canonicalName": "label",
				"storageSlug": None,
				"type": "string",
				"mediaOwnership": "none",
				"sourceDataClass": "public-content",
			},
		)
		mapping["recordBindings"][0].update(
			{"ownerKind": "taxonomy", "ownerKey": "categories", "targetPointer": "/taxonomies/0"},
		)
		seed["taxonomies"] = [
			{
				"name": "categories",
				"label": "Categories",
				"hierarchical": False,
				"collections": ["organizations"],
				"terms": [{"slug": "secret", "label": "Invented", "description": "Hardcoded visual copy"}],
			},
		]
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("taxonomy terms without term-level source mappings" in error for error in errors))

	def test_rejects_agent_self_authorized_metadata_origin(self) -> None:
		audit, mapping, seed = valid_artifacts()
		metadata_url = "http://169.254.169.254/latest/meta-data"
		for page in audit["pages"]:
			page["url"] = metadata_url
			page["document"]["surfaceLocation"] = metadata_url
			for surface in page["surfaces"]:
				surface["location"] = metadata_url
		audit["entities"][0]["sourceLocation"] = metadata_url
		errors = self.validate_values(
			audit,
			mapping,
			seed,
			trusted_explicit_urls=[metadata_url],
		)
		self.assertTrue(any("public HTTP(S) URL" in error or "unsafe/non-public" in error for error in errors))

	def test_rejects_excessively_nested_signed_url_encoding(self) -> None:
		value = "https://example.com/a?signature=secret"
		for _ in range(100):
			value = value.replace("=", "%3d").replace("%", "%25")
		self.assertTrue(VALIDATOR.contains_sensitive_data(value))

	def test_accepts_graphql_query_with_mutation_named_fragment_and_enum_default(self) -> None:
		document = (
			"query Read($type: Op = mutation) { viewer { ...mutation } } "
			"fragment mutation on Viewer { id }"
		)
		document_hash = hashlib.sha256(document.encode()).hexdigest()
		self.assertTrue(
			VALIDATOR.valid_graphql_query_surface(
				{
					"operationName": "Read",
					"requestDocument": document,
					"requestDocumentHash": document_hash,
					"parameters": f"operationName=Read; documentSha256={document_hash}",
				},
			),
		)

	def test_rejects_forbidden_private_identity_fields_even_if_claimed_public(self) -> None:
		for ref, value in (
			("Customer.ssn", "123-45-6789"),
			("Customer.dateOfBirth", "1980-01-01"),
			("Customer.creditCard", "4111111111111111"),
		):
			with self.subTest(ref=ref):
				audit, mapping, seed = valid_artifacts()
				field = audit["entities"][0]["fields"][0]
				field.update(
					{
						"ref": ref,
						"path": ref.split(".", 1)[1],
						"dataClass": "public-business-contact",
						"observedValues": [value],
						"enumDateSemantics": "none",
						"mediaShape": "none",
						"uiConsumers": ["Contact"],
					},
				)
				audit["pages"][0]["document"]["visibleEntities"][0]["visibleFieldRefs"] = [ref]
				audit["entities"][0]["records"][0]["values"] = {ref: value}
				mapping_field = mapping["fields"][0]
				mapping_field.update(
					{
						"sourceRef": ref,
						"sourcePath": ref.split(".", 1)[1],
						"sourceDataClass": "public-business-contact",
						"targetPath": "private_value",
						"canonicalName": "privateValue",
						"storageSlug": "private_value",
						"type": "string",
						"mediaOwnership": "none",
					},
				)
				seed["collections"][0]["fields"][0].update(
					{"slug": "private_value", "label": "privateValue", "type": "string"},
				)
				seed["content"]["organizations"][0]["data"] = {"private_value": value}
				errors = self.validate_values(audit, mapping, seed)
				self.assertTrue(any("forbidden private/account identity data" in error for error in errors))

	def test_rejects_unexecutable_locale_or_publication_status(self) -> None:
		for mutate, marker in (
			(lambda audit, mapping, seed: mapping["fields"][0].update({"statusBehavior": "totally-wrong"}), "statusBehavior"),
			(
				lambda audit, mapping, seed: (
					audit["entities"][0]["fields"][0].update({"localeStatus": "gibberish"}),
					mapping["fields"][0].update({"localeBehavior": "gibberish"}),
				),
				"localeStatus",
			),
			(lambda audit, mapping, seed: seed["content"]["organizations"][0].update({"status": "draft"}), "published"),
		):
			with self.subTest(marker=marker):
				audit, mapping, seed = valid_artifacts()
				mutate(audit, mapping, seed)
				errors = self.validate_values(audit, mapping, seed)
				self.assertTrue(any(marker in error for error in errors))

	def test_rejects_routable_collection_without_exact_seo_contract(self) -> None:
		for url_pattern, supports in (
			("/organizations", ["seo"]),
			("/organizations/{slug}", []),
			("//evil/{slug}", ["seo"]),
			("/../{slug}", ["seo"]),
			("/foo//{slug}", ["seo"]),
		):
			with self.subTest(url_pattern=url_pattern, supports=supports):
				audit, mapping, seed = valid_artifacts()
				seed["collections"][0].update({"urlPattern": url_pattern, "supports": supports})
				errors = self.validate_values(audit, mapping, seed)
				self.assertTrue(any("urlPattern" in error or 'supports ["seo"]' in error for error in errors))

	def test_rejects_source_document_snapshot_drift(self) -> None:
		audit, mapping, seed = valid_artifacts()
		document_snapshot = {
			"version": "1",
			"pages": [
				{
					"url": "https://example.com/",
					"capturedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
					"items": [
						{
							"itemId": "invented",
							"kind": "media",
							"selector": "header img",
							"sourceEntity": "Organization",
							"sourceRef": "Organization.logo.url",
							"sourceRecordId": "organization:example",
							"value": "https://example.com/invented.png",
						},
					],
				},
			],
		}
		errors = self.validate_values(audit, mapping, seed, document_snapshot=document_snapshot)
		self.assertTrue(any("document snapshot" in error for error in errors))

	def test_rejects_comment_only_render_consumer(self) -> None:
		for decoy in (
			'// const { entries, cacheHint } = await getDinewayCollection("organizations"); Astro.cache.set(cacheHint); featured_image',
			'const decoy = \'const { entries, cacheHint } = await getDinewayCollection("organizations"); Astro.cache.set(cacheHint); featured_image\';',
			'async function getDinewayCollection() { return { entries: [{ data: { featured_image: "hardcoded" } }], cacheHint: {} }; }\nconst { entries, cacheHint } = await getDinewayCollection("organizations"); Astro.cache.set(cacheHint); const featured_image = entries[0].data.featured_image;',
		):
			with self.subTest(decoy=decoy):
				audit, mapping, seed = valid_artifacts()
				errors = self.validate_values(
					audit,
					mapping,
					seed,
					render_source=f'---\n{decoy}\nconst value = "hardcoded";\n---\n<div>{{value}}</div>',
				)
				self.assertTrue(
					any("owner-specific Dineway read" in error or "not imported" in error for error in errors),
				)

	def test_rejects_query_helper_from_incomplete_server_runtime_barrel(self) -> None:
		audit, mapping, seed = valid_artifacts()
		render_source = '''---
import { getDinewayEntry } from "dineway/ui/server-runtime";
const { entry, cacheHint } = await getDinewayEntry("organizations", "example");
Astro.cache.set(cacheHint);
const value = entry?.data?.featured_image;
---
<div>{value}</div>
'''
		errors = self.validate_values(audit, mapping, seed, render_source=render_source)
		self.assertTrue(any("not imported from the Dineway runtime" in error for error in errors))

	def test_rejects_wrong_slug_for_planned_routable_destination(self) -> None:
		audit, mapping, seed = valid_artifacts()
		seed["collections"][0].update(
			{"urlPattern": "/organizations/{slug}", "supports": ["seo"]},
		)
		row = "| https://example.com/ | explicit | N/A | none | / | include |"
		planned = "| https://example.com/ | explicit | N/A | none | /organizations/example | include |"
		self.assertEqual(
			self.validate_values(audit, mapping, seed, agent_replacements=((row, planned),)),
			[],
		)
		seed["content"]["organizations"][0]["slug"] = "wrong-route"
		errors = self.validate_values(audit, mapping, seed, agent_replacements=((row, planned),))
		self.assertTrue(any("planned destination route" in error for error in errors))

	def test_rejects_planned_destination_without_astro_route(self) -> None:
		audit, mapping, seed = valid_artifacts()
		seed["collections"][0].update(
			{"urlPattern": "/organizations/{slug}", "supports": ["seo"]},
		)
		row = "| https://example.com/ | explicit | N/A | none | / | include |"
		planned = "| https://example.com/ | explicit | N/A | none | /organizations/example | include |"
		errors = self.validate_values(
			audit,
			mapping,
			seed,
			agent_replacements=((row, planned),),
			create_route_files=False,
		)
		self.assertTrue(any("no executable Astro SSR route" in error for error in errors))

	def test_rejects_malformed_ports_and_ambiguous_loopback_ipv4(self) -> None:
		for value in (
			"http://127.0.0.1:99999/",
			"https://example.com:99999/",
			"http://[::1/",
			"http://2130706433/",
			"http://0x7f000001/",
			"http://017700000001/",
			"http://127.1/",
			"http://127.0.1/",
		):
			with self.subTest(value=value):
				self.assertFalse(VALIDATOR.valid_public_url(value))

	def test_uses_runtime_read_alias_for_taxonomy_parent(self) -> None:
		self.assertEqual(VALIDATOR.expected_runtime_read_path("taxonomy", "terms.parent", None), "parentId")

	def test_rejects_canonical_name_collision_within_owner(self) -> None:
		audit, mapping, seed = valid_artifacts()
		second_ref = "Organization.tagline"
		audit["entities"][0]["fields"].append(
			{
				"ref": second_ref,
				"path": "tagline",
				"observedTypes": ["string"],
				"dataClass": "public-content",
				"nullable": False,
				"observedValues": ["Dining"],
				"identifierRole": "none",
				"enumDateSemantics": "none",
				"relationshipCardinality": "none",
				"localeStatus": "public/default",
				"mediaShape": "none",
				"uiConsumers": ["Header"],
				"evidence": ["docs/research/example/SOURCE_API_AUDIT.md#organization-logo"],
			},
		)
		audit["entities"][0]["records"][0]["values"][second_ref] = "Dining"
		audit["pages"][0]["document"]["visibleEntities"][0]["visibleFieldRefs"].append(second_ref)
		second_mapping = copy.deepcopy(mapping["fields"][0])
		second_mapping.update(
			{
				"sourceRef": second_ref,
				"sourcePath": "tagline",
				"sourceDataClass": "public-content",
				"targetPath": "featured__image",
				"canonicalName": "featuredImage",
				"storageSlug": "featured__image",
				"runtimeReadPath": "data.featured__image",
				"type": "string",
				"required": False,
				"nullable": False,
				"mediaOwnership": "none",
			},
		)
		mapping["fields"].append(second_mapping)
		seed["collections"][0]["fields"].append(
			{"slug": "featured__image", "label": "featuredImage", "type": "string"},
		)
		seed["content"]["organizations"][0]["data"]["featured__image"] = "Dining"
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("collides at Dineway canonicalName" in error for error in errors))

	def test_rejects_high_confidence_private_values_under_generic_field_names(self) -> None:
		for value in ("4111111111111111", "123-45-6789"):
			with self.subTest(value=value):
				audit, mapping, seed = valid_artifacts()
				field = audit["entities"][0]["fields"][0]
				field.update(
					{
						"dataClass": "public-identifier",
						"observedValues": [value],
						"enumDateSemantics": "none",
						"mediaShape": "none",
					},
				)
				audit["entities"][0]["records"][0]["values"]["Organization.logo.url"] = value
				mapping["fields"][0].update(
					{
						"sourceDataClass": "public-identifier",
						"type": "string",
						"mediaOwnership": "none",
					},
				)
				seed["collections"][0]["fields"][0]["type"] = "string"
				seed["content"]["organizations"][0]["data"]["featured_image"] = value
				errors = self.validate_values(audit, mapping, seed)
				self.assertTrue(any("forbidden private/account identity data" in error for error in errors))

	def test_requires_localized_mapping_to_match_bound_seed_locale(self) -> None:
		for locale in (None, "en"):
			with self.subTest(locale=locale):
				audit, mapping, seed = valid_artifacts()
				audit["entities"][0]["fields"][0]["localeStatus"] = "localized/fr"
				mapping["fields"][0]["localeBehavior"] = "localized/fr"
				if locale is not None:
					seed["content"]["organizations"][0]["locale"] = locale
				errors = self.validate_values(audit, mapping, seed)
				self.assertTrue(any("seed locale fr" in error for error in errors))
		audit, mapping, seed = valid_artifacts()
		audit["entities"][0]["fields"][0]["localeStatus"] = "localized/fr"
		mapping["fields"][0]["localeBehavior"] = "localized/fr"
		seed["content"]["organizations"][0]["locale"] = "fr"
		self.assertEqual(self.validate_values(audit, mapping, seed), [])

	def test_rejects_repeater_items_with_unmodeled_source_keys(self) -> None:
		audit, mapping, seed = valid_artifacts()
		cards = [{"title": "Burger", "description": "Grass-fed", "price": 19.5}]
		audit["entities"][0]["fields"][0].update(
			{
				"observedTypes": ["array"],
				"dataClass": "public-content",
				"observedValues": [cards],
				"enumDateSemantics": "none",
				"mediaShape": "none",
			},
		)
		audit["entities"][0]["records"][0]["values"]["Organization.logo.url"] = cards
		mapping["fields"][0].update(
			{
				"type": "repeater",
				"sourceDataClass": "public-content",
				"mediaOwnership": "none",
				"validation": {
					"subFields": [
						{"slug": "title", "label": "title", "type": "string", "required": True},
					],
				},
			},
		)
		seed["collections"][0]["fields"][0].update(
			{
				"type": "repeater",
				"validation": mapping["fields"][0]["validation"],
			},
		)
		seed["content"]["organizations"][0]["data"]["featured_image"] = cards
		errors = self.validate_values(audit, mapping, seed)
		self.assertTrue(any("incompatible with Dineway type repeater" in error for error in errors))

	def test_rejects_browser_media_downgraded_to_plain_content(self) -> None:
		audit, mapping, seed = valid_artifacts()
		audit["entities"][0]["fields"][0].update(
			{"dataClass": "public-content", "mediaShape": "none", "enumDateSemantics": "none"},
		)
		mapping["fields"][0].update(
			{
				"sourceDataClass": "public-content",
				"targetPath": "logo_url",
				"canonicalName": "logoUrl",
				"storageSlug": "logo_url",
				"runtimeReadPath": "data.logo_url",
				"type": "string",
				"mediaOwnership": "none",
			},
		)
		seed["collections"][0]["fields"][0].update(
			{"slug": "logo_url", "label": "logoUrl", "type": "string"},
		)
		seed["content"]["organizations"][0]["data"] = {"logo_url": "https://example.com/logo.png"}
		document_snapshot = {
			"version": "1",
			"pages": [
				{
					"url": "https://example.com/",
					"capturedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
					"items": [
						{
							"itemId": "logo",
							"kind": "media",
							"selector": "header img",
							"sourceEntity": "Organization",
							"sourceRef": "Organization.logo.url",
							"sourceRecordId": "organization:example",
							"value": "https://example.com/logo.png",
						},
					],
				},
			],
		}
		errors = self.validate_values(audit, mapping, seed, document_snapshot=document_snapshot)
		self.assertTrue(any("browser media and public-media classification" in error for error in errors))

	def test_requires_reversible_runtime_content_proof_for_every_mapped_selector(self) -> None:
		audit, mapping, seed = valid_artifacts()
		errors = self.validate_values(
			audit,
			mapping,
			seed,
			runtime_content_proof={"version": "1", "proofs": []},
		)
		self.assertTrue(any("runtime content proof must contain" in error for error in errors))

	def test_rejects_collection_media_restored_to_wrong_content_hash(self) -> None:
		audit, mapping, seed = valid_artifacts()
		source_hash = "sha1:" + hashlib.sha1(b"source-logo").hexdigest()
		wrong_hash = "sha1:" + hashlib.sha1(b"wrong-logo").hexdigest()
		sentinel_hash = "sha1:" + hashlib.sha1(b"sentinel-logo").hexdigest()
		wrong_url = "http://127.0.0.1:4321/_dineway/media/wrong.png"
		sentinel_url = "http://127.0.0.1:4321/_dineway/media/sentinel.png"
		runtime_content_proof = {
			"version": "1",
			"proofs": [
				{
					"pageUrl": "https://example.com/",
					"snapshotItemId": "Organization.logo.url:0",
					"sourceEntity": "Organization",
					"sourceRecordId": "organization:example",
					"sourceRef": "Organization.logo.url",
					"sourceValue": "https://example.com/logo.png",
					"ownerKind": "collection",
					"ownerKey": "organizations",
					"runtimeReadPath": "data.featured_image",
					"renderConsumer": "src/pages/index.astro",
					"selector": "header img",
					"cloneUrl": "http://127.0.0.1:4321/",
					"capturedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
					"mediaProof": {
						"sourceSnapshot": "docs/research/example/runtime-source-logo.bin",
						"sourceContentHash": source_hash,
						"before": {
							"mediaId": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
							"resolvedUrl": wrong_url,
							"contentHash": wrong_hash,
							"mimeType": "image/png",
						},
						"sentinel": {
							"mediaId": "01ARZ3NDEKTSV4RRFFQ69G5FAW",
							"resolvedUrl": sentinel_url,
							"contentHash": sentinel_hash,
							"mimeType": "image/png",
						},
						"restore": {
							"mediaId": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
							"resolvedUrl": wrong_url,
							"contentHash": wrong_hash,
							"mimeType": "image/png",
						},
					},
					"before": {"liveReadStatus": 200, "ssrStatus": 200, "observedValue": wrong_url},
					"sentinel": {
						"value": sentinel_url,
						"writeStatus": 200,
						"liveReadStatus": 200,
						"ssrStatus": 200,
						"observedValue": sentinel_url,
					},
					"restore": {
						"writeStatus": 200,
						"liveReadStatus": 200,
						"ssrStatus": 200,
						"observedValue": wrong_url,
					},
				},
			],
		}
		errors = self.validate_values(audit, mapping, seed, runtime_content_proof=runtime_content_proof)
		self.assertTrue(any("source content hash" in error for error in errors))

	def test_runtime_proof_preserves_each_repeated_record_occurrence(self) -> None:
		captured_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
		mapping = {
			"Card.title": {
				"ownerKind": "collection",
				"ownerKey": "cards",
				"runtimeReadPath": "data.title",
				"renderConsumers": ["src/pages/index.astro"],
			},
		}
		snapshot = {
			"pages": [
				{
					"url": "https://example.com/",
					"items": [
						{
							"itemId": f"card-{index}",
							"sourceEntity": "Card",
							"sourceRecordId": f"card:{index}",
							"sourceRef": "Card.title",
							"selector": ".card .title",
							"value": value,
						}
						for index, value in enumerate(("One", "Two"), start=1)
					],
				},
			],
		}
		proof = {
			"version": "1",
			"proofs": [
				{
					"pageUrl": "https://example.com/",
					"snapshotItemId": "card-1",
					"sourceEntity": "Card",
					"sourceRecordId": "card:1",
					"sourceRef": "Card.title",
					"sourceValue": "One",
					"ownerKind": "collection",
					"ownerKey": "cards",
					"runtimeReadPath": "data.title",
					"renderConsumer": "src/pages/index.astro",
					"selector": ".card .title",
					"cloneUrl": "http://127.0.0.1:4321/",
					"capturedAt": captured_at,
					"mediaProof": None,
					"before": {"liveReadStatus": 200, "ssrStatus": 200, "observedValue": "One"},
					"sentinel": {
						"value": "Probe",
						"writeStatus": 200,
						"liveReadStatus": 200,
						"ssrStatus": 200,
						"observedValue": "Probe",
					},
					"restore": {
						"writeStatus": 200,
						"liveReadStatus": 200,
						"ssrStatus": 200,
						"observedValue": "One",
					},
				},
			],
		}
		errors: list[str] = []
		VALIDATOR.validate_runtime_content_proof(
			proof,
			mapping,
			snapshot,
			{"Card.title": {"dataClass": "public-content"}},
			{
				("Card", "card:1"): {"values": {"Card.title": "One"}},
				("Card", "card:2"): {"values": {"Card.title": "Two"}},
			},
			"http://127.0.0.1:4321/",
			Path.cwd(),
			errors,
		)
		self.assertTrue(any("without reversible live proofs" in error for error in errors))


if __name__ == "__main__":
	unittest.main()

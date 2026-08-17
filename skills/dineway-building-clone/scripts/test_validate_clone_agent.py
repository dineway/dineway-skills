#!/usr/bin/env python3
"""Regression tests for the clone-agent contract validator."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = SCRIPT_DIR.parent / "references" / "clone-agent-template.md"
SPEC = importlib.util.spec_from_file_location(
	"validate_clone_agent",
	SCRIPT_DIR / "validate_clone_agent.py",
)
if SPEC is None or SPEC.loader is None:
	raise RuntimeError("Unable to load validate_clone_agent.py")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def generated_agent() -> str:
	text = TEMPLATE_PATH.read_text(encoding="utf-8")
	replacements = {
		"{{CLONE_SLUG}}": "example-clone",
		"{{SOURCE_ORIGINS}}": "https://example.com",
		"{{CLONE_NAME}}": "Example",
		"{{ORIGINAL_REQUEST}}": "Clone https://example.com as a CMS-backed Dineway Site.",
		"{{EXPLICIT_URLS}}": "https://example.com/",
		"{{SITE_ROOT}}": "/tmp/example-clone",
		"{{TARGET_IDENTITY}}": "Example",
		"{{APPROVED_CUSTOMIZATIONS}}": "None approved.",
		"{{SOURCE_URL_PLAN_ROWS}}": "| https://example.com/ | explicit | N/A | none | / | include |",
		"{{ROUTE_AND_ARTIFACT_ROWS}}": "| https://example.com/ | explicit | N/A | / | root | organizations/example | example-com-a1b2c3d4 | root-e3b0c442 | docs/research/example/root | docs/design-references/example/root | src/components/sites/example/root | public/sites/example/root | none |",
		"{{SOURCE_DATA_LAYER_AUDIT}}": "Public JSON-LD at https://example.com/ describes the visible Organization entity; no mutations are in scope.",
		"{{SOURCE_DATA_LAYER_ROWS}}": "| https://example.com/ | JSON-LD | https://example.com/#organization | embedded | embedded | anonymous-public | initial load | none | filter=none; sort=none | Organization | Header | SOURCE_API_AUDIT.md |",
		"{{SOURCE_PAGE_CONTENT_ROWS}}": "| https://example.com/ | https://example.com/ | Organization | Organization.logo.url | organization:example | header img | SOURCE_API_AUDIT.md#organization |",
		"{{SOURCE_FIELD_INVENTORY_ROWS}}": '| Organization.logo.url | Organization | logo.url | string | true | public-media | ["https://example.com/logo.png"] | none | URL | none | public/default | image URL | Header | SOURCE_API_AUDIT.md |',
		"{{SOURCE_RECORD_INVENTORY_ROWS}}": '| Organization | organization:example | {"Organization.logo.url":"https://example.com/logo.png"} | Header | SOURCE_API_AUDIT.md#organization-logo |',
		"{{DINEWAY_CMS_MODEL}}": "The Organization maps to the organizations collection and homepage route.",
		"{{SOURCE_ENTITY_MAPPING_ROWS}}": "| Organization | https://example.com/#organization | collection | organizations | / and Header | SOURCE_API_AUDIT.md |",
		"{{SOURCE_FIELD_MAPPING_ROWS}}": '| Organization.logo.url | collection | organizations | featured_image | featuredImage | featured_image | image | required=false; nullable=true | validation={}; options={} | {"cardinality":"none","targetOwner":null} | locale=public/default; status=published | cms | seed=seed/seed.json#content.organizations; render=src/pages/index.astro | SOURCE_API_AUDIT.md |',
		"{{SOURCE_RECORD_BINDING_ROWS}}": "| Organization | organization:example | collection | organizations | /content/organizations/0 | FIELD_MAPPING.md#organization-example |",
		"{{CHANGE_BUDGET}}": "Approved changes: none. Protected invariants: all observed source behavior and appearance.",
		"{{ENGINEERING_CONSTRAINTS}}": "Use Astro SSR, Dineway seed validation, generated types, browser QA, and repository checks.",
	}
	for placeholder, value in replacements.items():
		text = text.replace(placeholder, value)
	return text


class ValidateCloneAgentTests(unittest.TestCase):
	def validate_text(self, text: str) -> list[str]:
		with tempfile.TemporaryDirectory() as directory:
			path = Path(directory) / "agent-example-clone.md"
			path.write_text(text, encoding="utf-8")
			return VALIDATOR.validate(path, template=False)

	def test_accepts_a_concrete_agent_with_camel_case_mapping(self) -> None:
		self.assertEqual(self.validate_text(generated_agent()), [])

	def test_rejects_non_camel_case_canonical_field(self) -> None:
		text = generated_agent().replace("| featuredImage | featured_image |", "| featured_image | featured_image |")
		errors = self.validate_text(text)
		self.assertTrue(any("must be lower camelCase" in error for error in errors))

	def test_rejects_modified_execution_contract(self) -> None:
		text = generated_agent().replace(
			"For each section, repeat the original core loop: **extract → spec → dispatch → merge**.",
			"For each section, build it quickly.",
		)
		errors = self.validate_text(text)
		self.assertTrue(any("execution contract differs" in error for error in errors))

	def test_rejects_modified_hard_gate(self) -> None:
		text = generated_agent().replace(
			"Treat every gate as fail-closed.",
			"Treat every gate as optional.",
		)
		errors = self.validate_text(text)
		self.assertTrue(any("outside resolved placeholders" in error for error in errors))

	def test_rejects_visual_only_audit_and_unredacted_credentials(self) -> None:
		text = generated_agent().replace(
			"Public JSON-LD at https://example.com/ describes the visible Organization entity; no mutations are in scope.",
			"Skipped; visual-only.\nAuthorization: Bearer secret-token-value",
		)
		errors = self.validate_text(text)
		self.assertTrue(any("may not be skipped" in error for error in errors))
		self.assertTrue(any("unredacted credential" in error for error in errors))

	def test_rejects_reserved_custom_storage_slug(self) -> None:
		text = generated_agent().replace("| featured_image | image |", "| id | image |")
		errors = self.validate_text(text)
		self.assertTrue(any("uses reserved storageSlug id" in error for error in errors))

	def test_rejects_field_mapping_without_matching_source_inventory(self) -> None:
		text = generated_agent().replace(
			"| Organization.logo.url | collection | organizations |",
			"| Organization.name | collection | organizations |",
		)
		errors = self.validate_text(text)
		self.assertTrue(any("source field inventory and Dineway mappings differ" in error for error in errors))

	def test_accepts_anonymous_graphql_query_over_post(self) -> None:
		text = generated_agent().replace(
			"| https://example.com/ | JSON-LD | https://example.com/#organization | embedded | embedded | anonymous-public |",
			"| https://example.com/ | GraphQL | https://example.com/graphql | POST | query | anonymous-public |",
		)
		text = text.replace(
			"| Organization | https://example.com/#organization | collection |",
			"| Organization | https://example.com/graphql | collection |",
		)
		text = text.replace(
			"| query | anonymous-public | initial load |",
			"| query | anonymous-public | operationName=OrganizationQuery; documentSha256=ecc7806f726b8ab4a4b50a2d49bb93fc68b88839f58ad601d6f99003cbc1a615 |",
		)
		self.assertEqual(self.validate_text(text), [])

	def test_rejects_unknown_operation_type_on_get(self) -> None:
		text = generated_agent().replace(
			"| embedded | embedded | anonymous-public |",
			"| GET | delete | anonymous-public |",
		)
		errors = self.validate_text(text)
		self.assertTrue(any("not an anonymous read" in error for error in errors))

	def test_rejects_unsafe_surface_location(self) -> None:
		text = generated_agent().replace(
			"https://example.com/#organization | embedded | embedded",
			"javascript:deleteAll() | GET | read",
		)
		errors = self.validate_text(text)
		self.assertTrue(any("location must be a public HTTP(S) URL" in error for error in errors))

	def test_rejects_missing_response_entity_mapping(self) -> None:
		text = generated_agent().replace(
			"| Organization | Header | SOURCE_API_AUDIT.md |",
			"| MissingEntity | Header | SOURCE_API_AUDIT.md |",
			1,
		)
		errors = self.validate_text(text)
		self.assertTrue(any("response entity has no entity mapping" in error for error in errors))

	def test_rejects_non_path_evidence(self) -> None:
		text = generated_agent().replace(
			"| Header | SOURCE_API_AUDIT.md |",
			"| Header | self-attested |",
			1,
		)
		errors = self.validate_text(text)
		self.assertTrue(any("evidence must be a concrete Markdown path" in error for error in errors))

	def test_rejects_private_source_data_class(self) -> None:
		text = generated_agent().replace("| true | public-media |", "| true | private-account |")
		errors = self.validate_text(text)
		self.assertTrue(any("allowed public data class" in error for error in errors))

	def test_rejects_signed_url_and_private_account_field(self) -> None:
		for marker in (
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
			with self.subTest(marker=marker):
				text = generated_agent().replace("https://example.com/logo.png", marker)
				errors = self.validate_text(text)
				self.assertTrue(any("signed URL" in error or "personal/account" in error for error in errors))

	def test_rejects_duplicate_source_field_mapping(self) -> None:
		row = '| Organization.logo.url | collection | organizations | featured_image | featuredImage | featured_image | image | required=false; nullable=true | validation={}; options={} | {"cardinality":"none","targetOwner":null} | locale=public/default; status=published | cms | seed=seed/seed.json#content.organizations; render=src/pages/index.astro | SOURCE_API_AUDIT.md |'
		text = generated_agent().replace(row, f"{row}\n{row}")
		errors = self.validate_text(text)
		self.assertTrue(any("duplicate source refs" in error for error in errors))

	def test_rejects_entity_mapping_owner_or_location_drift(self) -> None:
		text = generated_agent().replace(
			"| Organization | https://example.com/#organization | collection | organizations | / and Header | SOURCE_API_AUDIT.md |",
			"| Organization | https://example.com/wrong | settings | wrongOwner | /wrong | SOURCE_API_AUDIT.md |",
		)
		errors = self.validate_text(text)
		self.assertTrue(any("source location must match" in error for error in errors))
		self.assertTrue(any("do not match source field owners" in error for error in errors))

	def test_rejects_duplicate_url_and_surface_rows(self) -> None:
		text = generated_agent()
		source_row = "| https://example.com/ | explicit | N/A | none | / | include |"
		data_row = "| https://example.com/ | JSON-LD | https://example.com/#organization | embedded | embedded | anonymous-public | initial load | none | filter=none; sort=none | Organization | Header | SOURCE_API_AUDIT.md |"
		text = text.replace(source_row, f"{source_row}\n{source_row}")
		text = text.replace(data_row, f"{data_row}\n{data_row}")
		errors = self.validate_text(text)
		self.assertTrue(any("duplicate URL rows" in error for error in errors))
		self.assertTrue(any("duplicate surface rows" in error for error in errors))


if __name__ == "__main__":
	unittest.main()

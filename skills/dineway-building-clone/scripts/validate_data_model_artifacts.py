#!/usr/bin/env python3
"""Validate source-audit → Dineway mapping → seed closure for clone executions."""

from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta, timezone
import hashlib
import ipaddress
import json
import math
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit


CAMEL_CASE_PATTERN = re.compile(r"^[a-z][A-Za-z0-9]*$")
STORAGE_SLUG_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
SENSITIVE_DATA_PATTERN = re.compile(
	r'''(?im)["']?\b(authorization|proxy-authorization|cookie|set-cookie|x-api-key|password)["']?\s*:\s*(?!["']?(?:<?redacted>?|\[redacted\]))["']?\S+|["']?(api[_-]?key|access[_-]?token|refresh[_-]?token|token|session|client[_-]?secret|private[_-]?key|x-amz-credential|x-amz-signature|x-goog-credential|x-goog-signature)["']?\s*[=:]\s*(?!["']?(?:<?redacted>?|\[redacted\]))["']?\S+|[?&](?:x-amz-credential|x-amz-signature|x-amz-security-token|x-goog-credential|x-goog-signature|signature|sig|key-pair-id|auth|token|access_token|api[_-]?key)=[^&#\s"']+|https?://[^/\s:@]+:[^@\s/]+@|(?:^|\s)-u\s+\S+:\S+|\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----''',
)
PRIVATE_PII_PATTERN = re.compile(
	r"(?i)\b(?:personal|private|customer|user|member|guest|subscriber|account|billing)(?:[._/-][A-Za-z0-9_-]+)*[._-]?(?:email|phone|address|name)\b",
)
ULID_PATTERN = re.compile(r"^[0-9A-HJKMNP-TV-Z]{26}$")
CONTENT_HASH_PATTERN = re.compile(r"^sha1:[0-9a-f]{40}$")
MEDIA_METADATA_SOURCE_KEYS = {
	"alt": "altSourceRef",
	"filename": "filenameSourceRef",
	"caption": "captionSourceRef",
}
EMAIL_VALUE_PATTERN = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
CONTACT_FIELD_TOKENS = {
	"address",
	"cell",
	"contact_number",
	"email",
	"mobile",
	"phone",
	"postal_address",
	"telephone",
	"whatsapp",
}
FORBIDDEN_PRIVATE_FIELD_TOKENS = {
	"bank_account",
	"birth_date",
	"card_number",
	"credit_card",
	"cvv",
	"date_of_birth",
	"dob",
	"ip_address",
	"national_id",
	"passport",
	"routing_number",
	"social_security",
	"ssn",
}
PHONE_VALUE_PATTERN = re.compile(r"(?<!\w)\+?\d[\d ()-]{7,}\d(?!\w)")
SSN_VALUE_PATTERN = re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)")
PUBLIC_CONTACT_CONSUMER_PATTERN = re.compile(r"(?i)(contact|footer|location|business|restaurant|venue)")
MIME_TYPE_PATTERN = re.compile(r"^[a-z0-9][a-z0-9!#$&^_+\-.]*/[a-z0-9!#$&^_+\-.]*$", re.IGNORECASE)
REPEATER_SUBFIELD_TYPES = {
	"string",
	"text",
	"url",
	"number",
	"integer",
	"boolean",
	"datetime",
	"select",
	"image",
}

FIELD_TYPES = {
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
RESERVED_COLLECTION_SLUGS = {
	"content",
	"media",
	"users",
	"revisions",
	"taxonomies",
	"options",
	"audit_logs",
}
SEEDABLE_SYSTEM_FIELDS = {"id": "string", "slug": "slug", "status": "select"}
OWNER_KINDS = {"collection", "settings", "menu", "section", "taxonomy"}
COLLECTION_SUPPORTS = {"drafts", "revisions", "preview", "scheduling", "search", "seo"}
SETTING_PATHS = {
	"title",
	"tagline",
	"logo",
	"favicon",
	"url",
	"postsPerPage",
	"dateFormat",
	"timezone",
	"social.twitter",
	"social.github",
	"social.facebook",
	"social.instagram",
	"social.linkedin",
	"social.youtube",
	"seo.titleSeparator",
	"seo.defaultOgImage",
	"seo.robotsTxt",
	"seo.googleVerification",
	"seo.bingVerification",
}
MENU_ITEM_PATHS = {"label", "url", "ref", "collection", "target", "titleAttr", "cssClasses", "children"}
MENU_CANONICAL_NAMES = {
	"label": "label",
	"url": "customUrl",
	"ref": "referenceId",
	"collection": "referenceCollection",
	"target": "target",
	"titleAttr": "titleAttr",
	"cssClasses": "cssClasses",
	"children": "children",
}
SECTION_PATHS = {"title", "description", "keywords", "content"}
TAXONOMY_PATHS = {
	"label",
	"labelSingular",
	"hierarchical",
	"collections",
	"terms.slug",
	"terms.label",
	"terms.description",
	"terms.parent",
}
FIXED_OWNER_TYPES = {
	"settings": {
		"title": {"string"},
		"tagline": {"string", "text"},
		"logo": {"image"},
		"favicon": {"image"},
		"url": {"url"},
		"postsPerPage": {"integer"},
		"dateFormat": {"string"},
		"timezone": {"string"},
		"social.twitter": {"url", "string"},
		"social.github": {"url", "string"},
		"social.facebook": {"url", "string"},
		"social.instagram": {"url", "string"},
		"social.linkedin": {"url", "string"},
		"social.youtube": {"url", "string"},
		"seo.titleSeparator": {"string"},
		"seo.defaultOgImage": {"image"},
		"seo.robotsTxt": {"text"},
		"seo.googleVerification": {"string"},
		"seo.bingVerification": {"string"},
	},
	"menu": {
		"label": {"string"},
		"url": {"url", "string"},
		"ref": {"reference", "string"},
		"collection": {"string"},
		"target": {"select", "string"},
		"titleAttr": {"string"},
		"cssClasses": {"string"},
		"children": {"repeater"},
	},
	"section": {
		"title": {"string"},
		"description": {"text", "string"},
		"keywords": {"multiSelect"},
		"content": {"portableText"},
	},
	"taxonomy": {
		"label": {"string"},
		"labelSingular": {"string"},
		"hierarchical": {"boolean"},
		"collections": {"multiSelect"},
		"terms.slug": {"slug"},
		"terms.label": {"string"},
		"terms.description": {"text", "string"},
		"terms.parent": {"reference", "string"},
	},
}
OBSERVED_TYPES = {"string", "integer", "number", "boolean", "array", "object", "null"}
PUBLIC_DATA_CLASSES = {"public-content", "public-business-contact", "public-identifier", "public-media"}
LOCALE_STATUS_PATTERN = re.compile(
	r"^(?:public/default|public/[a-z0-9]+(?:-[a-z0-9]+)*|localized/[a-z0-9]+(?:-[a-z0-9]+)*)$",
)
OBSERVED_TO_DINEWAY_TYPES = {
	"string": {"string", "text", "url", "datetime", "select", "slug", "image", "file", "reference", "portableText"},
	"integer": {"integer", "number", "string", "text", "select"},
	"number": {"number", "string", "text"},
	"boolean": {"boolean", "string", "select"},
	"array": {"multiSelect", "portableText", "repeater", "json", "reference"},
	"object": {"image", "file", "portableText", "repeater", "json"},
	"null": FIELD_TYPES,
}
READ_OPERATION_TYPES = {
	"get": {"read", "query"},
	"head": {"read", "query"},
	"embedded": {"embedded", "read"},
	"n/a": {"no-public-data"},
}
SURFACE_KINDS = {"html", "hydration", "json-ld", "xhr", "fetch", "rest", "graphql", "no-public-data"}


def decoded_for_security_scan(value: str) -> str:
	if len(value) > 32768:
		return value + "\ntoken=oversized-untrusted-value"
	decoded = value
	for _ in range(128):
		next_value = unquote(decoded)
		if len(next_value) > 32768:
			return next_value[:32768] + "\ntoken=oversized-decoded-value"
		if next_value == decoded:
			return decoded
		decoded = next_value
	return decoded + "\ntoken=excessive-percent-encoding"


def contains_sensitive_data(value: str) -> bool:
	decoded = decoded_for_security_scan(value)
	return bool(SENSITIVE_DATA_PATTERN.search(decoded) or PRIVATE_PII_PATTERN.search(decoded))


def load_json(path: Path, label: str, errors: list[str]) -> tuple[dict[str, Any], str]:
	try:
		raw = path.read_text(encoding="utf-8")
	except OSError as error:
		errors.append(f"cannot read {label} {path}: {error}")
		return {}, ""
	if SENSITIVE_DATA_PATTERN.search(decoded_for_security_scan(raw)):
		errors.append(f"{label} contains an unredacted credential, cookie, token, or signed URL")
	if PRIVATE_PII_PATTERN.search(decoded_for_security_scan(raw)):
		errors.append(f"{label} contains private personal/account data")
	try:
		value = json.loads(raw, parse_constant=lambda constant: (_ for _ in ()).throw(ValueError(constant)))
	except (json.JSONDecodeError, ValueError) as error:
		errors.append(f"invalid {label} JSON: {error}")
		return {}, raw
	if not isinstance(value, dict):
		errors.append(f"{label} root must be an object")
		return {}, raw
	return value, raw


def non_empty_strings(value: object) -> bool:
	return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)


def nested_value(value: object, dotted_path: str) -> object:
	current = value
	for segment in dotted_path.split("."):
		if not isinstance(current, dict) or segment not in current:
			return None
		current = current[segment]
	return current


def nested_value_with_presence(value: object, dotted_path: str) -> tuple[bool, object]:
	current = value
	for segment in dotted_path.split("."):
		if not isinstance(current, dict) or segment not in current:
			return False, None
		current = current[segment]
	return True, current


def find_named(items: object, key: str, expected: str) -> dict[str, Any] | None:
	if not isinstance(items, list):
		return None
	for item in items:
		if isinstance(item, dict) and item.get(key) == expected:
			return item
	return None


def menu_items_contain(items: object, key: str) -> bool:
	if not isinstance(items, list):
		return False
	for item in items:
		if not isinstance(item, dict):
			continue
		if key in item or menu_items_contain(item.get("children"), key):
			return True
	return False


def menu_item_values(items: object, key: str) -> list[object]:
	values: list[object] = []
	if not isinstance(items, list):
		return values
	for item in items:
		if not isinstance(item, dict):
			continue
		if key in item:
			values.append(item[key])
		values.extend(menu_item_values(item.get("children"), key))
	return values


def menu_item_objects(items: object) -> list[dict[str, Any]]:
	objects: list[dict[str, Any]] = []
	if not isinstance(items, list):
		return objects
	for item in items:
		if not isinstance(item, dict):
			continue
		objects.append(item)
		objects.extend(menu_item_objects(item.get("children")))
	return objects


def snake_to_camel(value: str) -> str:
	first, *rest = value.split("_")
	return first + "".join(part[:1].upper() + part[1:] for part in rest)


def fixed_owner_canonical_name(owner_kind: object, target_path: object) -> str | None:
	if not isinstance(target_path, str):
		return None
	if owner_kind == "menu":
		return MENU_CANONICAL_NAMES.get(target_path)
	if owner_kind == "taxonomy" and target_path == "terms.parent":
		return "parentId"
	if owner_kind in {"settings", "section", "taxonomy"}:
		return target_path.rsplit(".", 1)[-1]
	return None


def expected_runtime_read_path(owner_kind: object, target_path: object, storage_slug: object) -> str | None:
	if not isinstance(target_path, str):
		return None
	if owner_kind == "collection":
		if isinstance(storage_slug, str) and storage_slug.startswith("system:"):
			return target_path
		return f"data.{storage_slug}" if isinstance(storage_slug, str) else None
	if owner_kind == "menu":
		return {
			"url": "url",
			"ref": "url",
			"collection": "url",
		}.get(target_path, target_path)
	if owner_kind == "taxonomy" and target_path == "terms.parent":
		return "parentId"
	if owner_kind in {"settings", "section", "taxonomy"}:
		return target_path.rsplit(".", 1)[-1]
	return None


def json_value_type(value: object) -> str:
	if value is None:
		return "null"
	if isinstance(value, bool):
		return "boolean"
	if isinstance(value, int):
		return "integer"
	if isinstance(value, float):
		return "number"
	if isinstance(value, str):
		return "string"
	if isinstance(value, list):
		return "array"
	if isinstance(value, dict):
		return "object"
	return "unsupported"


def field_has_contact_semantics(field: dict[str, Any]) -> bool:
	ref_and_path = f"{field.get('ref', '')} {field.get('path', '')}"
	normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", ref_and_path).casefold()
	token_list = [token for token in re.split(r"[^a-z0-9]+", normalized) if token]
	tokens = set(token_list)
	compound_tokens = {"_".join(pair) for pair in zip(token_list, token_list[1:])}
	has_contact_field_semantics = bool(CONTACT_FIELD_TOKENS & (tokens | compound_tokens))
	values = field.get("observedValues")
	if has_contact_field_semantics:
		return True
	return isinstance(values, list) and any(
		isinstance(value, str) and EMAIL_VALUE_PATTERN.search(value) is not None for value in values
	)


def field_has_forbidden_private_semantics(field: dict[str, Any]) -> bool:
	ref_and_path = f"{field.get('ref', '')} {field.get('path', '')}"
	normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", ref_and_path).casefold()
	token_list = [token for token in re.split(r"[^a-z0-9]+", normalized) if token]
	tokens = set(token_list)
	compound_tokens = {"_".join(pair) for pair in zip(token_list, token_list[1:])}
	return bool(FORBIDDEN_PRIVATE_FIELD_TOKENS & (tokens | compound_tokens))


def luhn_identifier(value: str) -> bool:
	digits = re.sub(r"[ -]", "", value)
	if not digits.isdigit() or not 13 <= len(digits) <= 19 or len(set(digits)) == 1:
		return False
	total = 0
	for index, character in enumerate(reversed(digits)):
		digit = int(character)
		if index % 2 == 1:
			digit *= 2
			if digit > 9:
				digit -= 9
		total += digit
	return total % 10 == 0


def field_has_forbidden_private_values(field: dict[str, Any]) -> bool:
	values = field.get("observedValues")
	return isinstance(values, list) and any(
		isinstance(value, str) and (SSN_VALUE_PATTERN.search(value) is not None or luhn_identifier(value))
		for value in values
	)


def url_origin(value: str) -> str:
	parsed = urlsplit(value)
	host = parsed.hostname or ""
	port_value = parsed.port
	port = f":{port_value}" if port_value is not None else ""
	return f"{parsed.scheme.casefold()}://{host.casefold()}{port}"


def private_or_local_hostname(hostname: str) -> bool:
	host = hostname.rstrip(".").casefold()
	if host == "localhost" or host.endswith(".localhost") or host.endswith(".local"):
		return True
	try:
		address = ipaddress.ip_address(host)
	except ValueError:
		return False
	return any(
		(
			address.is_private,
			address.is_loopback,
			address.is_link_local,
			address.is_reserved,
			address.is_multicast,
			address.is_unspecified,
		)
	)


def private_hostname_can_be_explicit(hostname: str) -> bool:
	host = hostname.rstrip(".").casefold()
	if host == "localhost" or host.endswith(".localhost") or host.endswith(".local"):
		return True
	try:
		address = ipaddress.ip_address(host)
	except ValueError:
		return False
	return (address.is_loopback or address.is_private) and not any(
		(address.is_link_local, address.is_reserved, address.is_multicast, address.is_unspecified)
	)


def valid_public_url(value: object, *, allowed_private_origins: set[str] | None = None) -> bool:
	if not isinstance(value, str) or not value.strip() or contains_sensitive_data(value):
		return False
	try:
		parsed = urlsplit(value)
		hostname = parsed.hostname
		port = parsed.port
	except ValueError:
		return False
	if (
		parsed.scheme not in {"http", "https"}
		or not parsed.netloc
		or parsed.username is not None
		or hostname is None
		or (port is not None and not 1 <= port <= 65535)
	):
		return False
	legacy_ipv4 = re.fullmatch(r"(?:0x[0-9a-f]+|[0-9]+)(?:\.(?:0x[0-9a-f]+|[0-9]+))*", hostname.casefold())
	if legacy_ipv4 is not None:
		parts = hostname.split(".")
		if len(parts) != 4 or any(not part.isdecimal() or (len(part) > 1 and part.startswith("0")) for part in parts):
			return False
		if any(int(part) > 255 for part in parts):
			return False
	if ":" in parsed.netloc and parsed.netloc.count("[") != parsed.netloc.count("]"):
		return False
	if private_or_local_hostname(hostname):
		try:
			return url_origin(value) in (allowed_private_origins or set())
		except ValueError:
			return False
	return True


def valid_runtime_media_url(value: object, *, allowed_private_origins: set[str] | None = None) -> bool:
	if not isinstance(value, str) or not value.strip() or contains_sensitive_data(value):
		return False
	return (value.startswith("/") and not value.startswith("//")) or valid_public_url(
		value,
		allowed_private_origins=allowed_private_origins,
	)


def valid_route_path(value: object, *, pattern: bool = False) -> bool:
	if not isinstance(value, str) or not value.startswith("/") or value.startswith("//"):
		return False
	if value != "/" and value.endswith("/"):
		return False
	if any(character == "\\" or ord(character) < 32 for character in value):
		return False
	if "?" in value or "#" in value:
		return False
	if value == "/":
		return not pattern
	decoded = decoded_for_security_scan(value)
	if decoded.startswith("//") or "\\" in decoded:
		return False
	segments = decoded.split("/")[1:]
	if any(segment in {"", ".", ".."} for segment in segments):
		return False
	if pattern:
		return decoded.count("{slug}") == 1 and "{" not in decoded.replace("{slug}", "")
	return "{" not in decoded and "}" not in decoded


def astro_route_exists(root: Path, destination: str, collections: list[object]) -> bool:
	pages_root = root / "src" / "pages"
	if destination == "/":
		return (pages_root / "index.astro").is_file()
	relative = destination.lstrip("/")
	if (pages_root / f"{relative}.astro").is_file() or (pages_root / relative / "index.astro").is_file():
		return True
	for collection in collections:
		if not isinstance(collection, dict):
			continue
		pattern = collection.get("urlPattern")
		if not isinstance(pattern, str) or not valid_route_path(pattern, pattern=True):
			continue
		matcher = "^" + re.escape(pattern).replace(re.escape("{slug}"), r"[^/]+") + "$"
		if re.fullmatch(matcher, destination) is None:
			continue
		dynamic_relative = pattern.lstrip("/").replace("{slug}", "[slug]")
		if (pages_root / f"{dynamic_relative}.astro").is_file() or (
			pages_root / dynamic_relative / "index.astro"
		).is_file():
			return True
	return False


def valid_recent_utc_timestamp(value: object) -> bool:
	if not isinstance(value, str) or re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z", value) is None:
		return False
	try:
		captured = datetime.fromisoformat(value.replace("Z", "+00:00"))
	except ValueError:
		return False
	now = datetime.now(timezone.utc)
	return now - timedelta(hours=24) <= captured <= now + timedelta(minutes=5)


def valid_local_clone_url(value: object) -> bool:
	if not isinstance(value, str):
		return False
	try:
		parsed = urlsplit(value)
		hostname = parsed.hostname
		port = parsed.port
	except ValueError:
		return False
	if parsed.scheme not in {"http", "https"} or hostname is None or parsed.username is not None:
		return False
	if port is not None and not 1 <= port <= 65535:
		return False
	if hostname.rstrip(".").casefold() in {"localhost"}:
		return True
	try:
		return ipaddress.ip_address(hostname).is_loopback
	except ValueError:
		return False


def graphql_operations(document: str) -> list[tuple[str, str]] | None:
	"""Return top-level GraphQL operations after ignoring comments and string literals."""
	tokens: list[tuple[str, int]] = []
	depth = 0
	index = 0
	while index < len(document):
		character = document[index]
		if character in " \t\r\n,":
			index += 1
			continue
		if character == "#":
			newline = document.find("\n", index)
			index = len(document) if newline < 0 else newline + 1
			continue
		if document.startswith('"""', index):
			end = document.find('"""', index + 3)
			if end < 0:
				return None
			index = end + 3
			continue
		if character == '"':
			index += 1
			while index < len(document):
				if document[index] == "\\":
					index += 2
					continue
				if document[index] == '"':
					index += 1
					break
				index += 1
			else:
				return None
			continue
		if character == "{":
			tokens.append((character, depth))
			depth += 1
			index += 1
			continue
		if character == "}":
			depth -= 1
			if depth < 0:
				return None
			tokens.append((character, depth))
			index += 1
			continue
		if character.isalpha() or character == "_":
			end = index + 1
			while end < len(document) and (document[end].isalnum() or document[end] == "_"):
				end += 1
			tokens.append((document[index:end], depth))
			index = end
			continue
		index += 1
	if depth != 0:
		return None
	operations: list[tuple[str, str]] = []
	at_definition_start = True
	for token_index, (token, token_depth) in enumerate(tokens):
		if token_depth != 0:
			continue
		if token == "}":
			at_definition_start = True
			continue
		if not at_definition_start:
			continue
		if token == "{":
			operations.append(("query", "anonymous"))
			at_definition_start = False
		elif token in {"query", "mutation", "subscription"}:
			name = ""
			if token_index + 1 < len(tokens):
				next_token, next_depth = tokens[token_index + 1]
				if next_depth == 0 and re.fullmatch(r"[_A-Za-z][_0-9A-Za-z]*", next_token):
					name = next_token
			if not name:
				return None
			operations.append((token, name))
			at_definition_start = False
		elif token == "fragment":
			at_definition_start = False
		else:
			return None
	return operations


def valid_graphql_query_surface(surface: dict[str, Any]) -> bool:
	operation_name = surface.get("operationName")
	document = surface.get("requestDocument")
	document_hash = surface.get("requestDocumentHash")
	if not all(isinstance(value, str) and value.strip() for value in (operation_name, document, document_hash)):
		return False
	operations = graphql_operations(document)
	if operations != [("query", operation_name)]:
		return False
	expected_hash = hashlib.sha256(document.encode("utf-8")).hexdigest()
	return document_hash == expected_hash and surface.get("parameters") == (
		f"operationName={operation_name}; documentSha256={document_hash}"
	)


def decode_json_pointer(root: object, pointer: object) -> object:
	if pointer == "":
		return root
	if not isinstance(pointer, str) or not pointer.startswith("/"):
		return None
	current = root
	for raw_segment in pointer[1:].split("/"):
		segment = raw_segment.replace("~1", "/").replace("~0", "~")
		if isinstance(current, dict):
			if segment not in current:
				return None
			current = current[segment]
		elif isinstance(current, list) and segment.isdigit():
			index = int(segment)
			if index >= len(current):
				return None
			current = current[index]
		else:
			return None
	return current


def contains_identity(value: object, target: object) -> bool:
	if value is target:
		return True
	if isinstance(value, dict):
		return any(contains_identity(child, target) for child in value.values())
	if isinstance(value, list):
		return any(contains_identity(child, target) for child in value)
	return False


def binding_owns_target(
	seed: dict[str, Any],
	owner_kind: object,
	owner_key: object,
	target: object,
) -> bool:
	if not isinstance(owner_key, str):
		return False
	if owner_kind == "settings":
		return target is seed.get("settings") and owner_key == "settings"
	if owner_kind == "collection":
		content = seed.get("content")
		return isinstance(content, dict) and contains_identity(content.get(owner_key), target)
	if owner_kind == "menu":
		menu = find_named(seed.get("menus", []), "name", owner_key)
		return menu is not None and contains_identity(menu.get("items"), target)
	if owner_kind == "section":
		section = find_named(seed.get("sections", []), "slug", owner_key)
		return section is not None and target is section
	if owner_kind == "taxonomy":
		taxonomy = find_named(seed.get("taxonomies", []), "name", owner_key)
		return taxonomy is not None and contains_identity(taxonomy, target)
	return False


def binding_target_value(target: object, mapping_field: dict[str, Any]) -> tuple[bool, object]:
	if not isinstance(target, dict):
		return False, None
	owner_kind = mapping_field.get("ownerKind")
	target_path = mapping_field.get("targetPath")
	storage_slug = mapping_field.get("storageSlug")
	if owner_kind == "collection":
		if isinstance(storage_slug, str) and storage_slug.startswith("system:"):
			return nested_value_with_presence(target, target_path) if isinstance(target_path, str) else (False, None)
		data = target.get("data")
		if not isinstance(data, dict) or not isinstance(storage_slug, str) or storage_slug not in data:
			return False, None
		return True, data[storage_slug]
	if owner_kind == "taxonomy" and isinstance(target_path, str) and target_path.startswith("terms."):
		target_path = target_path.removeprefix("terms.")
	return nested_value_with_presence(target, target_path) if isinstance(target_path, str) else (False, None)


def valid_settings_media_reference(value: object) -> bool:
	if (
		not isinstance(value, dict)
		or set(value) != {"mediaId", "alt"}
		or not isinstance(value.get("mediaId"), str)
		or ULID_PATTERN.fullmatch(value["mediaId"]) is None
		or not isinstance(value.get("alt"), str)
	):
		return False
	return True


def valid_fixed_settings_value(
	target_path: str,
	field_type: object,
	value: object,
	*,
	nullable: bool,
	allowed_private_origins: set[str] | None = None,
) -> bool:
	if not valid_seed_value(
		field_type,
		value,
		nullable=nullable,
		allowed_private_origins=allowed_private_origins,
	):
		return False
	if target_path == "postsPerPage":
		return isinstance(value, int) and not isinstance(value, bool) and 1 <= value <= 100
	if target_path == "seo.titleSeparator":
		return isinstance(value, str) and len(value) <= 10
	if target_path == "seo.robotsTxt":
		return isinstance(value, str) and len(value) <= 5000
	if target_path in {"seo.googleVerification", "seo.bingVerification"}:
		return isinstance(value, str) and len(value) <= 100
	return True


def present_settings_paths(settings: object) -> set[str]:
	if not isinstance(settings, dict):
		return set()
	paths: set[str] = set()
	for key, value in settings.items():
		if key in {"social", "seo"} and isinstance(value, dict):
			for nested_key in value:
				paths.add(f"{key}.{nested_key}")
		else:
			paths.add(str(key))
	return paths


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
			rows.append(cells)
		return rows
	return []


def compact_json(value: object) -> str:
	return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def joined_strings(value: object) -> str:
	return ", ".join(value) if isinstance(value, list) and all(isinstance(item, str) for item in value) else ""


def strip_javascript_comments(source: str) -> str:
	"""Remove line/block comments while preserving string literals used by query-call checks."""
	result: list[str] = []
	index = 0
	quote: str | None = None
	while index < len(source):
		character = source[index]
		if quote is not None:
			result.append(character)
			if character == "\\" and index + 1 < len(source):
				result.append(source[index + 1])
				index += 2
				continue
			if character == quote:
				quote = None
			index += 1
			continue
		if character in {'"', "'", "`"}:
			quote = character
			result.append(character)
			index += 1
			continue
		if source.startswith("//", index):
			newline = source.find("\n", index + 2)
			index = len(source) if newline < 0 else newline
			continue
		if source.startswith("/*", index):
			end = source.find("*/", index + 2)
			index = len(source) if end < 0 else end + 2
			continue
		result.append(character)
		index += 1
	return "".join(result)


def javascript_position_is_code(source: str, position: int) -> bool:
	quote: str | None = None
	index = 0
	while index < position:
		character = source[index]
		if quote is not None:
			if character == "\\" and index + 1 < position:
				index += 2
				continue
			if character == quote:
				quote = None
			index += 1
			continue
		if character in {'"', "'", "`"}:
			quote = character
		index += 1
	return quote is None


def executable_regex_search(pattern: str, source: str) -> re.Match[str] | None:
	return next(
		(match for match in re.finditer(pattern, source) if javascript_position_is_code(source, match.start())),
		None,
	)


def validate_agent_alignment(
	agent_path: Path,
	audit: dict[str, Any],
	mapping: dict[str, Any],
	errors: list[str],
	trusted_explicit_urls: list[str],
) -> set[str]:
	try:
		text = agent_path.read_text(encoding="utf-8")
	except OSError as error:
		errors.append(f"cannot read clone agent {agent_path}: {error}")
		return set()
	if SENSITIVE_DATA_PATTERN.search(text) or PRIVATE_PII_PATTERN.search(text):
		errors.append("clone agent contains sensitive data")
	planned_rows = [
		row
		for row in markdown_table_rows(text, "| Source URL | Scope | Explicit parent | Preserved state |")
		if len(row) == 6
	]
	planned_urls = [row[0] for row in planned_rows]
	planned_explicit_urls = [row[0] for row in planned_rows if row[1].casefold() == "explicit"]
	if planned_explicit_urls != trusted_explicit_urls:
		errors.append("clone agent explicit URL rows differ from caller-trusted explicit URLs")
	allowed_private_origins = set()
	for value in trusted_explicit_urls:
		parsed = urlsplit(value)
		if parsed.hostname is not None and private_hostname_can_be_explicit(parsed.hostname):
			allowed_private_origins.add(url_origin(value))
	audit_urls = [
		page.get("url")
		for page in audit.get("pages", [])
		if isinstance(page, dict) and isinstance(page.get("url"), str)
	]
	if planned_urls != audit_urls:
		errors.append("clone agent URL plan and SOURCE_API_AUDIT.json pages differ")

	agent_surfaces = [
		tuple(row)
		for row in markdown_table_rows(
			text,
			"| Page URL | Surface | Location/endpoint | Transport method |",
		)
		if len(row) == 12
	]
	audit_surfaces = [
		(
			str(page.get("url")),
			str(surface.get("kind")),
			str(surface.get("location")),
			str(surface.get("transportMethod")),
			str(surface.get("operationType")),
			str(surface.get("access")),
			str(surface.get("parameters")),
			str(surface.get("pagination")),
			f"filter={surface.get('filtering')}; sort={surface.get('ordering')}",
			str(surface.get("responseEntity")),
			joined_strings(surface.get("uiConsumers")),
			joined_strings(surface.get("evidence")),
		)
		for page in audit.get("pages", [])
		if isinstance(page, dict)
		for surface in page.get("surfaces", [])
		if isinstance(surface, dict)
	]
	if agent_surfaces != audit_surfaces:
		errors.append("clone agent data surface table and SOURCE_API_AUDIT.json differ")

	agent_documents = [
		tuple(row)
		for row in markdown_table_rows(text, "| Page URL | HTML document surface |")
		if len(row) == 7
	]
	audit_documents = [
		(
			str(page.get("url")),
			str(document.get("surfaceLocation")),
			str(visible_entity.get("responseEntity")),
			joined_strings(visible_entity.get("visibleFieldRefs")),
			joined_strings(visible_entity.get("visibleRecordIds")),
			joined_strings(visible_entity.get("selectors")),
			joined_strings(document.get("evidence")),
		)
		for page in audit.get("pages", [])
		if isinstance(page, dict) and isinstance((document := page.get("document")), dict)
		for visible_entity in document.get("visibleEntities", [])
		if isinstance(visible_entity, dict)
	]
	if agent_documents != audit_documents:
		errors.append("clone agent page content closure table and SOURCE_API_AUDIT.json differ")

	agent_inventory = [
		tuple(row)
		for row in markdown_table_rows(text, "| Source field ref | Source entity |")
		if len(row) == 14
	]
	audit_inventory = [
		(
			str(field.get("ref")),
			str(entity.get("id")),
			str(field.get("path")),
			"/".join(field.get("observedTypes", [])),
			str(field.get("nullable")).casefold(),
			str(field.get("dataClass")),
			compact_json(field.get("observedValues")),
			str(field.get("identifierRole")),
			str(field.get("enumDateSemantics")),
			str(field.get("relationshipCardinality")),
			str(field.get("localeStatus")),
			str(field.get("mediaShape")),
			joined_strings(field.get("uiConsumers")),
			joined_strings(field.get("evidence")),
		)
		for entity in audit.get("entities", [])
		if isinstance(entity, dict)
		for field in entity.get("fields", [])
		if isinstance(field, dict)
	]
	if agent_inventory != audit_inventory:
		errors.append("clone agent source field inventory and SOURCE_API_AUDIT.json differ")

	agent_records = [
		tuple(row)
		for row in markdown_table_rows(text, "| Source entity | Source record ID | Ordered field tuple")
		if len(row) == 5
	]
	audit_record_rows = [
		(
			str(entity.get("id")),
			str(record.get("recordId")),
			compact_json(record.get("values")),
			joined_strings(record.get("uiConsumers")),
			joined_strings(record.get("evidence")),
		)
		for entity in audit.get("entities", [])
		if isinstance(entity, dict)
		for record in entity.get("records", [])
		if isinstance(record, dict)
	]
	if agent_records != audit_record_rows:
		errors.append("clone agent source record inventory and SOURCE_API_AUDIT.json differ")

	agent_entity_mappings = [
		tuple(row)
		for row in markdown_table_rows(text, "| Source entity | Source location/API |")
		if len(row) == 6
	]
	artifact_entity_mappings = [
		(
			str(entity_mapping.get("sourceEntity")),
			str(entity_mapping.get("sourceLocation")),
			str(entity_mapping.get("ownerKind")),
			str(entity_mapping.get("ownerKey")),
			joined_strings(entity_mapping.get("renderConsumers")),
			joined_strings(entity_mapping.get("evidence")),
		)
		for entity_mapping in mapping.get("entityMappings", [])
		if isinstance(entity_mapping, dict)
	]
	if agent_entity_mappings != artifact_entity_mappings:
		errors.append("clone agent entity mapping table and FIELD_MAPPING.json differ")

	agent_mappings = [
		tuple(row)
		for row in markdown_table_rows(text, "| Source field ref/path |")
		if len(row) == 14
	]
	artifact_mappings = [
		(
			str(field.get("sourceRef")),
			str(field.get("ownerKind")),
			str(field.get("ownerKey")),
			str(field.get("targetPath")),
			str(field.get("canonicalName")),
			"N/A" if field.get("storageSlug") is None else str(field.get("storageSlug")),
			str(field.get("type")),
			f"required={str(field.get('required')).casefold()}; nullable={str(field.get('nullable')).casefold()}",
			f"validation={compact_json(field.get('validation'))}; options={compact_json(field.get('options'))}",
			compact_json(field.get("relationship")),
			f"locale={field.get('localeBehavior')}; status={field.get('statusBehavior')}",
			str(field.get("mediaOwnership"))
			+ (f"; source={field.get('mediaSourceUrl')}" if field.get("mediaSourceUrl") is not None else "")
			+ (
				f"; metadata={compact_json(field.get('mediaMetadata'))}"
				if field.get("mediaMetadata") is not None
				else ""
			),
			f"seed={joined_strings(field.get('seedConsumers'))}; render={joined_strings(field.get('renderConsumers'))}",
			joined_strings(field.get("evidence")),
		)
		for field in mapping.get("fields", [])
		if isinstance(field, dict)
	]
	if agent_mappings != artifact_mappings:
		errors.append("clone agent Dineway field mapping table and FIELD_MAPPING.json differ")

	agent_bindings = [
		tuple(row)
		for row in markdown_table_rows(text, "| Source entity | Source record ID | Owner kind |")
		if len(row) == 6
	]
	artifact_bindings = [
		(
			str(binding.get("sourceEntity")),
			str(binding.get("sourceRecordId")),
			str(binding.get("ownerKind")),
			str(binding.get("ownerKey")),
			str(binding.get("targetPointer")),
			joined_strings(binding.get("evidence")),
		)
		for binding in mapping.get("recordBindings", [])
		if isinstance(binding, dict)
	]
	if agent_bindings != artifact_bindings:
		errors.append("clone agent source record binding plan and FIELD_MAPPING.json differ")
	return allowed_private_origins


def validate_evidence_refs(
	values: object,
	label: str,
	root: Path,
	errors: list[str],
	*,
	needle: str | list[str] | None = None,
) -> None:
	if not non_empty_strings(values):
		errors.append(f"{label} evidence must be a non-empty string array")
		return
	root = root.resolve()
	needles = [needle] if isinstance(needle, str) else (needle or [])
	missing_needles = set(needles)
	for raw in values:
		path_text, _, fragment = raw.partition("#")
		path = (root / path_text).resolve()
		if path != root and root not in path.parents:
			errors.append(f"{label} evidence escapes the artifact directory: {raw}")
			continue
		if not path.is_file():
			errors.append(f"{label} evidence file does not exist: {raw}")
			continue
		if path.suffix.casefold() in {".md", ".txt", ".json"}:
			try:
				content = path.read_text(encoding="utf-8")
				for expected in tuple(missing_needles):
					if expected in content:
						missing_needles.remove(expected)
			except (OSError, UnicodeDecodeError):
				pass
			else:
				if fragment and path.suffix.casefold() == ".md":
					anchors: set[str] = set()
					anchor_counts: dict[str, int] = {}
					for heading in re.findall(r"(?m)^#{1,6}\s+(.+?)\s*$", content):
						cleaned = "".join(
							character
							for character in heading.casefold().strip()
							if character in {" ", "-", "_"}
							or unicodedata.category(character).startswith(("L", "N"))
						).replace(" ", "-")
						count = anchor_counts.get(cleaned, 0)
						anchor_counts[cleaned] = count + 1
						anchors.add(cleaned if count == 0 else f"{cleaned}-{count}")
					if fragment not in anchors and f'id="{fragment}"' not in content:
						errors.append(f"{label} evidence anchor does not exist: {raw}")
	for expected in sorted(missing_needles):
		errors.append(f"{label} has no textual evidence containing {expected}")


def validate_site_consumers(
	values: object,
	label: str,
	root: Path,
	errors: list[str],
	*,
	kind: str,
	owner_kind: object = None,
	owner_key: object = None,
	field_tokens: tuple[object, ...] = (),
) -> None:
	if not non_empty_strings(values):
		return
	root = root.resolve()
	for raw in values:
		path_text, separator, fragment = raw.partition("#")
		if path_text.casefold() in {"n/a", "none", "unknown"} or Path(path_text).is_absolute():
			errors.append(f"{label} must reference a concrete site-root file: {raw}")
			continue
		path = (root / path_text).resolve()
		if root not in path.parents or not path.is_file():
			errors.append(f"{label} must reference a concrete site-root file: {raw}")
			continue
		if kind == "render":
			if path.suffix.casefold() not in {".astro", ".tsx", ".ts", ".jsx", ".js"}:
				errors.append(f"{label} render consumer must be executable Astro/React source: {raw}")
				continue
			try:
				content = path.read_text(encoding="utf-8")
			except (OSError, UnicodeDecodeError):
				errors.append(f"{label} render consumer cannot be inspected: {raw}")
				continue
			executable_content = strip_javascript_comments(content)
			content_folded = executable_content.casefold()
			if not isinstance(owner_key, str):
				errors.append(f"{label} render consumer has no owner-specific Dineway read: {raw}")
				continue
			quoted_owner = rf"['\"]{re.escape(owner_key)}['\"]"
			query_patterns = {
				"collection": rf"\bawait\s+getDineway(?:Collection|Entry)\s*\(\s*{quoted_owner}",
				"settings": r"\bawait\s+getSiteSettings\s*\(\s*\)|\bawait\s+getSiteSetting\s*\(",
				"menu": rf"\bawait\s+getMenu\s*\(\s*{quoted_owner}",
				"section": rf"\bawait\s+getSection\s*\(\s*{quoted_owner}",
				"taxonomy": rf"\bawait\s+getTaxonomy(?:Terms|Def)\s*\(\s*{quoted_owner}",
			}
			imported_functions = {
				"collection": ("getDinewayCollection", "getDinewayEntry"),
				"settings": ("getSiteSettings", "getSiteSetting"),
				"menu": ("getMenu",),
				"section": ("getSection",),
				"taxonomy": ("getTaxonomyTerms", "getTaxonomyDef"),
			}
			query_pattern = query_patterns.get(str(owner_kind))
			if query_pattern is None or executable_regex_search(query_pattern, executable_content) is None:
				errors.append(f"{label} render consumer has no owner-specific Dineway read: {raw}")
			functions = imported_functions.get(str(owner_kind), ())
			function_union = "|".join(re.escape(function) for function in functions)
			import_pattern = (
				rf"\bimport\s*\{{[^}}]*\b(?:{function_union})\b[^}}]*\}}\s*from\s*['\"]"
				r"dineway['\"]"
			)
			if not functions or executable_regex_search(import_pattern, executable_content) is None:
				errors.append(f"{label} Dineway query helper is not imported from the Dineway runtime: {raw}")
			if owner_kind == "collection":
				assignment = executable_regex_search(
					rf"\b(?:const|let)\s*\{{(?P<bindings>[^}}]+)\}}\s*=\s*await\s+getDineway(?:Collection|Entry)\s*\(\s*{quoted_owner}",
					executable_content,
				)
				bindings = assignment.group("bindings") if assignment is not None else ""
				cache_set = executable_regex_search(
					r"\bAstro\.cache\.set\s*\(\s*cacheHint\s*\)",
					executable_content,
				)
				binding_names = set(re.findall(r"\b[A-Za-z_$][\w$]*\b", bindings))
				if "cacheHint" not in binding_names or not ({"entries", "entry"} & binding_names) or cache_set is None:
					errors.append(f"{label} collection read must apply its returned cacheHint: {raw}")
			usable_tokens = {
				str(token).rsplit(".", 1)[-1].casefold()
				for token in field_tokens
				if isinstance(token, str) and token.casefold() not in {"n/a", "none"}
			}
			if not usable_tokens or not any(token in content_folded for token in usable_tokens):
				errors.append(f"{label} render consumer does not use the mapped runtime field: {raw}")
		elif kind == "seed":
			if path.suffix.casefold() != ".json" or not separator or not fragment:
				errors.append(f"{label} seed consumer must include a resolvable JSON path fragment: {raw}")
				continue
			try:
				seed_document = json.loads(path.read_text(encoding="utf-8"))
			except (OSError, UnicodeDecodeError, json.JSONDecodeError):
				errors.append(f"{label} seed consumer cannot be inspected: {raw}")
				continue
			resolved = (
				decode_json_pointer(seed_document, fragment)
				if fragment.startswith("/")
				else nested_value(seed_document, fragment)
			)
			if resolved is None:
				errors.append(f"{label} seed consumer fragment does not resolve: {raw}")
				continue
			expected: object = None
			if owner_kind == "collection" and isinstance(owner_key, str):
				expected = nested_value(seed_document, f"content.{owner_key}")
			elif owner_kind == "settings":
				expected = seed_document.get("settings") if isinstance(seed_document, dict) else None
			elif owner_kind == "menu":
				expected = find_named(seed_document.get("menus", []), "name", str(owner_key)) if isinstance(seed_document, dict) else None
			elif owner_kind == "section":
				expected = find_named(seed_document.get("sections", []), "slug", str(owner_key)) if isinstance(seed_document, dict) else None
			elif owner_kind == "taxonomy":
				expected = find_named(seed_document.get("taxonomies", []), "name", str(owner_key)) if isinstance(seed_document, dict) else None
			if expected is None or (resolved != expected and not contains_identity(resolved, expected)):
				errors.append(f"{label} seed consumer fragment does not contain its declared owner: {raw}")


def valid_seed_value(
	field_type: object,
	value: object,
	*,
	nullable: bool,
	cardinality: str = "none",
	allowed_private_origins: set[str] | None = None,
) -> bool:
	if value is None:
		return nullable
	if field_type in {"string", "text", "select", "slug"}:
		return isinstance(value, str)
	if field_type == "url":
		return valid_public_url(value, allowed_private_origins=allowed_private_origins)
	if field_type == "datetime":
		if not isinstance(value, str):
			return False
		date_pattern = r"^\d{4}-\d{2}-\d{2}$"
		datetime_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:\d{2})?$"
		if re.fullmatch(date_pattern, value) is None and re.fullmatch(datetime_pattern, value) is None:
			return False
		try:
			date.fromisoformat(value) if len(value) == 10 else datetime.fromisoformat(value.replace("Z", "+00:00"))
		except ValueError:
			return False
		return True
	if field_type == "reference":
		if cardinality == "many":
			return isinstance(value, list) and bool(value) and all(
				isinstance(item, str) and item.startswith("$ref:") and len(item) > 5 for item in value
			)
		return isinstance(value, str) and value.startswith("$ref:") and len(value) > 5
	if field_type == "number":
		return isinstance(value, (int, float)) and not isinstance(value, bool)
	if field_type == "integer":
		return isinstance(value, int) and not isinstance(value, bool)
	if field_type == "boolean":
		return isinstance(value, bool)
	if field_type == "multiSelect":
		return isinstance(value, list) and all(isinstance(item, str) for item in value)
	if field_type == "portableText":
		return isinstance(value, list) and all(
			isinstance(item, dict) and isinstance(item.get("_type"), str) and bool(item["_type"].strip())
			for item in value
		)
	if field_type == "repeater":
		return isinstance(value, list) and all(isinstance(item, dict) for item in value)
	if field_type == "json":
		return isinstance(value, (dict, list))
	if field_type in {"image", "file"}:
		if not isinstance(value, dict):
			return False
		media = value.get("$media")
		return (
			set(value) == {"$media"}
			and isinstance(media, dict)
			and "url" in media
			and set(media).issubset({"url", *MEDIA_METADATA_SOURCE_KEYS})
			and all(isinstance(media.get(key), str) for key in set(media) - {"url"})
			and valid_public_url(media.get("url"), allowed_private_origins=allowed_private_origins)
		)
	return False


def valid_validation_definition(field_type: object, validation: object) -> bool:
	if not isinstance(validation, dict):
		return False
	allowed_keys = {
		"required",
		"min",
		"max",
		"minLength",
		"maxLength",
		"pattern",
		"options",
		"subFields",
		"minItems",
		"maxItems",
		"allowedMimeTypes",
	}
	if set(validation) - allowed_keys:
		return False
	for key in ("min", "max"):
		if key in validation and (
			not isinstance(validation[key], (int, float))
			or isinstance(validation[key], bool)
			or not math.isfinite(validation[key])
		):
			return False
	for key in ("minLength", "maxLength", "minItems", "maxItems"):
		if key in validation and (
			not isinstance(validation[key], int)
			or isinstance(validation[key], bool)
			or validation[key] < 0
			or (key == "maxItems" and validation[key] == 0)
		):
			return False
	for minimum, maximum in (("min", "max"), ("minLength", "maxLength"), ("minItems", "maxItems")):
		if minimum in validation and maximum in validation and validation[minimum] > validation[maximum]:
			return False
	if "required" in validation and not isinstance(validation["required"], bool):
		return False
	type_keys = {
		"min": {"number", "integer"},
		"max": {"number", "integer"},
		"minLength": {"string", "text", "url", "slug"},
		"maxLength": {"string", "text", "url", "slug"},
		"pattern": {"string", "text", "url", "slug"},
		"options": {"select", "multiSelect"},
		"subFields": {"repeater"},
		"minItems": {"repeater"},
		"maxItems": {"repeater"},
		"allowedMimeTypes": {"image", "file"},
	}
	for key, supported_types in type_keys.items():
		if key in validation and field_type not in supported_types:
			return False
	if field_type in {"select", "multiSelect"}:
		options = validation.get("options")
		if not non_empty_strings(options) or len(options) != len(set(options)):
			return False
	sub_fields = validation.get("subFields")
	if sub_fields is not None:
		if not isinstance(sub_fields, list) or not sub_fields:
			return False
		for sub_field in sub_fields:
			if not isinstance(sub_field, dict) or set(sub_field) - {
				"slug",
				"type",
				"label",
				"required",
				"options",
			}:
				return False
			if (
				not isinstance(sub_field.get("slug"), str)
				or len(sub_field["slug"]) > 63
				or STORAGE_SLUG_PATTERN.fullmatch(sub_field["slug"]) is None
				or sub_field.get("type") not in REPEATER_SUBFIELD_TYPES
				or not isinstance(sub_field.get("label"), str)
				or not sub_field["label"].strip()
			):
				return False
			if "required" in sub_field and not isinstance(sub_field["required"], bool):
				return False
			if "options" in sub_field and (
				not isinstance(sub_field["options"], list)
				or any(not isinstance(option, str) for option in sub_field["options"])
			):
				return False
	allowed_mime_types = validation.get("allowedMimeTypes")
	if allowed_mime_types is not None and (
		not isinstance(allowed_mime_types, list)
		or not 1 <= len(allowed_mime_types) <= 64
		or any(not isinstance(value, str) or MIME_TYPE_PATTERN.fullmatch(value) is None for value in allowed_mime_types)
	):
		return False
	pattern = validation.get("pattern")
	if pattern is not None:
		if not isinstance(pattern, str) or not pattern:
			return False
		# Fail closed to the portable Python/ECMAScript subset. Dineway executes this with `new RegExp()`.
		if re.search(r"\(\?P[<=]|\(\?[aiLmsux-]+\)", pattern):
			return False
		try:
			re.compile(pattern)
		except re.error:
			return False
	return True


def valid_field_constraints(field_type: object, value: object, validation: object) -> bool:
	if value is None:
		return True
	if not valid_validation_definition(field_type, validation):
		return False
	if field_type in {"select", "multiSelect"}:
		options = validation.get("options")
		if not non_empty_strings(options):
			return False
		values = value if isinstance(value, list) else [value]
		if any(item not in options for item in values):
			return False
	if isinstance(value, (int, float)) and not isinstance(value, bool):
		if isinstance(validation.get("min"), (int, float)) and value < validation["min"]:
			return False
		if isinstance(validation.get("max"), (int, float)) and value > validation["max"]:
			return False
	if isinstance(value, str):
		if isinstance(validation.get("minLength"), int) and len(value) < validation["minLength"]:
			return False
		if isinstance(validation.get("maxLength"), int) and len(value) > validation["maxLength"]:
			return False
		if isinstance(validation.get("pattern"), str):
			try:
				if re.search(validation["pattern"], value) is None:
					return False
			except re.error:
				return False
	if isinstance(value, list):
		if isinstance(validation.get("minItems"), int) and len(value) < validation["minItems"]:
			return False
		if isinstance(validation.get("maxItems"), int) and len(value) > validation["maxItems"]:
			return False
	if field_type == "repeater":
		sub_fields = validation.get("subFields")
		if not isinstance(sub_fields, list) or not isinstance(value, list):
			return False
		sub_fields_by_slug = {
			sub_field.get("slug"): sub_field
			for sub_field in sub_fields
			if isinstance(sub_field, dict) and isinstance(sub_field.get("slug"), str)
		}
		if len(sub_fields_by_slug) != len(sub_fields):
			return False
		for item in value:
			if not isinstance(item, dict) or set(item) != set(sub_fields_by_slug):
				return False
			for slug, sub_field in sub_fields_by_slug.items():
				sub_value = item.get(slug)
				required = bool(sub_field.get("required", False))
				if required and sub_value is None:
					return False
				sub_type = sub_field.get("type")
				if not valid_seed_value(sub_type, sub_value, nullable=not required):
					return False
				if sub_type in {"select", "multiSelect"} and not valid_field_constraints(
					sub_type,
					sub_value,
					{"options": sub_field.get("options", [])},
				):
					return False
	return True


def comparable_value(field_type: object, value: object) -> str:
	if field_type in {"image", "file"} and isinstance(value, dict) and isinstance(value.get("$media"), dict):
		value = value["$media"].get("url")
	if field_type == "reference":
		if isinstance(value, str) and value.startswith("$ref:"):
			value = value[5:]
		elif isinstance(value, list):
			value = [item[5:] if isinstance(item, str) and item.startswith("$ref:") else item for item in value]
	return json.dumps(value, sort_keys=True, ensure_ascii=False)


def source_values_missing(audit_field: dict[str, Any] | None, field_type: object, seed_values: list[object]) -> list[object]:
	if audit_field is None:
		return []
	observed_values = audit_field.get("observedValues")
	if not isinstance(observed_values, list):
		return []
	seed_set = {comparable_value(field_type, value) for value in seed_values}
	return [value for value in observed_values if comparable_value(field_type, value) not in seed_set]


def validate_observed_value_closure(
	errors: list[str],
	source_ref: str,
	audit_field: dict[str, Any] | None,
	field_type: object,
	seed_values: list[object],
) -> None:
	missing = source_values_missing(audit_field, field_type, seed_values)
	if missing:
		errors.append(f"mapping {source_ref} has public source values absent from seed: {missing!r}")


def validate_seed_media_metadata(
	errors: list[str],
	source_ref: str,
	mapping_field: dict[str, Any],
	audit_fields: dict[str, dict[str, Any]],
	values: list[object],
) -> None:
	config = mapping_field.get("mediaMetadata")
	config = config if isinstance(config, dict) else {}
	expected_keys = {
		media_key
		for media_key, config_key in MEDIA_METADATA_SOURCE_KEYS.items()
		if isinstance(config.get(config_key), str)
	}
	metadata_values: dict[str, list[object]] = {key: [] for key in expected_keys}
	for value in values:
		media = value.get("$media") if isinstance(value, dict) and isinstance(value.get("$media"), dict) else value
		if not isinstance(media, dict):
			continue
		actual_keys = {
			key
			for key in MEDIA_METADATA_SOURCE_KEYS
			if key in media and (key in expected_keys or (media[key] is not None and media[key] != ""))
		}
		if actual_keys != expected_keys:
			errors.append(
				f"mapping {source_ref} seed media metadata does not match source-backed mediaMetadata refs",
			)
		for key in expected_keys:
			if key in media:
				metadata_values[key].append(media[key])
	for media_key, config_key in MEDIA_METADATA_SOURCE_KEYS.items():
		metadata_ref = config.get(config_key)
		if not isinstance(metadata_ref, str):
			continue
		validate_observed_value_closure(
			errors,
			f"{source_ref}.{media_key}",
			audit_fields.get(metadata_ref),
			"string",
			metadata_values.get(media_key, []),
		)


def validate_settings_media_proofs(
	proof_artifact: dict[str, Any],
	mappings_by_ref: dict[str, dict[str, Any]],
	seed: dict[str, Any],
	errors: list[str],
	*,
	allowed_private_origins: set[str] | None = None,
	root: Path,
) -> None:
	expected = {
		(source_ref, str(field.get("targetPath"))): field
		for source_ref, field in mappings_by_ref.items()
		if field.get("ownerKind") == "settings"
		and field.get("targetPath") in {"logo", "favicon", "seo.defaultOgImage"}
	}
	proofs = proof_artifact.get("proofs")
	if not isinstance(proofs, list):
		errors.append("settings media proof proofs must be an array")
		return
	proofs_by_key: dict[tuple[str, str], dict[str, Any]] = {}
	for index, proof in enumerate(proofs):
		if not isinstance(proof, dict):
			errors.append(f"settings media proof {index} must be an object")
			continue
		allowed_keys = {
			"sourceRef",
			"targetPath",
			"sourceUrl",
			"sourceSnapshot",
			"mediaId",
			"capturedAt",
			"sourceFetch",
			"mediaGet",
			"settingsGet",
		}
		if set(proof) != allowed_keys:
			errors.append(f"settings media proof {index} has missing or unexpected fields")
		key = (str(proof.get("sourceRef", "")), str(proof.get("targetPath", "")))
		if key in proofs_by_key:
			errors.append(f"duplicate settings media proof: {key}")
			continue
		proofs_by_key[key] = proof

	missing = sorted(set(expected) - set(proofs_by_key))
	extra = sorted(set(proofs_by_key) - set(expected))
	if missing:
		errors.append(f"settings media mappings without runtime proof: {missing!r}")
	if extra:
		errors.append(f"settings media proofs without mappings: {extra!r}")

	for key in sorted(set(expected) & set(proofs_by_key)):
		field = expected[key]
		proof = proofs_by_key[key]
		label = f"settings media proof {key}"
		media_id = proof.get("mediaId")
		source_url = proof.get("sourceUrl")
		seed_media = nested_value(seed.get("settings", {}), key[1])
		if media_id != nested_value(seed.get("settings", {}), key[1] + ".mediaId"):
			errors.append(f"{label} mediaId does not match seed settings")
		if media_id is None or ULID_PATTERN.fullmatch(str(media_id)) is None:
			errors.append(f"{label} mediaId must be a ULID")
		if source_url != field.get("mediaSourceUrl") or not valid_public_url(
			source_url,
			allowed_private_origins=allowed_private_origins,
		):
			errors.append(f"{label} sourceUrl does not match the sanitized mapping source")
		if not valid_recent_utc_timestamp(proof.get("capturedAt")):
			errors.append(f"{label} capturedAt must be a fresh RFC 3339 UTC timestamp")
		has_alt_source = isinstance(
			(field.get("mediaMetadata") if isinstance(field.get("mediaMetadata"), dict) else {}).get("altSourceRef"),
			str,
		)
		if not isinstance(seed_media, dict) or (not has_alt_source and seed_media.get("alt") != ""):
			errors.append(f"{label} alt must be empty unless a separate source-backed alt mapping exists")

		source_snapshot = proof.get("sourceSnapshot")
		source_fetch = proof.get("sourceFetch")
		snapshot_bytes: bytes | None = None
		if not isinstance(source_snapshot, str) or not source_snapshot.strip() or Path(source_snapshot).is_absolute():
			errors.append(f"{label} sourceSnapshot must be a site-root-relative file")
		else:
			snapshot_path = (root.resolve() / source_snapshot).resolve()
			if root.resolve() not in snapshot_path.parents or not snapshot_path.is_file():
				errors.append(f"{label} sourceSnapshot is outside the site root or missing")
			else:
				try:
					snapshot_bytes = snapshot_path.read_bytes()
				except OSError:
					errors.append(f"{label} sourceSnapshot cannot be read")
		if not isinstance(source_fetch, dict) or set(source_fetch) != {
			"requestedUrl",
			"finalUrl",
			"status",
			"mimeType",
			"byteLength",
			"contentHash",
			"capturedAt",
		}:
			errors.append(f"{label} sourceFetch has missing or unexpected fields")
			source_fetch = {}
		if (
			source_fetch.get("requestedUrl") != source_url
			or not valid_public_url(
				source_fetch.get("finalUrl"),
				allowed_private_origins=allowed_private_origins,
			)
			or source_fetch.get("status") != 200
			or not isinstance(source_fetch.get("mimeType"), str)
			or not source_fetch["mimeType"].casefold().startswith("image/")
			or not isinstance(source_fetch.get("byteLength"), int)
			or isinstance(source_fetch.get("byteLength"), bool)
			or source_fetch["byteLength"] <= 0
			or not isinstance(source_fetch.get("contentHash"), str)
			or CONTENT_HASH_PATTERN.fullmatch(source_fetch["contentHash"]) is None
			or not valid_recent_utc_timestamp(source_fetch.get("capturedAt"))
		):
			errors.append(f"{label} sourceFetch is not a fresh successful anonymous image fetch")
		if snapshot_bytes is not None:
			snapshot_hash = "sha1:" + hashlib.sha1(snapshot_bytes).hexdigest()
			if (
				source_fetch.get("byteLength") != len(snapshot_bytes)
				or source_fetch.get("contentHash") != snapshot_hash
			):
				errors.append(f"{label} source snapshot content does not match sourceFetch")

		media_get = proof.get("mediaGet")
		settings_get = proof.get("settingsGet")
		if not isinstance(media_get, dict) or set(media_get) != {"status", "item"}:
			errors.append(f"{label} mediaGet must contain only status and item")
			continue
		item = media_get.get("item")
		item_keys = {"id", "status", "mimeType", "storageKey", "url", "contentHash"}
		if media_get.get("status") != 200 or not isinstance(item, dict) or set(item) != item_keys:
			errors.append(f"{label} mediaGet is not a successful normalized media response")
			continue
		if (
			item.get("id") != media_id
			or item.get("status") != "ready"
			or not isinstance(item.get("mimeType"), str)
			or not item["mimeType"].casefold().startswith("image/")
			or not isinstance(item.get("storageKey"), str)
			or not item["storageKey"].strip()
			or not isinstance(item.get("contentHash"), str)
			or CONTENT_HASH_PATTERN.fullmatch(item["contentHash"]) is None
			or not valid_runtime_media_url(item.get("url"), allowed_private_origins=allowed_private_origins)
		):
			errors.append(f"{label} mediaGet item is not a ready, content-addressed image")
		if isinstance(source_fetch, dict) and item.get("contentHash") != source_fetch.get("contentHash"):
			errors.append(f"{label} imported media does not match source snapshot content")
		if not isinstance(settings_get, dict) or set(settings_get) != {"status", "mediaId", "resolvedUrl", "alt"}:
			errors.append(f"{label} settingsGet has missing or unexpected fields")
		elif (
			settings_get.get("status") != 200
			or settings_get.get("mediaId") != media_id
			or settings_get.get("resolvedUrl") != item.get("url")
			or not isinstance(seed_media, dict)
			or settings_get.get("alt") != seed_media.get("alt")
			or not valid_runtime_media_url(
				settings_get.get("resolvedUrl"),
				allowed_private_origins=allowed_private_origins,
			)
		):
			errors.append(f"{label} settingsGet does not resolve the imported media")


def validate_document_snapshot(
	snapshot: dict[str, Any],
	document_closures: list[tuple[str, dict[str, Any]]],
	audit_fields: dict[str, dict[str, Any]],
	audit_records: dict[tuple[str, str], dict[str, Any]],
	errors: list[str],
) -> None:
	pages = snapshot.get("pages")
	if not isinstance(pages, list) or not pages:
		errors.append("source document snapshot pages must be a non-empty array")
		return
	expected_pages = [url for url, _ in document_closures]
	actual_pages = [page.get("url") for page in pages if isinstance(page, dict)]
	if actual_pages != expected_pages:
		errors.append("source document snapshot pages differ from audited page order")
	for page_index, page in enumerate(pages):
		label = f"source document snapshot page {page_index}"
		if not isinstance(page, dict) or set(page) != {"url", "capturedAt", "items"}:
			errors.append(f"{label} has missing or unexpected fields")
			continue
		if not valid_recent_utc_timestamp(page.get("capturedAt")):
			errors.append(f"{label} capturedAt must be a fresh RFC 3339 UTC timestamp")
		items = page.get("items")
		if not isinstance(items, list) or not items:
			errors.append(f"{label} must contain browser-captured visible items")
			continue
		seen_item_ids: set[str] = set()
		actual_by_entity: dict[str, dict[str, set[str]]] = {}
		for item_index, item in enumerate(items):
			item_label = f"{label} item {item_index}"
			expected_keys = {
				"itemId",
				"kind",
				"selector",
				"sourceEntity",
				"sourceRef",
				"sourceRecordId",
				"value",
			}
			if not isinstance(item, dict) or set(item) != expected_keys:
				errors.append(f"{item_label} has missing or unexpected fields")
				continue
			for key in ("itemId", "kind", "selector", "sourceEntity", "sourceRef", "sourceRecordId"):
				if not isinstance(item.get(key), str) or not item[key].strip():
					errors.append(f"{item_label} has no {key}")
			item_id = str(item.get("itemId", ""))
			if item_id in seen_item_ids:
				errors.append(f"{label} has duplicate itemId: {item_id}")
			seen_item_ids.add(item_id)
			if item.get("kind") not in {"visible-text", "media", "link", "repeat-item"}:
				errors.append(f"{item_label} uses an unsupported visible item kind")
			source_entity = str(item.get("sourceEntity", ""))
			source_ref = str(item.get("sourceRef", ""))
			record_id = str(item.get("sourceRecordId", ""))
			field = audit_fields.get(source_ref)
			record = audit_records.get((source_entity, record_id))
			if field is None or field.get("_entityId") != source_entity:
				errors.append(f"{item_label} sourceRef is absent from its audited entity")
			elif (field.get("dataClass") == "public-media") != (item.get("kind") == "media"):
				errors.append(f"{item_label} browser media and public-media classification must match")
			if not isinstance(record, dict) or not isinstance(record.get("values"), dict):
				errors.append(f"{item_label} sourceRecordId is absent from its audited entity")
			elif source_ref not in record["values"] or record["values"][source_ref] != item.get("value"):
				errors.append(f"{item_label} value differs from the audited source record")
			group = actual_by_entity.setdefault(
				source_entity,
				{"fields": set(), "records": set(), "selectors": set()},
			)
			group["fields"].add(source_ref)
			group["records"].add(record_id)
			group["selectors"].add(str(item.get("selector", "")))
		if page_index >= len(document_closures):
			continue
		page_url, document = document_closures[page_index]
		if page.get("url") != page_url:
			continue
		expected_by_entity: dict[str, dict[str, set[str]]] = {}
		for visible_entity in document.get("visibleEntities", []):
			if not isinstance(visible_entity, dict):
				continue
			entity_id = str(visible_entity.get("responseEntity", ""))
			expected_by_entity[entity_id] = {
				"fields": set(visible_entity.get("visibleFieldRefs", [])),
				"records": set(visible_entity.get("visibleRecordIds", [])),
				"selectors": set(visible_entity.get("selectors", [])),
			}
		if actual_by_entity != expected_by_entity:
			errors.append(f"{label} browser items do not exactly close the audited visible entities")


def successful_status(value: object) -> bool:
	return isinstance(value, int) and not isinstance(value, bool) and 200 <= value < 300


def validate_runtime_content_proof(
	proof_document: dict[str, Any],
	mappings_by_ref: dict[str, dict[str, Any]],
	document_snapshot: dict[str, Any],
	audit_fields: dict[str, dict[str, Any]],
	audit_records: dict[tuple[str, str], dict[str, Any]],
	clone_url: str,
	root: Path,
	errors: list[str],
) -> None:
	proofs = proof_document.get("proofs")
	if not isinstance(proofs, list) or not proofs:
		errors.append("runtime content proof must contain one or more proofs")
		return
	snapshot_items: dict[tuple[str, str, str, str, str, str], dict[str, Any]] = {}
	for page in document_snapshot.get("pages", []):
		if not isinstance(page, dict):
			continue
		for item in page.get("items", []):
			if not isinstance(item, dict):
				continue
			item_key = (
				str(page.get("url", "")),
				str(item.get("itemId", "")),
				str(item.get("sourceEntity", "")),
				str(item.get("sourceRecordId", "")),
				str(item.get("sourceRef", "")),
				str(item.get("selector", "")),
			)
			snapshot_items[item_key] = item
	expected_keys = {
		(*item_key, render_consumer)
		for item_key in snapshot_items
		for mapping in [mappings_by_ref.get(item_key[4], {})]
		for render_consumer in mapping.get("renderConsumers", [])
		if isinstance(render_consumer, str)
	}
	proofs_by_key: dict[tuple[str, str, str, str, str, str, str], dict[str, Any]] = {}
	for index, proof in enumerate(proofs):
		label = f"runtime content proof {index}"
		expected_fields = {
			"pageUrl",
			"snapshotItemId",
			"sourceEntity",
			"sourceRecordId",
			"sourceRef",
			"sourceValue",
			"ownerKind",
			"ownerKey",
			"runtimeReadPath",
			"renderConsumer",
			"selector",
			"cloneUrl",
			"capturedAt",
			"mediaProof",
			"before",
			"sentinel",
			"restore",
		}
		if not isinstance(proof, dict) or set(proof) != expected_fields:
			errors.append(f"{label} has missing or unexpected fields")
			continue
		key = (
			str(proof.get("pageUrl", "")),
			str(proof.get("snapshotItemId", "")),
			str(proof.get("sourceEntity", "")),
			str(proof.get("sourceRecordId", "")),
			str(proof.get("sourceRef", "")),
			str(proof.get("selector", "")),
			str(proof.get("renderConsumer", "")),
		)
		if key in proofs_by_key:
			errors.append(f"duplicate runtime content proof: {key}")
			continue
		proofs_by_key[key] = proof
		mapping = mappings_by_ref.get(key[4])
		if mapping is None:
			errors.append(f"{label} has no mapped source field")
		else:
			for proof_key, mapping_key in (
				("ownerKind", "ownerKind"),
				("ownerKey", "ownerKey"),
				("runtimeReadPath", "runtimeReadPath"),
			):
				if proof.get(proof_key) != mapping.get(mapping_key):
					errors.append(f"{label} {proof_key} differs from the field mapping")
		snapshot_item = snapshot_items.get(key[:6])
		if snapshot_item is None:
			errors.append(f"{label} does not identify a browser snapshot occurrence")
		record = audit_records.get((key[2], key[3]))
		source_value = record.get("values", {}).get(key[4]) if isinstance(record, dict) else None
		if (
			not isinstance(record, dict)
			or key[4] not in record.get("values", {})
			or proof.get("sourceValue") != source_value
			or (isinstance(snapshot_item, dict) and snapshot_item.get("value") != source_value)
		):
			errors.append(f"{label} sourceValue differs from its audited source record occurrence")
		if proof.get("cloneUrl") != clone_url or not valid_local_clone_url(proof.get("cloneUrl")):
			errors.append(f"{label} must target the caller-trusted local clone URL")
		if not valid_recent_utc_timestamp(proof.get("capturedAt")):
			errors.append(f"{label} capturedAt must be a fresh RFC 3339 UTC timestamp")
		audit_field = audit_fields.get(key[4])
		is_media = isinstance(audit_field, dict) and audit_field.get("dataClass") == "public-media"
		media_proof = proof.get("mediaProof")
		if not is_media and media_proof is not None:
			errors.append(f"{label} non-media field must not contain mediaProof")
		if is_media:
			if not isinstance(media_proof, dict) or set(media_proof) != {
				"sourceSnapshot",
				"sourceContentHash",
				"before",
				"sentinel",
				"restore",
			}:
				errors.append(f"{label} mediaProof has missing or unexpected fields")
			else:
				source_snapshot = media_proof.get("sourceSnapshot")
				source_hash = media_proof.get("sourceContentHash")
				snapshot_bytes: bytes | None = None
				if (
					not isinstance(source_snapshot, str)
					or not source_snapshot.strip()
					or Path(source_snapshot).is_absolute()
				):
					errors.append(f"{label} media sourceSnapshot must be a site-root-relative file")
				else:
					snapshot_path = (root.resolve() / source_snapshot).resolve()
					if root.resolve() not in snapshot_path.parents or not snapshot_path.is_file():
						errors.append(f"{label} media sourceSnapshot is outside the site root or missing")
					else:
						try:
							snapshot_bytes = snapshot_path.read_bytes()
						except OSError:
							errors.append(f"{label} media sourceSnapshot cannot be read")
				if (
					not isinstance(source_hash, str)
					or CONTENT_HASH_PATTERN.fullmatch(source_hash) is None
				):
					errors.append(f"{label} media sourceContentHash must be a Dineway SHA-1 content hash")
				if snapshot_bytes is not None:
					computed_hash = "sha1:" + hashlib.sha1(snapshot_bytes).hexdigest()
					if source_hash != computed_hash:
						errors.append(f"{label} media source content hash differs from the source snapshot")

				media_states: dict[str, dict[str, Any]] = {}
				try:
					clone_origin = url_origin(clone_url)
				except ValueError:
					clone_origin = ""
				for state_name in ("before", "sentinel", "restore"):
					state = media_proof.get(state_name)
					state_label = f"{label} media {state_name}"
					if not isinstance(state, dict) or set(state) != {
						"mediaId",
						"resolvedUrl",
						"contentHash",
						"mimeType",
					}:
						errors.append(f"{state_label} has missing or unexpected fields")
						continue
					media_states[state_name] = state
					resolved_url = state.get("resolvedUrl")
					valid_resolved_url = valid_runtime_media_url(
						resolved_url,
						allowed_private_origins={clone_origin} if clone_origin else set(),
					)
					mime_type = state.get("mimeType")
					if (
						ULID_PATTERN.fullmatch(str(state.get("mediaId", ""))) is None
						or not valid_resolved_url
						or not isinstance(state.get("contentHash"), str)
						or CONTENT_HASH_PATTERN.fullmatch(state["contentHash"]) is None
						or not isinstance(mime_type, str)
						or not mime_type.strip()
						or (mapping is not None and mapping.get("type") == "image" and not mime_type.casefold().startswith("image/"))
					):
						errors.append(f"{state_label} is not a normalized ready Dineway media state")
				before_media = media_states.get("before")
				sentinel_media = media_states.get("sentinel")
				restore_media = media_states.get("restore")
				if before_media is not None and source_hash != before_media.get("contentHash"):
					errors.append(f"{label} media before content hash differs from the source content hash")
				if restore_media is not None and source_hash != restore_media.get("contentHash"):
					errors.append(f"{label} media restore content hash differs from the source content hash")
				if before_media is not None and restore_media is not None and restore_media != before_media:
					errors.append(f"{label} media restore did not return the original Dineway media state")
				if before_media is not None and sentinel_media is not None and (
					sentinel_media.get("mediaId") == before_media.get("mediaId")
					or sentinel_media.get("contentHash") == before_media.get("contentHash")
				):
					errors.append(f"{label} media sentinel must use a distinct Dineway media item")

		before = proof.get("before")
		sentinel = proof.get("sentinel")
		restore = proof.get("restore")
		if not isinstance(before, dict) or set(before) != {"liveReadStatus", "ssrStatus", "observedValue"}:
			errors.append(f"{label} before step has missing or unexpected fields")
			continue
		if not isinstance(sentinel, dict) or set(sentinel) != {
			"value",
			"writeStatus",
			"liveReadStatus",
			"ssrStatus",
			"observedValue",
		}:
			errors.append(f"{label} sentinel step has missing or unexpected fields")
			continue
		if not isinstance(restore, dict) or set(restore) != {
			"writeStatus",
			"liveReadStatus",
			"ssrStatus",
			"observedValue",
		}:
			errors.append(f"{label} restore step has missing or unexpected fields")
			continue
		if not all(
			successful_status(status)
			for status in (
				before.get("liveReadStatus"),
				before.get("ssrStatus"),
				sentinel.get("writeStatus"),
				sentinel.get("liveReadStatus"),
				sentinel.get("ssrStatus"),
				restore.get("writeStatus"),
				restore.get("liveReadStatus"),
				restore.get("ssrStatus"),
			)
		):
			errors.append(f"{label} contains a failed live read/write/SSR step")
		if sentinel.get("value") == before.get("observedValue"):
			errors.append(f"{label} sentinel must differ from the original rendered value")
		if sentinel.get("observedValue") != sentinel.get("value"):
			errors.append(f"{label} SSR selector did not render the sentinel value")
		if restore.get("observedValue") != before.get("observedValue"):
			errors.append(f"{label} restore did not return the source-faithful rendered value")
		if is_media and isinstance(media_proof, dict):
			before_media = media_proof.get("before")
			sentinel_media = media_proof.get("sentinel")
			restore_media = media_proof.get("restore")
			if isinstance(before_media, dict) and before.get("observedValue") != before_media.get("resolvedUrl"):
				errors.append(f"{label} original SSR media URL differs from the live Dineway media state")
			if isinstance(sentinel_media, dict) and sentinel.get("value") != sentinel_media.get("resolvedUrl"):
				errors.append(f"{label} sentinel SSR media URL differs from the live Dineway media state")
			if isinstance(restore_media, dict) and restore.get("observedValue") != restore_media.get("resolvedUrl"):
				errors.append(f"{label} restored SSR media URL differs from the live Dineway media state")
		if (
			isinstance(audit_field, dict)
			and not is_media
			and before.get("observedValue") != source_value
		):
			errors.append(f"{label} original SSR value differs from the audited source record")
	missing = sorted(expected_keys - set(proofs_by_key))
	extra = sorted(set(proofs_by_key) - expected_keys)
	if missing:
		errors.append(f"mapped runtime consumers without reversible live proofs: {missing!r}")
	if extra:
		errors.append(f"runtime content proofs without mapped consumers/selectors: {extra!r}")


def validate_artifacts(
	audit_path: Path,
	document_snapshot_path: Path,
	mapping_path: Path,
	seed_path: Path,
	settings_media_proof_path: Path,
	runtime_content_proof_path: Path | None,
	agent_path: Path,
	site_root: Path,
	trusted_explicit_urls: list[str],
	clone_url: str | None,
	phase: str = "completion",
) -> list[str]:
	errors: list[str] = []
	artifact_root = site_root.resolve()
	if artifact_root in {Path("/"), Path.home().resolve()}:
		return ["site root must be the exact Dineway Site directory, not a filesystem or home root"]
	artifact_paths = [
		audit_path,
		document_snapshot_path,
		mapping_path,
		seed_path,
		settings_media_proof_path,
		agent_path,
	]
	if runtime_content_proof_path is not None:
		artifact_paths.append(runtime_content_proof_path)
	for path in artifact_paths:
		resolved_path = path.resolve()
		if resolved_path != artifact_root and artifact_root not in resolved_path.parents:
			errors.append(f"artifact is outside the approved site root: {path}")
	if errors:
		return errors
	audit_root = artifact_root
	mapping_root = artifact_root
	audit, _ = load_json(audit_path, "source audit", errors)
	document_snapshot, _ = load_json(document_snapshot_path, "source document snapshot", errors)
	mapping, _ = load_json(mapping_path, "field mapping", errors)
	seed, _ = load_json(seed_path, "seed", errors)
	settings_media_proof, _ = load_json(settings_media_proof_path, "settings media proof", errors)
	runtime_content_proof: dict[str, Any] = {}
	if runtime_content_proof_path is not None:
		runtime_content_proof, _ = load_json(runtime_content_proof_path, "runtime content proof", errors)
	if errors:
		return errors

	if audit.get("version") != "1":
		errors.append('source audit version must be "1"')
	if document_snapshot.get("version") != "1":
		errors.append('source document snapshot version must be "1"')
	if mapping.get("version") != "1":
		errors.append('field mapping version must be "1"')
	if seed.get("version") != "1":
		errors.append('seed version must be "1"')
	if settings_media_proof.get("version") != "1":
		errors.append('settings media proof version must be "1"')
	if phase not in {"foundation", "completion"}:
		errors.append("validation phase must be foundation or completion")
	if phase == "completion":
		if runtime_content_proof_path is None or runtime_content_proof.get("version") != "1":
			errors.append('completion phase requires runtime content proof version "1"')
		if not valid_local_clone_url(clone_url):
			errors.append("completion phase clone URL must be an explicit localhost or loopback Dineway dev-server URL")
	if not trusted_explicit_urls:
		return ["at least one caller-trusted explicit URL is required"]
	allowed_private_origins = validate_agent_alignment(
		agent_path,
		audit,
		mapping,
		errors,
		trusted_explicit_urls,
	)
	try:
		agent_text = agent_path.read_text(encoding="utf-8")
	except OSError:
		agent_text = ""
	planned_destination_routes = {
		row[4]
		for row in markdown_table_rows(agent_text, "| Source URL | Scope | Explicit parent | Preserved state |")
		if len(row) == 6 and row[5].casefold() == "include"
	}

	surface_entities: list[tuple[str, str, str]] = []
	surface_locations: set[str] = set()
	document_closures: list[tuple[str, dict[str, Any]]] = []
	pages = audit.get("pages")
	if not isinstance(pages, list) or not pages:
		errors.append("source audit pages must be a non-empty array")
	else:
		seen_pages: set[str] = set()
		for index, page in enumerate(pages):
			if not isinstance(page, dict):
				errors.append(f"source audit page {index} must be an object")
				continue
			url = page.get("url")
			if not valid_public_url(url, allowed_private_origins=allowed_private_origins):
				errors.append(f"source audit page {index} has no public HTTP(S) URL")
			elif url in seen_pages:
				errors.append(f"duplicate source audit page URL: {url}")
			else:
				seen_pages.add(url)
			surfaces = page.get("surfaces")
			if not isinstance(surfaces, list) or not surfaces:
				errors.append(f"source audit page {index} must contain data or no-public-data surfaces")
				continue
			for surface_index, surface in enumerate(surfaces):
				if not isinstance(surface, dict):
					errors.append(f"source audit page {index} surface {surface_index} must be an object")
					continue
				for key in (
					"kind",
					"location",
					"transportMethod",
					"operationType",
					"access",
					"parameters",
					"pagination",
					"filtering",
					"ordering",
					"responseEntity",
				):
					if not isinstance(surface.get(key), str) or not surface[key].strip():
						errors.append(f"source audit page {index} surface {surface_index} has no {key}")
				transport_method = str(surface.get("transportMethod", "")).casefold()
				operation_type = str(surface.get("operationType", "")).casefold()
				kind = str(surface.get("kind", "")).casefold()
				if kind not in SURFACE_KINDS:
					errors.append(f"source audit page {index} surface {surface_index} uses an unsupported surface kind")
				if not valid_public_url(
					surface.get("location"),
					allowed_private_origins=allowed_private_origins,
				):
					errors.append(f"source audit page {index} surface {surface_index} has an unsafe/non-public location")
				else:
					surface_locations.add(str(surface["location"]))
				allowed_operation_types = READ_OPERATION_TYPES.get(transport_method, set())
				is_graphql_query = (
					kind == "graphql"
					and transport_method == "post"
					and operation_type == "query"
					and valid_graphql_query_surface(surface)
				)
				if operation_type not in allowed_operation_types and not is_graphql_query:
					errors.append(f"source audit page {index} surface {surface_index} is not a read operation")
				if surface.get("access") != "anonymous-public":
					errors.append(f"source audit page {index} surface {surface_index} access must be anonymous-public")
				evidence_needles = [str(surface.get("location", "")), str(surface.get("responseEntity", ""))]
				if kind == "graphql":
					evidence_needles.extend(
						[str(surface.get("operationName", "")), str(surface.get("requestDocumentHash", ""))],
					)
				validate_evidence_refs(
					surface.get("evidence"),
					f"source audit page {index} surface {surface_index}",
					audit_root,
					errors,
					needle=evidence_needles,
				)
				if not non_empty_strings(surface.get("uiConsumers")):
					errors.append(f"source audit page {index} surface {surface_index} has no UI consumers")
				response_entity = surface.get("responseEntity")
				if isinstance(response_entity, str):
					surface_entities.append((kind, operation_type, response_entity))
			document = page.get("document")
			if not isinstance(document, dict):
				errors.append(f"source audit page {index} lacks a visible document closure")
				continue
			document_closures.append((str(url), document))
			if set(document) != {
				"surfaceLocation",
				"visibleEntities",
				"evidence",
			}:
				errors.append(f"source audit page {index} visible document closure has missing or unexpected fields")
			if not isinstance(document.get("surfaceLocation"), str) or not document["surfaceLocation"].strip():
				errors.append(f"source audit page {index} visible document closure lacks surface location")
			visible_entities = document.get("visibleEntities")
			if not isinstance(visible_entities, list) or not visible_entities:
				errors.append(f"source audit page {index} visible document closure has no visibleEntities")
				visible_entities = []
			for visible_index, visible_entity in enumerate(visible_entities):
				if not isinstance(visible_entity, dict) or set(visible_entity) != {
					"responseEntity",
					"visibleFieldRefs",
					"visibleRecordIds",
					"selectors",
				}:
					errors.append(
						f"source audit page {index} visible entity {visible_index} has missing or unexpected fields",
					)
					continue
				if not isinstance(visible_entity.get("responseEntity"), str) or not visible_entity["responseEntity"].strip():
					errors.append(f"source audit page {index} visible entity {visible_index} lacks responseEntity")
				for key in ("visibleFieldRefs", "visibleRecordIds", "selectors"):
					if not non_empty_strings(visible_entity.get(key)):
						errors.append(f"source audit page {index} visible entity {visible_index} has no {key}")
			has_matching_html_surface = any(
				isinstance(surface, dict)
				and str(surface.get("kind", "")).casefold() == "html"
				and surface.get("location") == document.get("surfaceLocation") == url
				for surface in surfaces
			)
			if not has_matching_html_surface:
				errors.append(f"source audit page {index} visible document closure lacks its HTML surface")
			validate_evidence_refs(
				document.get("evidence"),
				f"source audit page {index} visible document closure",
				audit_root,
				errors,
				needle=[
					str(url),
					*[
						str(value)
						for visible_entity in visible_entities
						if isinstance(visible_entity, dict)
						for key in ("responseEntity", "visibleFieldRefs", "visibleRecordIds", "selectors")
						for value in (
							visible_entity.get(key, [])
							if isinstance(visible_entity.get(key), list)
							else [visible_entity.get(key, "")]
						)
					],
				],
			)

	audit_fields: dict[str, dict[str, Any]] = {}
	audit_records: dict[tuple[str, str], dict[str, Any]] = {}
	entities = audit.get("entities")
	if not isinstance(entities, list) or not entities:
		errors.append("source audit entities must be a non-empty array, including an HTML document entity")
	else:
		entity_ids: set[str] = set()
		for entity_index, entity in enumerate(entities):
			if not isinstance(entity, dict):
				errors.append(f"source audit entity {entity_index} must be an object")
				continue
			entity_id = entity.get("id")
			if not isinstance(entity_id, str) or not entity_id.strip():
				errors.append(f"source audit entity {entity_index} has no stable id")
				continue
			if entity_id in entity_ids:
				errors.append(f"duplicate source audit entity id: {entity_id}")
			entity_ids.add(entity_id)
			source_location = entity.get("sourceLocation")
			if not valid_public_url(source_location, allowed_private_origins=allowed_private_origins):
				errors.append(f"source audit entity {entity_id} has no sourceLocation")
			elif source_location not in surface_locations:
				errors.append(
					f"source audit entity {entity_id} sourceLocation is not bound to an anonymous public surface",
				)
			fields = entity.get("fields")
			if not isinstance(fields, list) or not fields:
				errors.append(f"source audit entity {entity_id} has no fields")
				continue
			for field_index, field in enumerate(fields):
				if not isinstance(field, dict):
					errors.append(f"source audit {entity_id} field {field_index} must be an object")
					continue
				field_ref = field.get("ref")
				if not isinstance(field_ref, str) or not field_ref.strip():
					errors.append(f"source audit {entity_id} field {field_index} has no ref")
					continue
				if field_ref in audit_fields:
					errors.append(f"duplicate source field ref: {field_ref}")
					continue
				for required_key in (
					"path",
					"identifierRole",
					"enumDateSemantics",
					"relationshipCardinality",
					"localeStatus",
					"mediaShape",
				):
					if not isinstance(field.get(required_key), str) or not field[required_key].strip():
						errors.append(f"source field {field_ref} has no {required_key}")
				if not non_empty_strings(field.get("uiConsumers")):
					errors.append(f"source field {field_ref} uiConsumers must be a non-empty string array")
				observed_types = field.get("observedTypes")
				if (
					not isinstance(observed_types, list)
					or not observed_types
					or any(item not in OBSERVED_TYPES for item in observed_types)
				):
					errors.append(f"source field {field_ref} observedTypes must use supported JSON types")
				if not isinstance(field.get("nullable"), bool):
					errors.append(f"source field {field_ref} nullable must be boolean")
				if field.get("dataClass") not in PUBLIC_DATA_CLASSES:
					errors.append(f"source field {field_ref} dataClass must be an allowed public classification")
				if field_has_forbidden_private_semantics(field) or field_has_forbidden_private_values(field):
					errors.append(f"source field {field_ref} contains forbidden private/account identity data")
				if field.get("relationshipCardinality") not in {"none", "one", "many"}:
					errors.append(f"source field {field_ref} relationshipCardinality must be none, one, or many")
				elif field.get("relationshipCardinality") == "many":
					errors.append(
					f"source field {field_ref} has a many relationship; normalize it into source edge records with two singular references and optional order before mapping",
				)
				if (
					not isinstance(field.get("localeStatus"), str)
					or LOCALE_STATUS_PATTERN.fullmatch(field["localeStatus"]) is None
				):
					errors.append(f"source field {field_ref} localeStatus is not executable")
				if not isinstance(field.get("observedValues"), list) or not field["observedValues"]:
					errors.append(f"source field {field_ref} observedValues must be a non-empty sanitized array")
				if field_has_contact_semantics(field):
					if field.get("dataClass") != "public-business-contact":
						errors.append(
							f"source field {field_ref} contact data must use public-business-contact classification",
						)
					if not any(
						PUBLIC_CONTACT_CONSUMER_PATTERN.search(consumer)
						for consumer in field.get("uiConsumers", [])
						if isinstance(consumer, str)
					):
						errors.append(
							f"source field {field_ref} contact data lacks an anonymous public business-contact consumer",
						)
				entity_record_ids = [
					str(record.get("recordId"))
					for record in entity.get("records", [])
					if isinstance(record, dict) and isinstance(record.get("recordId"), str)
				]
				validate_evidence_refs(
					field.get("evidence"),
					f"source field {field_ref}",
					audit_root,
					errors,
					needle=[
						field_ref,
						*[
							value if isinstance(value, str) else compact_json(value)
							for value in field.get("observedValues", [])
						],
						*entity_record_ids,
					],
				)
				audit_fields[field_ref] = {**field, "_entityId": entity_id}

			field_refs = {
				field.get("ref")
				for field in fields
				if isinstance(field, dict) and isinstance(field.get("ref"), str)
			}
			records = entity.get("records")
			if not isinstance(records, list) or not records:
				errors.append(f"source audit entity {entity_id} has no record-level observations")
				continue
			for record_index, record in enumerate(records):
				if not isinstance(record, dict):
					errors.append(f"source audit entity {entity_id} record {record_index} must be an object")
					continue
				record_id = record.get("recordId")
				values = record.get("values")
				if not isinstance(record_id, str) or not record_id.strip():
					errors.append(f"source audit entity {entity_id} record {record_index} has no recordId")
					continue
				key = (entity_id, record_id)
				if key in audit_records:
					errors.append(f"duplicate source record id: {entity_id}.{record_id}")
					continue
				if not isinstance(values, dict) or set(values) != field_refs:
					errors.append(f"source record {entity_id}.{record_id} values must match every entity field ref")
					continue
				if not non_empty_strings(record.get("uiConsumers")):
					errors.append(f"source record {entity_id}.{record_id} uiConsumers must be non-empty")
				validate_evidence_refs(
					record.get("evidence"),
					f"source record {entity_id}.{record_id}",
					audit_root,
					errors,
					needle=[record_id, compact_json(values)],
				)
				audit_records[key] = record

			for field in fields:
				if not isinstance(field, dict) or not isinstance(field.get("ref"), str):
					continue
				field_ref = field["ref"]
				record_values = [
					record["values"][field_ref]
					for record in records
					if isinstance(record, dict) and isinstance(record.get("values"), dict) and field_ref in record["values"]
				]
				if [comparable_value(None, value) for value in field.get("observedValues", [])] != [
					comparable_value(None, value) for value in record_values
				]:
					errors.append(f"source field {field_ref} observedValues must preserve record order and cardinality")
				observed_types = field.get("observedTypes")
				actual_types = {json_value_type(value) for value in record_values}
				if isinstance(observed_types, list) and set(observed_types) != actual_types:
					errors.append(f"source field {field_ref} observedTypes do not match record values")
				if field.get("nullable") is False and any(value is None for value in record_values):
					errors.append(f"source field {field_ref} is non-nullable but contains null")

	entity_ids = {
		entity.get("id") for entity in entities if isinstance(entity, dict) and isinstance(entity.get("id"), str)
	} if isinstance(entities, list) else set()
	for kind, operation_type, response_entity in surface_entities:
		if response_entity == "none":
			if kind != "no-public-data" or operation_type != "no-public-data":
				errors.append("responseEntity none is valid only for a no-public-data surface")
		elif response_entity not in entity_ids:
			errors.append(f"source surface responseEntity is absent from entities: {response_entity}")

	visible_field_union: set[str] = set()
	visible_record_union: set[tuple[str, str]] = set()
	for page_url, document in document_closures:
		for visible_entity in document.get("visibleEntities", []):
			if not isinstance(visible_entity, dict):
				continue
			entity_id = visible_entity.get("responseEntity")
			entity_field_refs = {
				field_ref
				for field_ref, field in audit_fields.items()
				if field.get("_entityId") == entity_id
			}
			entity_record_ids = {
				record_id
				for source_entity, record_id in audit_records
				if source_entity == entity_id
			}
			visible_field_refs = visible_entity.get("visibleFieldRefs")
			visible_record_ids = visible_entity.get("visibleRecordIds")
			if not isinstance(entity_id, str) or entity_id not in entity_ids:
				errors.append(f"source page {page_url} visible document entity is absent from entities")
				continue
			if isinstance(visible_field_refs, list):
				unknown_fields = sorted(set(visible_field_refs) - entity_field_refs)
				if unknown_fields:
					errors.append(f"source page {page_url} visible document references unknown fields: {unknown_fields!r}")
				visible_field_union.update(item for item in visible_field_refs if isinstance(item, str))
			if isinstance(visible_record_ids, list):
				unknown_records = sorted(set(visible_record_ids) - entity_record_ids)
				if unknown_records:
					errors.append(f"source page {page_url} visible document references unknown records: {unknown_records!r}")
				visible_record_union.update(
					(entity_id, item) for item in visible_record_ids if isinstance(item, str)
				)
	missing_visible_fields = sorted(set(audit_fields) - visible_field_union)
	if missing_visible_fields:
		errors.append(f"source fields absent from every visible page document closure: {missing_visible_fields!r}")
	missing_visible_records = sorted(set(audit_records) - visible_record_union)
	if missing_visible_records:
		errors.append(f"source records absent from every visible page document closure: {missing_visible_records!r}")
	validate_document_snapshot(
		document_snapshot,
		document_closures,
		audit_fields,
		audit_records,
		errors,
	)

	mapping_fields = mapping.get("fields")
	mappings_by_ref: dict[str, dict[str, Any]] = {}
	if not isinstance(mapping_fields, list) or not mapping_fields:
		errors.append("field mapping fields must be a non-empty array")
	else:
		for index, field in enumerate(mapping_fields):
			if not isinstance(field, dict):
				errors.append(f"field mapping row {index} must be an object")
				continue
			source_ref = field.get("sourceRef")
			if not isinstance(source_ref, str) or not source_ref.strip():
				errors.append(f"field mapping row {index} has no sourceRef")
				continue
			if source_ref in mappings_by_ref:
				errors.append(f"duplicate field mapping sourceRef: {source_ref}")
				continue
			mappings_by_ref[source_ref] = field

	missing_mappings = sorted(set(audit_fields) - set(mappings_by_ref))
	if missing_mappings:
		errors.append("unmapped public source fields: " + ", ".join(missing_mappings))
	extra_mappings = sorted(set(mappings_by_ref) - set(audit_fields))
	if extra_mappings:
		errors.append("field mappings without source evidence: " + ", ".join(extra_mappings))

	audit_entities_by_id = {
		str(entity.get("id")): entity
		for entity in (entities if isinstance(entities, list) else [])
		if isinstance(entity, dict) and isinstance(entity.get("id"), str)
	}
	expected_entity_owner_keys = {
		(str(field.get("sourceEntity")), str(field.get("ownerKind")), str(field.get("ownerKey")))
		for field in mappings_by_ref.values()
		if all(isinstance(field.get(key), str) for key in ("sourceEntity", "ownerKind", "ownerKey"))
	}
	entity_mappings = mapping.get("entityMappings")
	entity_mappings_by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
	if not isinstance(entity_mappings, list) or not entity_mappings:
		errors.append("field mapping entityMappings must be a non-empty array")
	else:
		for index, entity_mapping in enumerate(entity_mappings):
			if not isinstance(entity_mapping, dict):
				errors.append(f"entity mapping {index} must be an object")
				continue
			key = (
				str(entity_mapping.get("sourceEntity", "")),
				str(entity_mapping.get("ownerKind", "")),
				str(entity_mapping.get("ownerKey", "")),
			)
			if key in entity_mappings_by_key:
				errors.append(f"duplicate structured entity mapping: {key}")
				continue
			entity_mappings_by_key[key] = entity_mapping
			audit_entity = audit_entities_by_id.get(key[0])
			if audit_entity is None:
				errors.append(f"entity mapping {key} has no source entity")
			elif entity_mapping.get("sourceLocation") != audit_entity.get("sourceLocation"):
				errors.append(f"entity mapping {key} sourceLocation does not match source audit")
			if key[1] not in OWNER_KINDS or not key[2]:
				errors.append(f"entity mapping {key} has an invalid Dineway owner")
			expected_render_consumers = {
				consumer
				for field in mappings_by_ref.values()
				if (
					field.get("sourceEntity"),
					field.get("ownerKind"),
					field.get("ownerKey"),
				) == key
				for consumer in field.get("renderConsumers", [])
				if isinstance(consumer, str)
			}
			if (
				not non_empty_strings(entity_mapping.get("renderConsumers"))
				or set(entity_mapping["renderConsumers"]) != expected_render_consumers
			):
				errors.append(f"entity mapping {key} renderConsumers do not match field mappings")
			validate_evidence_refs(
				entity_mapping.get("evidence"),
				f"entity mapping {key}",
				mapping_root,
				errors,
				needle=[key[0], str(entity_mapping.get("sourceLocation", ""))],
			)
	missing_entity_mappings = sorted(expected_entity_owner_keys - set(entity_mappings_by_key))
	extra_entity_mappings = sorted(set(entity_mappings_by_key) - expected_entity_owner_keys)
	if missing_entity_mappings:
		errors.append(f"field owners without structured entity mappings: {missing_entity_mappings!r}")
	if extra_entity_mappings:
		errors.append(f"structured entity mappings without field owners: {extra_entity_mappings!r}")

	collections = seed.get("collections", [])
	content = seed.get("content", {})
	settings = seed.get("settings", {})
	seen_collection_slugs: set[str] = set()
	if not isinstance(collections, list):
		errors.append("seed collections must be an array")
		collections = []
	for index, collection in enumerate(collections):
		if not isinstance(collection, dict):
			errors.append(f"seed collection {index} must be an object")
			continue
		slug = collection.get("slug")
		if (
			not isinstance(slug, str)
			or len(slug) > 63
			or STORAGE_SLUG_PATTERN.fullmatch(slug) is None
		):
			errors.append(f"seed collection {index} slug must be a valid <=63 character identifier")
		elif slug in RESERVED_COLLECTION_SLUGS:
			errors.append(f"seed collection uses reserved slug: {slug}")
		elif slug in seen_collection_slugs:
			errors.append(f"duplicate seed collection slug: {slug}")
		else:
			seen_collection_slugs.add(slug)
		supports = collection.get("supports", [])
		if (
			not isinstance(supports, list)
			or any(not isinstance(item, str) or item not in COLLECTION_SUPPORTS for item in supports)
			or len(supports) != len(set(supports))
		):
			errors.append(f"seed collection {slug} supports must use unique runtime support names")
			valid_supports: set[str] = set()
		else:
			valid_supports = set(supports)
		url_pattern = collection.get("urlPattern")
		if url_pattern is not None:
			if not valid_route_path(url_pattern, pattern=True):
				errors.append(f"seed collection {slug} urlPattern must be an exact root-relative {{slug}} pattern")
			if "seo" not in valid_supports:
				errors.append(f'seed routable collection {slug} must include supports ["seo"]')
		seen_field_slugs: set[str] = set()
		for field_index, seed_field in enumerate(collection.get("fields", [])):
			if not isinstance(seed_field, dict):
				errors.append(f"seed collection {slug} field {field_index} must be an object")
				continue
			field_slug = seed_field.get("slug")
			if (
				not isinstance(field_slug, str)
				or len(field_slug) > 63
				or STORAGE_SLUG_PATTERN.fullmatch(field_slug) is None
			):
				errors.append(f"seed collection {slug} field {field_index} has an invalid storage slug")
			elif field_slug in RESERVED_FIELD_SLUGS:
				errors.append(f"seed collection {slug} uses reserved custom field slug: {field_slug}")
			elif field_slug in seen_field_slugs:
				errors.append(f"seed collection {slug} has duplicate field slug: {field_slug}")
			else:
				seen_field_slugs.add(field_slug)
	for destination in sorted(planned_destination_routes):
		if not valid_route_path(destination):
			errors.append(f"planned destination route is not a canonical root-relative path: {destination}")
		elif not astro_route_exists(artifact_root, destination, collections):
			errors.append(f"planned destination route has no executable Astro SSR route: {destination}")

	seed_ids_by_collection: dict[str, set[str]] = {}
	all_seed_ids: set[str] = set()
	if isinstance(content, dict):
		for collection_slug, entries in content.items():
			ids: set[str] = set()
			if isinstance(entries, list):
				for entry in entries:
					if isinstance(entry, dict) and isinstance(entry.get("id"), str) and entry["id"].strip():
						if entry["id"] in all_seed_ids:
							errors.append(f"duplicate seed-local content id: {entry['id']}")
						ids.add(entry["id"])
						all_seed_ids.add(entry["id"])
			seed_ids_by_collection[collection_slug] = ids

	record_bindings = mapping.get("recordBindings")
	bindings_by_key: dict[tuple[str, str, str, str], dict[str, Any]] = {}
	seen_binding_targets: set[tuple[str, str, str, str]] = set()
	if not isinstance(record_bindings, list) or not record_bindings:
		errors.append("field mapping recordBindings must be a non-empty array")
	else:
		for index, binding in enumerate(record_bindings):
			if not isinstance(binding, dict):
				errors.append(f"record binding {index} must be an object")
				continue
			for key in ("sourceEntity", "sourceRecordId", "ownerKind", "ownerKey", "targetPointer"):
				if not isinstance(binding.get(key), str) or not binding[key].strip():
					errors.append(f"record binding {index} has no {key}")
			binding_key = (
				str(binding.get("sourceEntity", "")),
				str(binding.get("sourceRecordId", "")),
				str(binding.get("ownerKind", "")),
				str(binding.get("ownerKey", "")),
			)
			if binding_key in bindings_by_key:
				errors.append(f"duplicate record binding: {binding_key}")
				continue
			bindings_by_key[binding_key] = binding
			validate_evidence_refs(
				binding.get("evidence"),
				f"record binding {binding_key}",
				mapping_root,
				errors,
				needle=[str(binding.get("sourceRecordId", "")), str(binding.get("targetPointer", ""))],
			)
			target = decode_json_pointer(seed, binding.get("targetPointer"))
			if not isinstance(target, dict):
				errors.append(f"record binding {binding_key} targetPointer does not resolve to an object")
			elif not binding_owns_target(seed, binding.get("ownerKind"), binding.get("ownerKey"), target):
				errors.append(f"record binding {binding_key} targetPointer is outside its declared owner")
			target_key = (
				str(binding.get("sourceEntity", "")),
				str(binding.get("ownerKind", "")),
				str(binding.get("ownerKey", "")),
				str(binding.get("targetPointer", "")),
			)
			if target_key in seen_binding_targets:
				errors.append(f"multiple source records bind to the same Dineway target: {target_key}")
			seen_binding_targets.add(target_key)

	expected_bindings: set[tuple[str, str, str, str]] = set()
	owners_by_entity: dict[str, set[tuple[str, str]]] = {}
	for field in mappings_by_ref.values():
		source_entity = field.get("sourceEntity")
		owner_kind = field.get("ownerKind")
		owner_key = field.get("ownerKey")
		if all(isinstance(value, str) for value in (source_entity, owner_kind, owner_key)):
			owners_by_entity.setdefault(source_entity, set()).add((owner_kind, owner_key))
	for source_entity, record_id in audit_records:
		for owner_kind, owner_key in owners_by_entity.get(source_entity, set()):
			expected_bindings.add((source_entity, record_id, owner_kind, owner_key))
	missing_bindings = sorted(expected_bindings - set(bindings_by_key))
	extra_bindings = sorted(set(bindings_by_key) - expected_bindings)
	if missing_bindings:
		errors.append(f"source records without Dineway target bindings: {missing_bindings!r}")
	if extra_bindings:
		errors.append(f"Dineway target bindings without source records/owners: {extra_bindings!r}")

	collection_owners = {
		str(field.get("ownerKey"))
		for field in mappings_by_ref.values()
		if field.get("ownerKind") == "collection" and isinstance(field.get("ownerKey"), str)
	}
	mapped_custom_fields: dict[str, set[str]] = {owner_key: set() for owner_key in collection_owners}
	for field in mappings_by_ref.values():
		if field.get("ownerKind") != "collection":
			continue
		owner_key = field.get("ownerKey")
		storage_slug = field.get("storageSlug")
		if (
			isinstance(owner_key, str)
			and isinstance(storage_slug, str)
			and not storage_slug.startswith("system:")
		):
			mapped_custom_fields[owner_key].add(storage_slug)
	for owner_key, mapped_slugs in mapped_custom_fields.items():
		collection = find_named(collections, "slug", owner_key)
		if collection is not None:
			seed_slugs = {
				field.get("slug")
				for field in collection.get("fields", [])
				if isinstance(field, dict) and isinstance(field.get("slug"), str)
			}
			extra_seed_slugs = sorted(seed_slugs - mapped_slugs)
			if extra_seed_slugs:
				errors.append(
					f"seed custom fields without source mappings in {owner_key}: {extra_seed_slugs!r}",
				)
		entries = content.get(owner_key, []) if isinstance(content, dict) else []
		if not isinstance(entries, list):
			errors.append(f"seed content owner {owner_key} must be an array")
			continue
		bound_targets = {
			id(target)
			for binding in bindings_by_key.values()
			if binding.get("ownerKind") == "collection"
			and binding.get("ownerKey") == owner_key
			and isinstance((target := decode_json_pointer(seed, binding.get("targetPointer"))), dict)
		}
		unbound_entries: list[str] = []
		for index, entry in enumerate(entries):
			if not isinstance(entry, dict):
				continue
			if id(entry) not in bound_targets:
				unbound_entries.append(str(entry.get("id", index)))
			else:
				if entry.get("status") != "published":
					errors.append(f"source-backed public seed entry {owner_key}.{index} must be published")
				if not isinstance(entry.get("slug"), str) or not entry["slug"].strip():
					errors.append(f"source-backed public seed entry {owner_key}.{index} must have a slug")
			data = entry.get("data")
			if isinstance(data, dict):
				extra_data_slugs = sorted(set(data) - mapped_slugs)
				if extra_data_slugs:
					errors.append(
						f"seed content data without source mappings in {owner_key}: {extra_data_slugs!r}",
					)
		if unbound_entries:
			errors.append(
				f"seed content entries without source record bindings in {owner_key}: {unbound_entries!r}",
			)
		collection = find_named(collections, "slug", owner_key)
		url_pattern = collection.get("urlPattern") if isinstance(collection, dict) else None
		if isinstance(url_pattern, str) and isinstance(entries, list):
			for entry_index, entry in enumerate(entries):
				slug = entry.get("slug") if isinstance(entry, dict) else None
				generated_route = url_pattern.replace("{slug}", slug) if isinstance(slug, str) else ""
				if generated_route not in planned_destination_routes:
					errors.append(
						f"seed collection {owner_key} entry {entry_index} does not match a planned destination route",
					)

	menu_owners = {
		str(field.get("ownerKey"))
		for field in mappings_by_ref.values()
		if field.get("ownerKind") == "menu" and isinstance(field.get("ownerKey"), str)
	}
	for owner_key in menu_owners:
		menu = find_named(seed.get("menus", []), "name", owner_key)
		if menu is None:
			continue
		bound_targets = {
			id(target)
			for binding in bindings_by_key.values()
			if binding.get("ownerKind") == "menu"
			and binding.get("ownerKey") == owner_key
			and isinstance((target := decode_json_pointer(seed, binding.get("targetPointer"))), dict)
		}
		unbound_items = [
			str(item.get("label", index))
			for index, item in enumerate(menu_item_objects(menu.get("items")))
			if id(item) not in bound_targets
		]
		if unbound_items:
			errors.append(
				f"seed menu items without source record bindings in {owner_key}: {unbound_items!r}",
			)
		mapped_paths = {
			str(field.get("targetPath"))
			for field in mappings_by_ref.values()
			if field.get("ownerKind") == "menu" and field.get("ownerKey") == owner_key
		}
		for index, item in enumerate(menu_item_objects(menu.get("items"))):
			content_keys = (set(item) & MENU_ITEM_PATHS) - {"children"}
			extra_keys = sorted(content_keys - mapped_paths)
			if extra_keys:
				errors.append(
					f"seed menu item {owner_key}.{index} fields without source mappings: {extra_keys!r}",
				)

	settings_mapped_paths = {
		str(field.get("targetPath"))
		for field in mappings_by_ref.values()
		if field.get("ownerKind") == "settings" and field.get("ownerKey") == "settings"
	}
	if settings_mapped_paths:
		extra_settings_paths = sorted(present_settings_paths(settings) - settings_mapped_paths)
		if extra_settings_paths:
			errors.append(f"seed settings fields without source mappings: {extra_settings_paths!r}")

	section_owners = {
		str(field.get("ownerKey"))
		for field in mappings_by_ref.values()
		if field.get("ownerKind") == "section" and isinstance(field.get("ownerKey"), str)
	}
	for owner_key in section_owners:
		section = find_named(seed.get("sections", []), "slug", owner_key)
		if section is None:
			continue
		mapped_paths = {
			str(field.get("targetPath"))
			for field in mappings_by_ref.values()
			if field.get("ownerKind") == "section" and field.get("ownerKey") == owner_key
		}
		content_paths = set(section) & SECTION_PATHS
		if section.get("content") == []:
			content_paths.discard("content")
		extra_paths = sorted(content_paths - mapped_paths)
		if extra_paths:
			errors.append(f"seed section fields without source mappings in {owner_key}: {extra_paths!r}")

	taxonomy_owners = {
		str(field.get("ownerKey"))
		for field in mappings_by_ref.values()
		if field.get("ownerKind") == "taxonomy" and isinstance(field.get("ownerKey"), str)
	}
	for owner_key in taxonomy_owners:
		taxonomy = find_named(seed.get("taxonomies", []), "name", owner_key)
		if taxonomy is None:
			continue
		mapped_paths = {
			str(field.get("targetPath"))
			for field in mappings_by_ref.values()
			if field.get("ownerKind") == "taxonomy" and field.get("ownerKey") == owner_key
		}
		mapped_term_keys = {path.removeprefix("terms.") for path in mapped_paths if path.startswith("terms.")}
		terms = taxonomy.get("terms", [])
		if isinstance(terms, list) and terms and not mapped_term_keys:
			errors.append(f"seed taxonomy terms without term-level source mappings in {owner_key}")
		elif isinstance(terms, list) and mapped_term_keys:
			bound_targets = {
				id(target)
				for binding in bindings_by_key.values()
				if binding.get("ownerKind") == "taxonomy"
				and binding.get("ownerKey") == owner_key
				and isinstance((target := decode_json_pointer(seed, binding.get("targetPointer"))), dict)
			}
			unbound_terms: list[str] = []
			for index, term in enumerate(terms):
				if not isinstance(term, dict):
					continue
				if id(term) not in bound_targets:
					unbound_terms.append(str(term.get("slug", index)))
				content_keys = set(term) & {"label", "description", "parent"}
				extra_term_keys = sorted(content_keys - mapped_term_keys)
				if extra_term_keys:
					errors.append(
						f"seed taxonomy term {owner_key}.{index} fields without source mappings: {extra_term_keys!r}",
					)
			if unbound_terms:
				errors.append(
					f"seed taxonomy terms without source record bindings in {owner_key}: {unbound_terms!r}",
				)

	seen_targets: set[tuple[str, str, str]] = set()
	seen_canonical_names: set[tuple[str, str, str]] = set()
	for source_ref, field in mappings_by_ref.items():
		if "approvedExclusion" in field or "approvedExclusionEvidence" in field:
			errors.append(f"mapping {source_ref} may not replace a Dineway mapping with a self-approved exclusion")

		for key in (
			"sourceEntity",
			"sourcePath",
			"ownerKind",
			"ownerKey",
			"targetPath",
			"canonicalName",
			"runtimeReadPath",
			"type",
			"localeBehavior",
			"statusBehavior",
			"mediaOwnership",
			"sourceDataClass",
		):
			if not isinstance(field.get(key), str) or not field[key].strip():
				errors.append(f"mapping {source_ref} has no {key}")
		if field.get("statusBehavior") != "published":
			errors.append(f"mapping {source_ref} statusBehavior must be published for anonymous public source content")
		if not isinstance(field.get("required"), bool) or not isinstance(field.get("nullable"), bool):
			errors.append(f"mapping {source_ref} required and nullable must be booleans")
		for key in ("validation", "options"):
			if not isinstance(field.get(key), dict):
				errors.append(f"mapping {source_ref} {key} must be an object")
		for key in ("seedConsumers", "renderConsumers"):
			if not non_empty_strings(field.get(key)):
				errors.append(f"mapping {source_ref} {key} must be a non-empty string array")
		validate_site_consumers(
			field.get("seedConsumers"),
			f"mapping {source_ref} seedConsumers",
			mapping_root,
			errors,
			kind="seed",
			owner_kind=field.get("ownerKind"),
			owner_key=field.get("ownerKey"),
			field_tokens=(field.get("targetPath"), field.get("canonicalName"), field.get("storageSlug")),
		)
		validate_site_consumers(
			field.get("renderConsumers"),
			f"mapping {source_ref} renderConsumers",
			mapping_root,
			errors,
			kind="render",
			owner_kind=field.get("ownerKind"),
			owner_key=field.get("ownerKey"),
			field_tokens=(field.get("runtimeReadPath"),),
		)
		validate_evidence_refs(
			field.get("evidence"),
			f"mapping {source_ref}",
			mapping_root,
			errors,
			needle=source_ref,
		)
		relationship = field.get("relationship")
		if not isinstance(relationship, dict) or relationship.get("cardinality") not in {"none", "one", "many"}:
			errors.append(f"mapping {source_ref} relationship cardinality must be none, one, or many")
		elif relationship.get("cardinality") != "none" and not isinstance(relationship.get("targetOwner"), str):
			errors.append(f"mapping {source_ref} relationship targetOwner is required")

		owner_kind = field.get("ownerKind")
		owner_key = field.get("ownerKey")
		target_path = field.get("targetPath")
		canonical_name = field.get("canonicalName")
		storage_slug = field.get("storageSlug")
		runtime_read_path = field.get("runtimeReadPath")
		field_type = field.get("type")
		media_metadata = field.get("mediaMetadata")
		if media_metadata is not None:
			if field_type not in {"image", "file"} or not isinstance(media_metadata, dict):
				errors.append(f"mapping {source_ref} mediaMetadata is valid only for image/file mappings")
			elif set(media_metadata) - set(MEDIA_METADATA_SOURCE_KEYS.values()):
				errors.append(f"mapping {source_ref} mediaMetadata has unsupported keys")
			else:
				for metadata_key, metadata_ref in media_metadata.items():
					metadata_field = audit_fields.get(metadata_ref) if isinstance(metadata_ref, str) else None
					if (
						metadata_field is None
						or metadata_ref == source_ref
						or metadata_field.get("_entityId") != field.get("sourceEntity")
						or set(metadata_field.get("observedTypes", [])) - {"string", "null"}
					):
						errors.append(
							f"mapping {source_ref} {metadata_key} must reference a string field on the same source entity",
						)
		audit_field = audit_fields.get(source_ref)
		if audit_field is not None:
			if field.get("sourceEntity") != audit_field.get("_entityId"):
				errors.append(f"mapping {source_ref} sourceEntity does not match source audit")
			if field.get("sourcePath") != audit_field.get("path"):
				errors.append(f"mapping {source_ref} sourcePath does not match source audit")
			if field.get("nullable") != audit_field.get("nullable"):
				errors.append(f"mapping {source_ref} nullable does not match source audit")
			if field.get("sourceDataClass") != audit_field.get("dataClass"):
				errors.append(f"mapping {source_ref} sourceDataClass does not match source audit")
			if field.get("localeBehavior") != audit_field.get("localeStatus"):
				errors.append(f"mapping {source_ref} localeBehavior does not match source audit locale/status")
			if audit_field.get("dataClass") == "public-media" or str(audit_field.get("mediaShape", "")).casefold() not in {
				"none",
				"n/a",
			}:
				if field_type not in {"image", "file"} or field.get("mediaOwnership") != "cms":
					errors.append(
						f"mapping {source_ref} public media must use a Dineway image/file field with CMS ownership",
					)
			source_cardinality = audit_field.get("relationshipCardinality")
			mapped_cardinality = relationship.get("cardinality") if isinstance(relationship, dict) else None
			if source_cardinality in {"none", "one"} and mapped_cardinality != source_cardinality:
				errors.append(f"mapping {source_ref} relationship cardinality does not match source audit")
			if source_cardinality == "many":
				errors.append(
					f"mapping {source_ref} cannot map a raw many relationship; normalize it into source edge records first",
				)
			enum_date_semantics = str(audit_field.get("enumDateSemantics", "")).casefold()
			if "enum" in enum_date_semantics and field_type not in {"select", "multiSelect"}:
				errors.append(f"mapping {source_ref} enum semantics require select/multiSelect")
			if ("date" in enum_date_semantics or "time" in enum_date_semantics) and field_type != "datetime":
				errors.append(f"mapping {source_ref} date semantics require datetime")
			if "url" in enum_date_semantics and field_type not in {"url", "image", "file"}:
				errors.append(f"mapping {source_ref} URL semantics require url/image/file")
			identifier_role = str(audit_field.get("identifierRole", "none")).casefold()
			if identifier_role not in {"none", "n/a"} and not (
				storage_slug in {"system:id", "system:slug"} or field_type in {"reference", "slug"}
			):
				errors.append(f"mapping {source_ref} identifier role lacks an executable identifier target")
			observed_types = audit_field.get("observedTypes")
			if isinstance(observed_types, list) and isinstance(field_type, str):
				incompatible_types = [
					observed_type
					for observed_type in observed_types
					if observed_type in OBSERVED_TO_DINEWAY_TYPES
					and field_type not in OBSERVED_TO_DINEWAY_TYPES[observed_type]
				]
				if incompatible_types:
					errors.append(
						f"mapping {source_ref} Dineway type {field_type} is incompatible with observed types {incompatible_types}",
					)
		if owner_kind not in OWNER_KINDS:
			errors.append(f"mapping {source_ref} has unsupported ownerKind: {owner_kind}")
			continue
		if not isinstance(canonical_name, str) or CAMEL_CASE_PATTERN.fullmatch(canonical_name) is None:
			errors.append(f"mapping {source_ref} canonicalName must be lower camelCase")
		expected_read_path = expected_runtime_read_path(owner_kind, target_path, storage_slug)
		if expected_read_path is None or runtime_read_path != expected_read_path:
			errors.append(f"mapping {source_ref} runtimeReadPath must match Dineway runtime path {expected_read_path}")
		expected_fixed_name = fixed_owner_canonical_name(owner_kind, target_path)
		if expected_fixed_name is not None and canonical_name != expected_fixed_name:
			errors.append(
				f"mapping {source_ref} canonicalName must match runtime key {expected_fixed_name}",
			)
		if field_type not in FIELD_TYPES:
			errors.append(f"mapping {source_ref} has unsupported Dineway type: {field_type}")
		elif not valid_validation_definition(field_type, field.get("validation")):
			errors.append(f"mapping {source_ref} has an invalid Dineway validation definition")
		if isinstance(relationship, dict):
			cardinality = relationship.get("cardinality")
			if cardinality == "many":
				errors.append(
					f"mapping {source_ref} cannot use unsupported many-valued Dineway references; use a link collection",
				)
			if cardinality in {"one", "many"} and field_type != "reference":
				errors.append(f"mapping {source_ref} relationship must use the reference field type")
			if field_type == "reference" and cardinality == "none":
				errors.append(f"mapping {source_ref} reference field must declare one/many cardinality")
			if cardinality in {"one", "many"}:
				target_owner = relationship.get("targetOwner")
				if not isinstance(target_owner, str) or find_named(collections, "slug", target_owner) is None:
					errors.append(f"mapping {source_ref} relationship target collection is absent from seed")
		if field.get("mediaOwnership") not in {"cms", "static", "none"}:
			errors.append(f"mapping {source_ref} mediaOwnership must be cms, static, or none")
		if field_type in {"image", "file"} and field.get("mediaOwnership") != "cms":
			errors.append(f"mapping {source_ref} editable media must use CMS media ownership")
		if field_type not in {"image", "file"} and field.get("mediaOwnership") != "none":
			errors.append(f"mapping {source_ref} non-media field must use mediaOwnership none")
		if not isinstance(owner_key, str) or not isinstance(target_path, str):
			continue
		target_key = (owner_kind, owner_key, target_path)
		if target_key in seen_targets:
			errors.append(f"mapping {source_ref} collides at {owner_kind}:{owner_key}:{target_path}")
		seen_targets.add(target_key)
		canonical_key = (str(owner_kind), str(owner_key), str(canonical_name))
		if canonical_key in seen_canonical_names:
			errors.append(f"mapping {source_ref} collides at Dineway canonicalName {canonical_name}")
		seen_canonical_names.add(canonical_key)

		if owner_kind == "collection":
			collection = find_named(collections, "slug", owner_key)
			if collection is None:
				errors.append(f"mapping {source_ref} collection does not exist in seed: {owner_key}")
				continue
			if isinstance(storage_slug, str) and storage_slug.startswith("system:"):
				system_slug = storage_slug.removeprefix("system:")
				if system_slug not in SEEDABLE_SYSTEM_FIELDS or target_path != system_slug:
					errors.append(f"mapping {source_ref} has invalid system field marker: {storage_slug}")
					continue
				if canonical_name != snake_to_camel(system_slug):
					errors.append(f"mapping {source_ref} canonicalName does not match system field {system_slug}")
				if field_type != SEEDABLE_SYSTEM_FIELDS[system_slug]:
					errors.append(f"mapping {source_ref} type does not match system field {system_slug}")
				entries = content.get(owner_key, []) if isinstance(content, dict) else []
				values = [entry.get(system_slug) for entry in entries if isinstance(entry, dict) and system_slug in entry]
				if not values:
					errors.append(f"mapping {source_ref} has no seeded system values for {owner_key}.{system_slug}")
				elif not all(
					valid_seed_value(
						field_type,
						value,
						nullable=bool(field.get("nullable")),
						allowed_private_origins=allowed_private_origins,
					)
					for value in values
				):
					errors.append(f"mapping {source_ref} has invalid seeded system values for {field_type}")
				if field.get("required") and len(values) != len(entries):
					errors.append(f"mapping {source_ref} required system field is missing from a seed entry")
				validate_observed_value_closure(errors, source_ref, audit_field, field_type, values)
				continue
			if not isinstance(storage_slug, str) or len(storage_slug) > 63 or STORAGE_SLUG_PATTERN.fullmatch(storage_slug) is None:
				errors.append(f"mapping {source_ref} storageSlug must be a valid <=63 character identifier")
				continue
			if storage_slug in RESERVED_FIELD_SLUGS:
				errors.append(f"mapping {source_ref} uses reserved custom storageSlug: {storage_slug}")
				continue
			if canonical_name != snake_to_camel(storage_slug):
				errors.append(f"mapping {source_ref} canonicalName must be the camelCase form of storageSlug")
			if target_path != storage_slug:
				errors.append(f"mapping {source_ref} targetPath must equal its custom storageSlug")
			seed_field = find_named(collection.get("fields"), "slug", storage_slug)
			if seed_field is None:
				errors.append(f"mapping {source_ref} field is absent from seed collection {owner_key}: {storage_slug}")
				continue
			if seed_field.get("label") != canonical_name:
				errors.append(f"mapping {source_ref} seed label must equal canonicalName {canonical_name}")
			if seed_field.get("type") != field_type:
				errors.append(f"mapping {source_ref} seed field type does not match {field_type}")
			if seed_field.get("validation", {}) != field.get("validation"):
				errors.append(f"mapping {source_ref} seed validation does not match")
			if seed_field.get("options", {}) != field.get("options"):
				errors.append(f"mapping {source_ref} seed options do not match")
			if bool(seed_field.get("required", False)) != bool(field.get("required")):
				errors.append(f"mapping {source_ref} seed required flag does not match")
			entries = content.get(owner_key, []) if isinstance(content, dict) else []
			values = [
				entry["data"][storage_slug]
				for entry in entries
				if isinstance(entry, dict) and isinstance(entry.get("data"), dict) and storage_slug in entry["data"]
			]
			if not values:
				errors.append(f"mapping {source_ref} has no seeded content value for {owner_key}.{storage_slug}")
			elif not all(
				valid_seed_value(
					field_type,
					value,
					nullable=bool(field.get("nullable")),
					cardinality=str(relationship.get("cardinality")) if isinstance(relationship, dict) else "none",
					allowed_private_origins=allowed_private_origins,
				)
				and valid_field_constraints(field_type, value, field.get("validation"))
				for value in values
			):
				errors.append(f"mapping {source_ref} has seeded values incompatible with Dineway type {field_type}")
			if field_type in {"image", "file"}:
				validate_seed_media_metadata(errors, source_ref, field, audit_fields, values)
			if field_type == "reference" and isinstance(relationship, dict):
				target_owner = relationship.get("targetOwner")
				target_ids = seed_ids_by_collection.get(target_owner, set()) if isinstance(target_owner, str) else set()
				for value in values:
					references = value if isinstance(value, list) else [value]
					for reference in references:
						if isinstance(reference, str) and reference.startswith("$ref:") and reference[5:] not in target_ids:
							errors.append(f"mapping {source_ref} contains unresolved reference: {reference}")
				if seed_field.get("options", {}).get("collection") != target_owner:
					errors.append(f"mapping {source_ref} seed reference options must name target collection {target_owner}")
			if field.get("required") and len(values) != len(entries):
				errors.append(f"mapping {source_ref} required field is missing from a seed entry")
			validate_observed_value_closure(errors, source_ref, audit_field, field_type, values)
		elif owner_kind == "settings":
			if owner_key != "settings":
				errors.append(f"mapping {source_ref} settings ownerKey must be settings")
			if storage_slug not in (None, "N/A"):
				errors.append(f"mapping {source_ref} fixed settings field must use null/N/A storageSlug")
			if target_path not in SETTING_PATHS:
				errors.append(f"mapping {source_ref} uses unsupported settings path: {target_path}")
			else:
				value = nested_value(settings, target_path)
				if value is None:
					errors.append(f"mapping {source_ref} settings path is absent from seed: {target_path}")
				elif field_type not in FIXED_OWNER_TYPES["settings"].get(target_path, set()):
					errors.append(f"mapping {source_ref} settings path {target_path} cannot use type {field_type}")
				elif target_path in {"logo", "favicon", "seo.defaultOgImage"} and not valid_settings_media_reference(value):
					errors.append(f"mapping {source_ref} settings media must use a well-formed mediaId/alt reference")
				elif target_path not in {"logo", "favicon", "seo.defaultOgImage"} and not valid_fixed_settings_value(
					target_path,
					field_type,
					value,
					nullable=bool(field.get("nullable")),
					allowed_private_origins=allowed_private_origins,
				):
					errors.append(f"mapping {source_ref} settings value is incompatible with type {field_type}")
				if target_path in {"logo", "favicon", "seo.defaultOgImage"}:
					media_source_url = field.get("mediaSourceUrl")
					if not valid_public_url(
						media_source_url,
						allowed_private_origins=allowed_private_origins,
					):
						errors.append(f"mapping {source_ref} settings media requires a sanitized mediaSourceUrl")
					else:
						validate_observed_value_closure(errors, source_ref, audit_field, field_type, [media_source_url])
					if isinstance(value, dict):
						validate_seed_media_metadata(errors, source_ref, field, audit_fields, [value])
						validate_evidence_refs(
							field.get("evidence"),
							f"mapping {source_ref} settings media",
							mapping_root,
							errors,
							needle=[source_ref, str(value.get("mediaId", "")), str(media_source_url or "")],
						)
				else:
					validate_observed_value_closure(errors, source_ref, audit_field, field_type, [value])
		elif owner_kind == "menu":
			if storage_slug not in (None, "N/A"):
				errors.append(f"mapping {source_ref} fixed menu field must use null/N/A storageSlug")
			if target_path not in MENU_ITEM_PATHS:
				errors.append(f"mapping {source_ref} uses unsupported menu item path: {target_path}")
			elif field_type not in FIXED_OWNER_TYPES["menu"].get(target_path, set()):
				errors.append(f"mapping {source_ref} menu path {target_path} cannot use type {field_type}")
			menu = find_named(seed.get("menus", []), "name", owner_key)
			if menu is None or not menu_items_contain(menu.get("items"), target_path):
				errors.append(f"mapping {source_ref} menu field is absent from seed: {owner_key}.{target_path}")
			else:
				values = menu_item_values(menu.get("items"), target_path)
				if not all(
					valid_seed_value(
						field_type,
						value,
						nullable=bool(field.get("nullable")),
						allowed_private_origins=allowed_private_origins,
					)
					for value in values
				):
					errors.append(f"mapping {source_ref} menu values are incompatible with type {field_type}")
				validate_observed_value_closure(errors, source_ref, audit_field, field_type, values)
		elif owner_kind == "section":
			if storage_slug not in (None, "N/A"):
				errors.append(f"mapping {source_ref} fixed section field must use null/N/A storageSlug")
			if target_path not in SECTION_PATHS:
				errors.append(f"mapping {source_ref} uses unsupported section path: {target_path}")
			elif field_type not in FIXED_OWNER_TYPES["section"].get(target_path, set()):
				errors.append(f"mapping {source_ref} section path {target_path} cannot use type {field_type}")
			section = find_named(seed.get("sections", []), "slug", owner_key)
			if section is None or target_path not in section:
				errors.append(f"mapping {source_ref} section field is absent from seed: {owner_key}.{target_path}")
			elif not valid_seed_value(
				field_type,
				section[target_path],
				nullable=bool(field.get("nullable")),
				allowed_private_origins=allowed_private_origins,
			):
				errors.append(f"mapping {source_ref} section value is incompatible with type {field_type}")
			else:
				validate_observed_value_closure(
					errors,
					source_ref,
					audit_field,
					field_type,
					[section[target_path]],
				)
		elif owner_kind == "taxonomy":
			if storage_slug not in (None, "N/A"):
				errors.append(f"mapping {source_ref} fixed taxonomy field must use null/N/A storageSlug")
			if target_path not in TAXONOMY_PATHS:
				errors.append(f"mapping {source_ref} uses unsupported taxonomy path: {target_path}")
			elif field_type not in FIXED_OWNER_TYPES["taxonomy"].get(target_path, set()):
				errors.append(f"mapping {source_ref} taxonomy path {target_path} cannot use type {field_type}")
			taxonomy = find_named(seed.get("taxonomies", []), "name", owner_key)
			if taxonomy is None:
				errors.append(f"mapping {source_ref} taxonomy is absent from seed: {owner_key}")
			elif target_path.startswith("terms."):
				term_key = target_path.removeprefix("terms.")
				terms = taxonomy.get("terms", [])
				values = [term[term_key] for term in terms if isinstance(term, dict) and term_key in term]
				if not values:
					errors.append(f"mapping {source_ref} taxonomy term field has no seeded values: {target_path}")
				elif not all(
					valid_seed_value(
						field_type,
						value,
						nullable=bool(field.get("nullable")),
						allowed_private_origins=allowed_private_origins,
					)
					for value in values
				):
					errors.append(f"mapping {source_ref} taxonomy term values are incompatible with type {field_type}")
				if field.get("required") and len(values) != len(terms):
					errors.append(f"mapping {source_ref} required taxonomy term field is missing")
				validate_observed_value_closure(errors, source_ref, audit_field, field_type, values)
			elif target_path not in taxonomy:
				errors.append(f"mapping {source_ref} taxonomy field is absent from seed: {target_path}")
			elif not valid_seed_value(
				field_type,
				taxonomy[target_path],
				nullable=bool(field.get("nullable")),
				allowed_private_origins=allowed_private_origins,
			):
				errors.append(f"mapping {source_ref} taxonomy value is incompatible with type {field_type}")
			else:
				validate_observed_value_closure(
					errors,
					source_ref,
					audit_field,
					field_type,
					[taxonomy[target_path]],
				)

	for binding_key in sorted(expected_bindings & set(bindings_by_key)):
		source_entity, source_record_id, owner_kind, owner_key = binding_key
		binding = bindings_by_key[binding_key]
		record = audit_records.get((source_entity, source_record_id))
		target = decode_json_pointer(seed, binding.get("targetPointer"))
		if record is None or not isinstance(record.get("values"), dict) or not isinstance(target, dict):
			continue
		for source_ref, field in mappings_by_ref.items():
			if (
				field.get("sourceEntity") != source_entity
				or field.get("ownerKind") != owner_kind
				or field.get("ownerKey") != owner_key
			):
				continue
			if source_ref not in record["values"]:
				continue
			locale_behavior = field.get("localeBehavior")
			locale_match = (
				re.fullmatch(r"(?:public|localized)/([A-Za-z0-9-]+)", locale_behavior)
				if isinstance(locale_behavior, str)
				else None
			)
			if locale_match is not None and locale_behavior != "public/default":
				expected_locale = locale_match.group(1)
				if owner_kind in {"settings", "section"}:
					errors.append(
						f"record binding {source_entity}.{source_record_id} uses localized content in unsupported owner {owner_kind}",
					)
				elif target.get("locale") != expected_locale:
					errors.append(
						f"record binding {source_entity}.{source_record_id} must use seed locale {expected_locale}",
					)
			found, target_value = binding_target_value(target, field)
			if not found:
				errors.append(
					f"record binding {source_entity}.{source_record_id} lacks mapped target value for {source_ref}",
				)
				continue
			source_value = record["values"][source_ref]
			seed_target_value = target_value
			media_metadata = field.get("mediaMetadata")
			if field.get("type") in {"image", "file"} and isinstance(media_metadata, dict):
				media_value = (
					seed_target_value.get("$media")
					if isinstance(seed_target_value, dict) and isinstance(seed_target_value.get("$media"), dict)
					else seed_target_value
				)
				for media_key, config_key in MEDIA_METADATA_SOURCE_KEYS.items():
					metadata_ref = media_metadata.get(config_key)
					if not isinstance(metadata_ref, str):
						continue
					if (
						metadata_ref not in record["values"]
						or not isinstance(media_value, dict)
						or media_value.get(media_key) != record["values"][metadata_ref]
					):
						errors.append(
							f"record binding {source_entity}.{source_record_id} does not preserve {metadata_ref} in media metadata",
						)
			if (
				owner_kind == "settings"
				and field.get("targetPath") in {"logo", "favicon", "seo.defaultOgImage"}
			):
				target_value = field.get("mediaSourceUrl")
			if comparable_value(field.get("type"), source_value) != comparable_value(field.get("type"), target_value):
				errors.append(
					f"record binding {source_entity}.{source_record_id} does not preserve {source_ref}",
				)

	validate_settings_media_proofs(
		settings_media_proof,
		mappings_by_ref,
		seed,
		errors,
		allowed_private_origins=allowed_private_origins,
		root=artifact_root,
	)
	if phase == "completion" and isinstance(clone_url, str):
		validate_runtime_content_proof(
			runtime_content_proof,
			mappings_by_ref,
			document_snapshot,
			audit_fields,
			audit_records,
			clone_url,
			artifact_root,
			errors,
		)

	return errors


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--audit", type=Path, required=True)
	parser.add_argument("--document-snapshot", type=Path, required=True)
	parser.add_argument("--mapping", type=Path, required=True)
	parser.add_argument("--seed", type=Path, required=True)
	parser.add_argument("--settings-media-proof", type=Path, required=True)
	parser.add_argument("--runtime-content-proof", type=Path)
	parser.add_argument("--agent", type=Path, required=True)
	parser.add_argument("--site-root", type=Path, required=True)
	parser.add_argument(
		"--clone-url",
		help="Caller-trusted localhost/loopback URL of the running clone used for reversible runtime proof",
	)
	parser.add_argument("--phase", choices=("foundation", "completion"), required=True)
	parser.add_argument(
		"--explicit-url",
		action="append",
		required=True,
		help="Caller-trusted source URL from the original user request; repeat for every explicit URL",
	)
	args = parser.parse_args()

	errors = validate_artifacts(
		args.audit,
		args.document_snapshot,
		args.mapping,
		args.seed,
		args.settings_media_proof,
		args.runtime_content_proof,
		args.agent,
		args.site_root,
		args.explicit_url,
		args.clone_url,
		args.phase,
	)
	if errors:
		print("INVALID Dineway clone data model", file=sys.stderr)
		for error in errors:
			print(f"- {error}", file=sys.stderr)
		return 1

	print("VALID Dineway clone data model")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

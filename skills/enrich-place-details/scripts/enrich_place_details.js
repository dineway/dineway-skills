#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const DEFAULT_BASE_URL = "https://api.dineway.ai";
const DEFAULT_LANGUAGE = "en";
const DEFAULT_TIMEOUT_MS = 20000;
const DEFAULT_BOOTSTRAP_PLACE_ID = "ChIJs5ydyTiuEmsR0fRSlU0C7k0";
const DEFAULT_OUTPUT_DIR = "places";
const FOOD_TYPES = new Set(["restaurant", "cafe", "food", "meal_takeaway", "meal_delivery", "bakery"]);
const VALUE_FLAGS = new Map([
	["--name", "name"],
	["--restaurant", "name"],
	["--city", "city"],
	["--place-id", "placeId"],
	["--placeId", "placeId"],
	["--language", "language"],
	["--base-url", "baseUrl"],
	["--bootstrap-place-id", "bootstrapPlaceId"],
	["--output-dir", "outputDir"],
	["--timeout-ms", "timeoutMs"],
]);
const EQUALS_FLAG_RE = /^(--[A-Za-z-]+)=(.*)$/;
const TRAILING_SLASHES_RE = /\/+$/;
const DIACRITICS_RE = /[\u0300-\u036f]/g;
const NON_COMPARE_RE = /[^\p{Letter}\p{Number}]+/gu;
const LOCATION_PARTS_RE = /[,;|/]+|\s+-\s+/u;
const PLACE_ID_RE = /^[A-Za-z0-9_-]{10,}$/;
const SAFE_FILENAME_RE = /[^A-Za-z0-9_-]+/g;

class HttpError extends Error {
	constructor(message, { status, body, cause }) {
		super(message, cause ? { cause } : undefined);
		this.name = "HttpError";
		this.status = status;
		this.body = body;
	}
}

function usage() {
	return `Usage:
  node scripts/enrich_place_details.js --name "Peace Harmony" --city "Sydney, Australia"
  node scripts/enrich_place_details.js "Peace Harmony" "Sydney, Australia" --place-id "ChIJs5ydyTiuEmsR0fRSlU0C7k0"

Required:
  --name, --restaurant     Restaurant name
  --city                   City, region, or city/country

Options:
  --place-id, --placeId    Optional user-provided place id
  --language               Shadow user language (default: en)
  --base-url               Dineway API base URL (default: https://api.dineway.ai)
  --bootstrap-place-id     Temporary bootstrap id used when no valid place id is provided
  --output-dir             Directory for saved JSON, relative to cwd unless absolute (default: ./places)
  --include-candidates     Include all search candidates in output
  --details-only           Save only the detail endpoint response instead of the full payload
  --compact                Print compact JSON
  --timeout-ms             Request timeout in milliseconds
  --help                   Show this help`;
}

function parseArgs(argv) {
	const options = {
		name: "",
		city: "",
		placeId: "",
		language: process.env.DINEWAY_SHADOW_LANGUAGE || DEFAULT_LANGUAGE,
		baseUrl: process.env.DINEWAY_API_BASE_URL || DEFAULT_BASE_URL,
		bootstrapPlaceId: process.env.DINEWAY_BOOTSTRAP_PLACE_ID || DEFAULT_BOOTSTRAP_PLACE_ID,
		outputDir: DEFAULT_OUTPUT_DIR,
		includeCandidates: false,
		detailsOnly: false,
		compact: false,
		timeoutMs: DEFAULT_TIMEOUT_MS,
	};
	const positional = [];

	for (let index = 0; index < argv.length; index += 1) {
		const arg = argv[index];
		if (arg === "--help" || arg === "-h") {
			options.help = true;
			continue;
		}
		if (arg === "--include-candidates") {
			options.includeCandidates = true;
			continue;
		}
		if (arg === "--details-only") {
			options.detailsOnly = true;
			continue;
		}
		if (arg === "--compact") {
			options.compact = true;
			continue;
		}

		const equalsMatch = arg.match(EQUALS_FLAG_RE);
		if (equalsMatch && VALUE_FLAGS.has(equalsMatch[1])) {
			const key = VALUE_FLAGS.get(equalsMatch[1]);
			options[key] = equalsMatch[2];
			continue;
		}

		if (VALUE_FLAGS.has(arg)) {
			const key = VALUE_FLAGS.get(arg);
			const value = argv[index + 1];
			if (!value || value.startsWith("--")) {
				throw new Error(`${arg} requires a value`);
			}
			options[key] = value;
			index += 1;
			continue;
		}

		if (arg.startsWith("--")) {
			throw new Error(`Unknown option: ${arg}`);
		}
		positional.push(arg);
	}

	if (!options.name && positional[0]) options.name = positional[0];
	if (!options.city && positional[1]) options.city = positional[1];
	options.name = String(options.name || "").trim();
	options.city = String(options.city || "").trim();
	options.placeId = String(options.placeId || "").trim();
	options.language = String(options.language || DEFAULT_LANGUAGE).trim() || DEFAULT_LANGUAGE;
	options.baseUrl = String(options.baseUrl || DEFAULT_BASE_URL).replace(TRAILING_SLASHES_RE, "");
	options.bootstrapPlaceId = String(options.bootstrapPlaceId || DEFAULT_BOOTSTRAP_PLACE_ID).trim();
	options.outputDir = String(options.outputDir || DEFAULT_OUTPUT_DIR).trim() || DEFAULT_OUTPUT_DIR;
	options.timeoutMs = Number(options.timeoutMs);

	if (!Number.isFinite(options.timeoutMs) || options.timeoutMs < 1000) {
		throw new Error("--timeout-ms must be a number >= 1000");
	}

	return options;
}

function missingInputs(options) {
	const missing = [];
	if (!options.name) missing.push("restaurant name");
	if (!options.city) missing.push("city");
	return missing;
}

function normalize(value) {
	return String(value || "")
		.toLowerCase()
		.normalize("NFKD")
		.replace(DIACRITICS_RE, "")
		.replace(NON_COMPARE_RE, "");
}

function looksLikePlaceId(value) {
	const id = String(value || "").trim();
	return PLACE_ID_RE.test(id);
}

function safePlaceFilename(placeId) {
	return `${String(placeId || "place").replace(SAFE_FILENAME_RE, "_") || "place"}.json`;
}

function relativeDisplayPath(filePath) {
	const relativePath = path.relative(process.cwd(), filePath);
	if (!relativePath || relativePath.startsWith("..") || path.isAbsolute(relativePath)) {
		return filePath;
	}
	return relativePath;
}

function writePlaceJson(payload, placeId, outputDir) {
	const targetDir = path.isAbsolute(outputDir) ? outputDir : path.resolve(process.cwd(), outputDir);
	fs.mkdirSync(targetDir, { recursive: true });
	const outputPath = path.join(targetDir, safePlaceFilename(placeId));
	fs.writeFileSync(outputPath, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
	return {
		outputPath,
		displayPath: relativeDisplayPath(outputPath),
	};
}

function buildSavedOutputSummary(payload, savedFile, savedPayloadType) {
	return {
		placeId: payload.selectedPlace?.placeId ?? payload.authFlow?.finalPlaceId ?? null,
		placeDetailsPath: savedFile.displayPath,
		savedPayload: savedPayloadType,
		selectedPlace: payload.selectedPlace,
		search: {
			resultCount: payload.search?.resultCount ?? null,
			selectionReason: payload.search?.selectionReason ?? null,
			selectedCandidate: payload.search?.selectedCandidate ?? null,
		},
	};
}

function uniqueStrings(values) {
	return [...new Set(values.map((value) => String(value || "").trim()).filter(Boolean))];
}

function displayText(value) {
	if (typeof value === "string" || typeof value === "number") return String(value);
	if (Array.isArray(value)) return value.map(displayText).filter(Boolean).join(" ");
	if (value && typeof value === "object") {
		return (
			displayText(value.text) ||
			displayText(value.name) ||
			displayText(value.displayName) ||
			displayText(value.longText) ||
			displayText(value.shortText) ||
			displayText(value.long_name) ||
			displayText(value.short_name) ||
			displayText(value.value)
		);
	}
	return "";
}

function candidatePlaceId(candidate) {
	return String(candidate?.placeId || candidate?.id || "").trim();
}

function candidateNameTexts(candidate) {
	return uniqueStrings([
		displayText(candidate?.displayName),
		displayText(candidate?.name),
		displayText(candidate?.businessName),
		displayText(candidate?.title),
	]);
}

function candidateAddressTexts(candidate) {
	const addressComponents = Array.isArray(candidate?.addressComponents)
		? candidate.addressComponents.flatMap((component) => [
				displayText(component?.longText),
				displayText(component?.shortText),
				displayText(component?.long_name),
				displayText(component?.short_name),
				displayText(component?.name),
			])
		: [];

	return uniqueStrings([
		displayText(candidate?.formattedAddress),
		displayText(candidate?.shortFormattedAddress),
		displayText(candidate?.address),
		displayText(candidate?.vicinity),
		displayText(candidate?.plusCode?.compoundCode),
		displayText(candidate?.plus_code?.compound_code),
		...addressComponents,
	]);
}

function candidateAddress(candidate) {
	return candidateAddressTexts(candidate).join(" ");
}

function candidateTypes(candidate) {
	const types = [
		...(Array.isArray(candidate?.types) ? candidate.types : []),
		candidate?.primaryType,
		candidate?.primary_type,
	];
	return uniqueStrings(types).map((type) => type.toLowerCase());
}

function locationParts(value) {
	const parts = String(value || "")
		.split(LOCATION_PARTS_RE)
		.map(normalize)
		.filter(Boolean);
	return uniqueStrings(parts);
}

function scoreNameMatch(queryName, candidateNames) {
	let bestScore = 0;
	let bestReason = "";

	for (const name of candidateNames) {
		const currentName = normalize(name);
		if (!queryName || !currentName) continue;

		let score = 0;
		let reason = "";
		if (currentName === queryName) {
			score = 120;
			reason = "exact_name";
		} else if (currentName.includes(queryName)) {
			score = 80;
			reason = "candidate_contains_name";
		} else if (queryName.includes(currentName) && currentName.length >= Math.min(4, queryName.length)) {
			score = 45;
			reason = "query_contains_candidate_name";
		}

		if (score > bestScore) {
			bestScore = score;
			bestReason = reason;
		}
	}

	return { score: bestScore, reason: bestReason };
}

function scoreLocationMatch(city, candidate) {
	const queryLocation = normalize(city);
	const parts = locationParts(city);
	const candidateLocation = normalize(candidateAddress(candidate));
	let score = 0;
	const reasons = [];

	if (!candidateLocation) return { score, reasons };

	if (queryLocation && candidateLocation.includes(queryLocation)) {
		score += 55;
		reasons.push("location_full_match");
		return { score, reasons };
	}

	const [primaryPart, ...secondaryParts] = parts;
	if (primaryPart && candidateLocation.includes(primaryPart)) {
		score += 38;
		reasons.push("location_primary_match");
	}

	for (const part of secondaryParts) {
		if (part.length >= 3 && candidateLocation.includes(part)) {
			score += 10;
			reasons.push("location_secondary_match");
		}
	}

	return { score, reasons };
}

function compactCandidate(candidate, matchContext) {
	if (!candidate || typeof candidate !== "object") return null;
	const match = matchContext ? scoreCandidate(candidate, matchContext) : null;
	return {
		placeId: candidatePlaceId(candidate),
		displayName: candidate.displayName ?? candidate.name ?? candidate.businessName ?? candidate.title ?? null,
		formattedAddress:
			candidate.formattedAddress ?? candidate.shortFormattedAddress ?? candidate.address ?? candidate.vicinity ?? null,
		types:
			candidate.types ??
			(candidate.primaryType || candidate.primary_type ? [candidate.primaryType ?? candidate.primary_type] : null),
		rating: candidate.rating ?? null,
		userRatingCount: candidate.userRatingCount ?? candidate.user_ratings_total ?? null,
		priceLevel: candidate.priceLevel ?? null,
		businessStatus: candidate.businessStatus ?? candidate.business_status ?? null,
		matchScore: match?.score ?? null,
		matchReason: match?.reason ?? null,
	};
}

function scoreCandidate(candidate, { name, city, providedPlaceId }) {
	const queryName = normalize(name);
	const currentPlaceId = candidatePlaceId(candidate);

	let score = 0;
	const reasons = [];

	if (providedPlaceId && currentPlaceId === providedPlaceId) {
		score += 10000;
		reasons.push("provided_place_id");
	}

	const nameMatch = scoreNameMatch(queryName, candidateNameTexts(candidate));
	if (nameMatch.score) {
		score += nameMatch.score;
		reasons.push(nameMatch.reason);
	}

	const locationMatch = scoreLocationMatch(city, candidate);
	if (locationMatch.score) {
		score += locationMatch.score;
		reasons.push(...locationMatch.reasons);
	}

	const types = candidateTypes(candidate);
	if (types.some((type) => FOOD_TYPES.has(type))) {
		score += 10;
		reasons.push("food_type");
	}

	const businessStatus = String(candidate.businessStatus ?? candidate.business_status ?? "").toUpperCase();
	if (businessStatus === "OPERATIONAL") {
		score += 4;
		reasons.push("operational");
	} else if (businessStatus === "CLOSED_PERMANENTLY") {
		score -= 60;
		reasons.push("closed_permanently");
	}

	const rating = Number(candidate.rating);
	if (Number.isFinite(rating)) {
		score += Math.min(Math.max(rating, 0), 5);
	}

	const reviewCount = Number(candidate.userRatingCount ?? candidate.user_ratings_total);
	if (Number.isFinite(reviewCount)) {
		score += Math.min(Math.max(reviewCount, 0), 500) / 100;
	}

	return { score, reason: reasons.join("+") || "fallback" };
}

function selectCandidate(places, context) {
	let best = null;
	let bestScore = Number.NEGATIVE_INFINITY;
	let bestReason = "fallback";

	for (const candidate of places) {
		if (!candidate || typeof candidate !== "object") continue;
		const { score, reason } = scoreCandidate(candidate, context);
		if (score > bestScore) {
			best = candidate;
			bestScore = score;
			bestReason = reason;
		}
	}

	if (!best) return null;
	return { candidate: best, reason: bestReason, score: bestScore };
}

async function readJsonResponse(response) {
	const text = await response.text();
	if (!text) return null;
	try {
		return JSON.parse(text);
	} catch (error) {
		throw new HttpError("API returned non-JSON response", {
			status: response.status,
			body: text.slice(0, 1000),
			cause: error,
		});
	}
}

async function fetchJson(url, { method = "GET", headers = {}, body, timeoutMs }) {
	const controller = new AbortController();
	const timeout = setTimeout(() => controller.abort(), timeoutMs);
	try {
		const requestOptions = {
			method,
			headers,
			signal: controller.signal,
		};
		if (body !== undefined) {
			requestOptions.body = JSON.stringify(body);
		}
		const response = await fetch(url, requestOptions);
		const payload = await readJsonResponse(response);
		if (!response.ok) {
			throw new HttpError(`${method} ${url} failed with HTTP ${response.status}`, {
				status: response.status,
				body: payload,
			});
		}
		return payload;
	} catch (error) {
		if (error?.name === "AbortError") {
			throw new Error(`${method} ${url} timed out after ${timeoutMs}ms`, { cause: error });
		}
		throw error;
	} finally {
		clearTimeout(timeout);
	}
}

function extractTokens(payload, context) {
	const accessToken = payload?.accessToken ?? payload?.data?.accessToken ?? payload?.tokens?.accessToken;
	const refreshToken = payload?.refreshToken ?? payload?.data?.refreshToken ?? payload?.tokens?.refreshToken;
	if (typeof accessToken !== "string" || !accessToken) {
		throw new Error(`${context} response did not include accessToken`);
	}
	if (typeof refreshToken !== "string" || !refreshToken) {
		throw new Error(`${context} response did not include refreshToken`);
	}
	return { accessToken, refreshToken };
}

async function createShadowUser({ baseUrl, placeId, language, timeoutMs }) {
	const payload = await fetchJson(`${baseUrl}/api/auth/users/shadow`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: { placeId, language },
		timeoutMs,
	});
	const tokens = extractTokens(payload, "Shadow user");
	return {
		placeId,
		accessToken: tokens.accessToken,
		refreshToken: tokens.refreshToken,
		user: payload?.user ?? payload?.data?.user ?? null,
		isNewUser: payload?.isNewUser ?? payload?.data?.isNewUser ?? null,
	};
}

async function refreshAuth(auth, { baseUrl, timeoutMs }) {
	const payload = await fetchJson(`${baseUrl}/api/auth/refresh?client_type=server`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: { refreshToken: auth.refreshToken },
		timeoutMs,
	});
	const tokens = extractTokens(payload, "Refresh");
	auth.accessToken = tokens.accessToken;
	auth.refreshToken = tokens.refreshToken;
	auth.user = payload?.user ?? payload?.data?.user ?? auth.user ?? null;
	return auth;
}

async function fetchWithAuth(auth, endpointPath, { baseUrl, timeoutMs, method = "GET", body } = {}) {
	const headers = {
		Authorization: `Bearer ${auth.accessToken}`,
	};
	if (body !== undefined) headers["Content-Type"] = "application/json";

	try {
		return await fetchJson(`${baseUrl}${endpointPath}`, {
			method,
			headers,
			body,
			timeoutMs,
		});
	} catch (error) {
		if (error instanceof HttpError && error.status === 401) {
			await refreshAuth(auth, { baseUrl, timeoutMs });
			const retryHeaders = {
				Authorization: `Bearer ${auth.accessToken}`,
			};
			if (body !== undefined) retryHeaders["Content-Type"] = "application/json";
			return fetchJson(`${baseUrl}${endpointPath}`, {
				method,
				headers: retryHeaders,
				body,
				timeoutMs,
			});
		}
		throw error;
	}
}

function extractPlaces(searchResponse) {
	const places =
		searchResponse?.places ??
		searchResponse?.results ??
		searchResponse?.data?.places ??
		searchResponse?.data?.results;
	if (!Array.isArray(places)) {
		throw new Error("Search response did not include a places/results array");
	}
	return places.filter((candidate) => candidate && typeof candidate === "object");
}

function detailDisplayName(detail, fallback) {
	return detail?.displayName ?? fallback?.displayName ?? fallback?.name ?? null;
}

function detailFormattedAddress(detail, fallback) {
	return detail?.formattedAddress ?? fallback?.formattedAddress ?? null;
}

async function enrichPlaceDetails(options) {
	const providedPlaceId = looksLikePlaceId(options.placeId) ? options.placeId : "";
	const initialPlaceId = providedPlaceId || options.bootstrapPlaceId;
	if (!looksLikePlaceId(initialPlaceId)) {
		throw new Error("No valid place id was provided and the bootstrap place id is invalid");
	}

	const initialAuth = await createShadowUser({
		baseUrl: options.baseUrl,
		placeId: initialPlaceId,
		language: options.language,
		timeoutMs: options.timeoutMs,
	});

	const textQuery = `${options.name} in ${options.city}`;
	const searchResponse = await fetchWithAuth(initialAuth, "/api/places/search", {
		baseUrl: options.baseUrl,
		timeoutMs: options.timeoutMs,
		method: "POST",
		body: { textQuery },
	});
	const candidates = extractPlaces(searchResponse);

	if (candidates.length === 0 && !providedPlaceId) {
		throw new Error(`Search returned no candidates for "${textQuery}"`);
	}

	const matchContext = {
		name: options.name,
		city: options.city,
		providedPlaceId,
	};
	const selected = selectCandidate(candidates, matchContext);

	const selectedCandidate = selected?.candidate ?? null;
	const selectedCandidatePlaceId = selectedCandidate ? candidatePlaceId(selectedCandidate) : "";
	const finalPlaceId = providedPlaceId || selectedCandidatePlaceId;
	if (!looksLikePlaceId(finalPlaceId)) {
		throw new Error("Could not determine a valid place id from the user input or search results");
	}

	const usedBootstrapPlaceId = !providedPlaceId;
	const requiresRebind = usedBootstrapPlaceId || finalPlaceId !== initialPlaceId;
	const finalAuth = requiresRebind
		? await createShadowUser({
				baseUrl: options.baseUrl,
				placeId: finalPlaceId,
				language: options.language,
				timeoutMs: options.timeoutMs,
			})
		: initialAuth;

	const detailResponse = await fetchWithAuth(finalAuth, `/api/places/${encodeURIComponent(finalPlaceId)}`, {
		baseUrl: options.baseUrl,
		timeoutMs: options.timeoutMs,
	});

	const selectedPlace = {
		placeId: finalPlaceId,
		displayName: detailDisplayName(detailResponse, selectedCandidate),
		formattedAddress: detailFormattedAddress(detailResponse, selectedCandidate),
	};

	const result = {
		query: {
			name: options.name,
			city: options.city,
			textQuery,
			providedPlaceId: providedPlaceId || null,
			baseUrl: options.baseUrl,
			language: options.language,
		},
		authFlow: {
			initialPlaceId,
			initialPlaceIdSource: providedPlaceId ? "user" : "bootstrap",
			reboundShadowUser: requiresRebind,
			finalPlaceId,
		},
		search: {
			resultCount: candidates.length,
			selectionReason: selected?.reason ?? (providedPlaceId ? "provided_place_id_no_search_match" : "none"),
			selectedCandidate: compactCandidate(selectedCandidate, matchContext),
		},
		selectedPlace,
		placeDetails: detailResponse,
	};

	if (options.includeCandidates) {
		result.search.candidates = candidates.map((candidate) => compactCandidate(candidate, matchContext));
	}

	return result;
}

async function main() {
	let options;
	try {
		options = parseArgs(process.argv.slice(2));
	} catch (error) {
		console.error(error.message);
		console.error(usage());
		return 2;
	}

	if (options.help) {
		console.log(usage());
		return 0;
	}

	const missing = missingInputs(options);
	if (missing.length > 0) {
		console.error(`Missing required input: ${missing.join(" and ")}. Provide both restaurant name and city.`);
		return 2;
	}

	try {
		const payload = await enrichPlaceDetails(options);
		const savedPayload = options.detailsOnly ? payload.placeDetails : payload;
		const placeId = payload.selectedPlace?.placeId ?? payload.authFlow?.finalPlaceId;
		const savedFile = writePlaceJson(savedPayload, placeId, options.outputDir);
		const output = buildSavedOutputSummary(payload, savedFile, options.detailsOnly ? "placeDetails" : "fullPayload");
		console.log(JSON.stringify(output, null, options.compact ? 0 : 2));
		return 0;
	} catch (error) {
		if (error instanceof HttpError) {
			console.error(`${error.message}: ${JSON.stringify(error.body)}`);
		} else {
			console.error(error.message || String(error));
		}
		return 1;
	}
}

main().then(
	(code) => {
		process.exitCode = code;
		return undefined;
	},
	(error) => {
		console.error(error?.message || String(error));
		process.exitCode = 1;
		return undefined;
	},
);

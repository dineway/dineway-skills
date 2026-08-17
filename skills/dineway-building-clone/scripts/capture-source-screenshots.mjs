#!/usr/bin/env node

/** Capture an image-complete source page as viewport tiles, then stitch it. */

import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, extname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { chromium } from "@playwright/test";

const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));
const STITCH_SCRIPT = join(SCRIPT_DIR, "stitch-browser-screenshots.py");
const MAX_PRELOAD_PASSES = 6;
const MAX_CAPTURE_PASSES = 3;
const SENSITIVE_QUERY_PATTERN = /(?:auth|credential|key|pass|secret|session|sig|token)/iu;
const PNG_EXTENSION_PATTERN = /\.png$/iu;
const CSS_URL_PATTERN_SOURCE = String.raw`url\(["']?([^"')]+)["']?\)`;

function usage() {
	return `Usage: node capture-source-screenshots.mjs --url <http(s)://...> --output <file.png> [options]

Options:
  --width <css-px>       Viewport width (default: 1440)
  --height <css-px>      Viewport height (default: 900)
  --timeout-ms <ms>      Navigation/media timeout (default: 60000)
  --settle-ms <ms>       Delay after each scroll (default: 250)
  --headed               Show Chromium while capturing`;
}

function parsePositiveInteger(value, name) {
	const parsed = Number(value);
	if (!Number.isInteger(parsed) || parsed <= 0) {
		throw new Error(`${name} must be a positive integer`);
	}
	return parsed;
}

function parseArgs(argv) {
	const options = {
		width: 1440,
		height: 900,
		timeoutMs: 60_000,
		settleMs: 250,
		headed: false,
	};

	for (let index = 0; index < argv.length; index += 1) {
		const argument = argv[index];
		if (argument === "--headed") {
			options.headed = true;
			continue;
		}

		const value = argv[index + 1];
		if (!value || value.startsWith("--")) {
			throw new Error(`Missing value for ${argument}`);
		}
		index += 1;

		switch (argument) {
			case "--url":
				options.url = value;
				break;
			case "--output":
				options.output = value;
				break;
			case "--width":
				options.width = parsePositiveInteger(value, "--width");
				break;
			case "--height":
				options.height = parsePositiveInteger(value, "--height");
				break;
			case "--timeout-ms":
				options.timeoutMs = parsePositiveInteger(value, "--timeout-ms");
				break;
			case "--settle-ms":
				options.settleMs = parsePositiveInteger(value, "--settle-ms");
				break;
			default:
				throw new Error(`Unknown argument: ${argument}`);
		}
	}

	if (!options.url || !options.output) {
		throw new Error("--url and --output are required");
	}
	const url = new URL(options.url);
	if (!new Set(["http:", "https:"]).has(url.protocol)) {
		throw new Error("--url must use HTTP or HTTPS");
	}
	if (extname(options.output).toLowerCase() !== ".png") {
		throw new Error("--output must be a .png file");
	}

	return { ...options, url: url.href, output: resolve(options.output) };
}

function sanitizeUrl(value) {
	try {
		const url = new URL(value);
		url.username = "";
		url.password = "";
		for (const key of url.searchParams.keys()) {
			if (SENSITIVE_QUERY_PATTERN.test(key)) {
				url.searchParams.set(key, "[redacted]");
			}
		}
		return url.href;
	} catch {
		return value.startsWith("data:") ? "data:[inline]" : value;
	}
}

function pngDimensions(path) {
	const header = readFileSync(path).subarray(0, 24);
	if (header.length < 24 || header.toString("hex", 1, 4) !== "504e47") {
		throw new Error(`Expected PNG output: ${path}`);
	}
	return { width: header.readUInt32BE(16), height: header.readUInt32BE(20) };
}

function metadataPathFor(output) {
	return output.replace(PNG_EXTENSION_PATTERN, ".capture.json");
}

function tileDirectoryFor(output) {
	return output.replace(PNG_EXTENSION_PATTERN, ".tiles");
}

async function documentState(page) {
	return page.evaluate(() => {
		const root = document.documentElement;
		const body = document.body;
		return {
			innerWidth: window.innerWidth,
			innerHeight: window.innerHeight,
			devicePixelRatio: window.devicePixelRatio,
			scrollHeight: Math.ceil(
				Math.max(
					root.scrollHeight,
					root.offsetHeight,
					root.clientHeight,
					body?.scrollHeight ?? 0,
					body?.offsetHeight ?? 0,
				),
			),
		};
	});
}

async function scrollToCssPosition(page, requestedY, timeoutMs) {
	const targetY = await page.evaluate((scrollY) => {
		const root = document.documentElement;
		root.style.setProperty("scroll-behavior", "auto", "important");
		document.body?.style.setProperty("scroll-behavior", "auto", "important");
		const maximumY = Math.max(0, root.scrollHeight - window.innerHeight);
		const target = Math.min(Math.max(0, Math.round(scrollY)), maximumY);
		window.scrollTo({ top: target, left: 0, behavior: "instant" });
		return target;
	}, requestedY);
	await page.waitForFunction(
		(expectedY) => Math.abs(window.scrollY - expectedY) <= 1,
		targetY,
		{ timeout: Math.min(timeoutMs, 5000) },
	);
	return Math.round(await page.evaluate(() => window.scrollY));
}

async function waitForFonts(page, timeoutMs) {
	let timeout;
	try {
		await Promise.race([
			page.evaluate(async () => {
				if (document.fonts) await document.fonts.ready;
			}),
			new Promise((_, reject) => {
				timeout = setTimeout(() => reject(new Error("Timed out waiting for document fonts")), timeoutMs);
			}),
		]);
	} finally {
		if (timeout) clearTimeout(timeout);
	}
	return true;
}

async function waitForViewportImages(page, timeoutMs) {
	try {
		await page.waitForFunction(
			() => {
				return [...document.images]
					.filter((image) => {
						const style = getComputedStyle(image);
						const rect = image.getBoundingClientRect();
						return (
							style.display !== "none" &&
							style.visibility !== "hidden" &&
							Number(style.opacity) !== 0 &&
							rect.width > 0 &&
							rect.height > 0 &&
							rect.bottom > 0 &&
							rect.top < window.innerHeight
						);
					})
					.every((image) => {
						const expectedSource =
							image.currentSrc ||
							image.getAttribute("src") ||
							image.getAttribute("data-src") ||
							image.getAttribute("data-lazy-src") ||
							image.closest("picture")?.querySelector("source[srcset], source[data-srcset]");
						if (!expectedSource) return true;
						return Boolean(image.currentSrc || image.src) && image.complete && image.naturalWidth > 0;
					});
			},
			undefined,
			{ timeout: timeoutMs },
		);
		return true;
	} catch {
		return false;
	}
}

async function decodeRenderedImages(page) {
	await page.evaluate(async () => {
		await Promise.allSettled(
			[...document.images]
				.filter((image) => {
					const style = getComputedStyle(image);
					const rect = image.getBoundingClientRect();
					return (
						style.display !== "none" &&
						style.visibility !== "hidden" &&
						rect.width > 0 &&
						rect.height > 0 &&
						image.complete &&
						image.naturalWidth > 0
					);
				})
				.map((image) => image.decode()),
		);
	});
}

async function auditImages(page) {
	return page.evaluate(() => {
		const images = [...document.images]
			.filter((image) => {
				const style = getComputedStyle(image);
				const rect = image.getBoundingClientRect();
				return (
					style.display !== "none" &&
					style.visibility !== "hidden" &&
					Number(style.opacity) !== 0 &&
					rect.width > 0 &&
					rect.height > 0
				);
			})
			.map((image, index) => {
				const pictureSource = image.closest("picture")?.querySelector("source[srcset], source[data-srcset]");
				return {
					index,
					source:
						image.currentSrc ||
						image.getAttribute("src") ||
						image.getAttribute("data-src") ||
						image.getAttribute("data-lazy-src") ||
						pictureSource?.getAttribute("srcset") ||
						pictureSource?.getAttribute("data-srcset") ||
						"",
					complete: image.complete,
					naturalWidth: image.naturalWidth,
					naturalHeight: image.naturalHeight,
				};
			});
		const expected = images.filter((image) => image.source);
		const failed = expected.filter(
			(image) => !image.complete || image.naturalWidth <= 0 || image.naturalHeight <= 0,
		);

		return {
			renderedImageElements: expected.length,
			loadedImageElements: expected.length - failed.length,
			failedImages: failed,
			imageSignature: expected.map((image) => image.source).toSorted(),
		};
	});
}

async function preloadCssAndPosterImages(page, timeoutMs) {
	const urls = await page.evaluate((urlPatternSource) => {
		const values = new Set();
		const urlPattern = new RegExp(urlPatternSource, "giu");
		function add(value) {
			for (const match of value.matchAll(urlPattern)) values.add(match[1]);
		}
		for (const element of document.querySelectorAll("*")) {
			const style = getComputedStyle(element);
			const rect = element.getBoundingClientRect();
			if (style.display === "none" || style.visibility === "hidden" || rect.width <= 0 || rect.height <= 0) {
				continue;
			}
			add(style.backgroundImage);
			add(style.borderImageSource);
			add(style.listStyleImage);
			add(style.maskImage);
		}
		for (const video of document.querySelectorAll("video[poster]")) {
			if (video.poster) values.add(video.poster);
		}
		return [...values];
	}, CSS_URL_PATTERN_SOURCE);

	const results = await page.evaluate(
		async ({ mediaUrls, timeout }) =>
			Promise.all(
				mediaUrls.map(async (url) => {
					const image = new Image();
					image.src = url;
					let timer;
					const timedResult = new Promise((complete) => {
						timer = setTimeout(complete, timeout, { url, loaded: false, reason: "timeout" });
					});
					const decodedResult = image.decode().then(
						() => ({ url, loaded: image.naturalWidth > 0, reason: "decode" }),
						() => ({ url, loaded: false, reason: "error" }),
					);
					const result = await Promise.race([decodedResult, timedResult]);
					clearTimeout(timer);
					return result;
				}),
			),
		{ mediaUrls: urls, timeout: timeoutMs },
	);

	return {
		backgroundAndPosterAssets: results.length,
		loadedBackgroundAndPosterAssets: results.filter((result) => result.loaded).length,
		failed: results.filter((result) => !result.loaded),
		assetSignature: results.map((result) => result.url).toSorted(),
	};
}

async function throwForIncompleteImages(page, timeoutMs) {
	await decodeRenderedImages(page);
	const imageAudit = await auditImages(page);
	const cssAudit = await preloadCssAndPosterImages(page, timeoutMs);
	const failed = [
		...imageAudit.failedImages.map((image) => ({
			source: sanitizeUrl(image.source),
			reason: image.complete ? "zero natural dimensions" : "load incomplete",
		})),
		...cssAudit.failed.map((image) => ({ source: sanitizeUrl(image.url), reason: image.reason })),
	];
	if (failed.length > 0) {
		throw new Error(`Incomplete rendered image assets: ${JSON.stringify(failed)}`);
	}
	return { ...imageAudit, ...cssAudit, failedImages: [] };
}

async function scrollThroughPage(page, settleMs, timeoutMs) {
	let previousSignature = null;
	let lastAudit = null;

	for (let pass = 1; pass <= MAX_PRELOAD_PASSES; pass += 1) {
		let state = await documentState(page);
		const step = Math.max(100, Math.floor(state.innerHeight * 0.8));
		for (let y = 0; ; y = Math.min(y + step, state.scrollHeight - state.innerHeight)) {
			await scrollToCssPosition(page, Math.max(0, y), timeoutMs);
			await page.waitForTimeout(settleMs);
			const viewportReady = await waitForViewportImages(page, Math.min(timeoutMs, 15_000));
			if (!viewportReady) await throwForIncompleteImages(page, Math.min(timeoutMs, 15_000));
			state = await documentState(page);
			if (windowEnd(y, state) >= state.scrollHeight) break;
		}

		await scrollToCssPosition(page, state.scrollHeight, timeoutMs);
		await page.waitForTimeout(settleMs);
		const bottomReady = await waitForViewportImages(page, Math.min(timeoutMs, 15_000));
		if (!bottomReady) await throwForIncompleteImages(page, Math.min(timeoutMs, 15_000));
		lastAudit = await throwForIncompleteImages(page, Math.min(timeoutMs, 15_000));
		state = await documentState(page);
		const signature = JSON.stringify([
			state.scrollHeight,
			lastAudit.imageSignature,
			lastAudit.assetSignature,
		]);
		if (signature === previousSignature) {
			await scrollToCssPosition(page, 0, timeoutMs);
			await page.waitForTimeout(settleMs);
			return { state, audit: lastAudit, passes: pass, stable: true };
		}
		previousSignature = signature;
	}

	throw new Error("The source document height or rendered image set did not stabilize");
}

function windowEnd(y, state) {
	return Math.max(0, y) + state.innerHeight;
}

function validateTileCoverage(tiles, documentHeight) {
	if (tiles.length === 0 || tiles[0].y !== 0) {
		throw new Error("Screenshot tiles do not start at CSS scroll position 0");
	}
	let coveredUntil = 0;
	for (const tile of tiles) {
		if (tile.y > coveredUntil) {
			throw new Error(`Screenshot tiles leave an uncovered gap before CSS position ${tile.y}`);
		}
		coveredUntil = Math.max(coveredUntil, tile.y + tile.height);
	}
	if (coveredUntil < documentHeight) {
		throw new Error(`Screenshot tiles stop at CSS position ${coveredUntil} before ${documentHeight}`);
	}
}

async function captureTiles(page, options, tileDirectory) {
	for (let attempt = 1; attempt <= MAX_CAPTURE_PASSES; attempt += 1) {
		const prepared = await scrollThroughPage(page, options.settleMs, options.timeoutMs);
		const expectedHeight = prepared.state.scrollHeight;
		rmSync(tileDirectory, { recursive: true, force: true });
		mkdirSync(tileDirectory, { recursive: true });

		const tiles = [];
		const seenPositions = new Set();
		let requestedY = 0;
		for (let index = 0; ; index += 1) {
			await scrollToCssPosition(page, requestedY, options.timeoutMs);
			await page.waitForTimeout(options.settleMs);
			const viewportReady = await waitForViewportImages(page, Math.min(options.timeoutMs, 15_000));
			if (!viewportReady) {
				await throwForIncompleteImages(page, Math.min(options.timeoutMs, 15_000));
			}
			await throwForIncompleteImages(page, Math.min(options.timeoutMs, 15_000));

			const position = await scrollToCssPosition(page, requestedY, options.timeoutMs);
			if (seenPositions.has(position)) break;
			seenPositions.add(position);

			const state = await documentState(page);
			if (state.scrollHeight !== expectedHeight) break;
			const tilePath = join(tileDirectory, `tile-${String(index).padStart(3, "0")}.png`);
			await page.screenshot({ path: tilePath, type: "png", fullPage: false, caret: "hide" });
			const pixels = pngDimensions(tilePath);
			tiles.push({
				file: tilePath,
				y: position,
				width: state.innerWidth,
				height: state.innerHeight,
				docHeight: state.scrollHeight,
				pixelWidth: pixels.width,
				pixelHeight: pixels.height,
				capturedAt: new Date().toISOString(),
			});

			if (position + state.innerHeight >= expectedHeight) {
				const finalState = await documentState(page);
				if (finalState.scrollHeight === expectedHeight) {
					validateTileCoverage(tiles, expectedHeight);
					return { prepared, tiles };
				}
				break;
			}
			requestedY = Math.min(position + state.innerHeight, expectedHeight - state.innerHeight);
		}
	}

	throw new Error("The source document changed height while screenshot tiles were being captured");
}

function relativePath(fromDirectory, path) {
	return relative(fromDirectory, path).split("\\").join("/");
}

async function capture(options) {
	mkdirSync(dirname(options.output), { recursive: true });
	const metadataPath = metadataPathFor(options.output);
	const tileDirectory = tileDirectoryFor(options.output);
	const browser = await chromium.launch({ headless: !options.headed });

	try {
		const context = await browser.newContext({
			viewport: { width: options.width, height: options.height },
			deviceScaleFactor: 1,
			serviceWorkers: "block",
		});
		const page = await context.newPage();
		page.setDefaultTimeout(options.timeoutMs);
		page.setDefaultNavigationTimeout(options.timeoutMs);

		const response = await page.goto(options.url, { waitUntil: "domcontentloaded" });
		if (!response || response.status() >= 400) {
			throw new Error(`Source navigation failed with HTTP ${response?.status() ?? "unknown"}`);
		}
		await page.waitForLoadState("load");
		const fontsReady = await waitForFonts(page, options.timeoutMs);
		const result = await captureTiles(page, options, tileDirectory);
		const finalState = await documentState(page);

		const metadataDirectory = dirname(metadataPath);
		const metadata = {
			version: "1",
			requestedUrl: sanitizeUrl(options.url),
			finalUrl: sanitizeUrl(page.url()),
			capturedAt: new Date().toISOString(),
			viewport: {
				width: options.width,
				height: options.height,
				deviceScaleFactor: 1,
			},
			document: finalState,
			readiness: {
				fontsReady,
				documentHeightStable: result.prepared.stable,
				scrollPasses: result.prepared.passes,
				renderedImageElements: result.prepared.audit.renderedImageElements,
				loadedImageElements: result.prepared.audit.loadedImageElements,
				backgroundAndPosterAssets: result.prepared.audit.backgroundAndPosterAssets,
				loadedBackgroundAndPosterAssets: result.prepared.audit.loadedBackgroundAndPosterAssets,
				failedImages: [],
			},
			tiles: result.tiles.map((tile) => ({
				...tile,
				file: relativePath(metadataDirectory, tile.file),
			})),
		};
		writeFileSync(metadataPath, `${JSON.stringify(metadata, null, 2)}\n`);

		const stitched = spawnSync("python3", [STITCH_SCRIPT, metadataPath, options.output], {
			encoding: "utf-8",
		});
		if (stitched.error) throw stitched.error;
		if (stitched.status !== 0) {
			throw new Error(stitched.stderr.trim() || stitched.stdout.trim() || "Screenshot stitching failed");
		}
		if (!existsSync(options.output)) throw new Error("Screenshot stitcher did not create the output file");

		const outputPixels = pngDimensions(options.output);
		metadata.output = {
			file: relativePath(metadataDirectory, options.output),
			pixelWidth: outputPixels.width,
			pixelHeight: outputPixels.height,
		};
		writeFileSync(metadataPath, `${JSON.stringify(metadata, null, 2)}\n`);
		await context.close();
		return { metadataPath, metadata };
	} finally {
		await browser.close();
	}
}

async function main() {
	try {
		const options = parseArgs(process.argv.slice(2));
		const result = await capture(options);
		process.stdout.write(
			`${JSON.stringify({ output: options.output, metadata: result.metadataPath, readiness: result.metadata.readiness })}\n`,
		);
	} catch (error) {
		process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
		process.stderr.write(`${usage()}\n`);
		process.exitCode = 1;
	}
}

await main();

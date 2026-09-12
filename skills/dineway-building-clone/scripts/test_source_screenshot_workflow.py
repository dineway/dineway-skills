#!/usr/bin/env python3
"""Regression tests for the source screenshot capture workflow."""

from __future__ import annotations

import json
import subprocess
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from PIL import Image


SCRIPT_DIR = Path(__file__).resolve().parent
CAPTURE_SCRIPT = SCRIPT_DIR / "capture-source-screenshots.mjs"

# A 1x1 opaque PNG. The delayed response makes a premature capture observable.
PNG_BYTES = bytes.fromhex(
	"89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
	"0000000d49444154789c6360f8cff0000004010100cd9c7f180000000049454e44ae426082"
)


class ScreenshotFixtureHandler(BaseHTTPRequestHandler):
	def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
		path = self.path.split("?", 1)[0]
		if path == "/pixel.png":
			time.sleep(0.35)
			self.send_response(200)
			self.send_header("Content-Type", "image/png")
			self.send_header("Content-Length", str(len(PNG_BYTES)))
			self.end_headers()
			self.wfile.write(PNG_BYTES)
			return

		if path == "/missing.png":
			self.send_error(404)
			return

		if path == "/positioned":
			body = b"""<!doctype html><style>
html,body { margin:0; } body { height: 570px; padding-top:50px; box-sizing:border-box; }
#sticky { position:sticky;top:0;height:20px;background:rgb(0,0,255); }
#top { position:fixed;top:0;width:100%;height:20px;background:rgb(255,0,0); }
#bottom { position:fixed;bottom:0;width:100%;height:20px;background:rgb(0,255,0); }
</style><div id="sticky"></div><div id="top"></div><div id="bottom"></div>"""
		elif path == "/broken":
			body = b"<!doctype html><img src='/missing.png' width='40' height='40'>"
		else:
			body = b"""<!doctype html>
<meta charset="utf-8">
<style>
  html, body { margin: 0; }
  html { scroll-behavior: smooth; }
  .spacer { height: 260px; }
  img { display: block; width: 48px; height: 48px; }
</style>
<img src="/pixel.png?top" alt="top">
<div class="spacer"></div>
<img id="lazy" alt="lazy" width="48" height="48">
<div id="late"></div>
<script>
  const lazy = document.querySelector('#lazy');
  const observer = new IntersectionObserver((entries) => {
    if (!entries.some((entry) => entry.isIntersecting)) return;
    observer.disconnect();
    setTimeout(() => {
      lazy.src = '/pixel.png?lazy';
      lazy.addEventListener('load', () => {
        document.querySelector('#late').style.height = '220px';
        document.body.dataset.lazyReady = 'true';
      }, { once: true });
    }, 150);
  });
  observer.observe(lazy);
</script>"""

		self.send_response(200)
		self.send_header("Content-Type", "text/html; charset=utf-8")
		self.send_header("Content-Length", str(len(body)))
		self.end_headers()
		self.wfile.write(body)

	def log_message(self, _format: str, *_args: object) -> None:
		return


class SourceScreenshotWorkflowTests(unittest.TestCase):
	@classmethod
	def setUpClass(cls) -> None:
		cls.server = ThreadingHTTPServer(("127.0.0.1", 0), ScreenshotFixtureHandler)
		cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
		cls.thread.start()
		cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

	@classmethod
	def tearDownClass(cls) -> None:
		cls.server.shutdown()
		cls.server.server_close()
		cls.thread.join(timeout=5)

	def run_capture(self, url: str, output: Path) -> subprocess.CompletedProcess[str]:
		return subprocess.run(
			[
				"node",
				str(CAPTURE_SCRIPT),
				"--url",
				url,
				"--output",
				str(output),
				"--width",
				"320",
				"--height",
				"180",
				"--timeout-ms",
				"15000",
				"--settle-ms",
				"100",
			],
			cwd=SCRIPT_DIR.parents[2],
			capture_output=True,
			text=True,
			timeout=60,
		)

	def test_waits_for_lazy_images_and_uses_the_stable_document_height(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			output = Path(directory) / "source-desktop.png"
			result = self.run_capture(f"{self.base_url}/", output)

			self.assertEqual(result.returncode, 0, result.stderr)
			metadata = json.loads(output.with_suffix(".capture.json").read_text(encoding="utf-8"))
			self.assertTrue(metadata["readiness"]["fontsReady"])
			self.assertTrue(metadata["readiness"]["documentHeightStable"])
			self.assertEqual(metadata["readiness"]["failedImages"], [])
			self.assertEqual(metadata["readiness"]["loadedImageElements"], 2)
			self.assertGreaterEqual(metadata["document"]["scrollHeight"], 570)
			self.assertGreater(len(metadata["tiles"]), 2)
			self.assertEqual(metadata["tiles"][0]["y"], 0)

			with Image.open(output) as screenshot:
				self.assertEqual(screenshot.width, 320)
				self.assertEqual(screenshot.height, metadata["document"]["scrollHeight"])

	def test_prepared_page_requires_exact_state_and_keeps_context_for_batch_capture(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			output = Path(directory) / "prepared.png"
			program = """
import assert from 'node:assert/strict';
import { chromium } from '@playwright/test';
const { capturePreparedPage } = await import(process.env.CAPTURE_MODULE);
const browser = await chromium.launch();
try {
  const context = await browser.newContext({ viewport: { width: 320, height: 180 }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  await page.goto(process.env.FIXTURE_URL);
  const options = { url: process.env.FIXTURE_URL, expectedUrl: process.env.FIXTURE_URL, output: process.env.OUTPUT, width: 320, height: 180, settleMs: 100, timeoutMs: 15000 };
  await assert.rejects(capturePreparedPage(page, { ...options, expectedUrl: process.env.FIXTURE_URL + 'login' }), /expected source state/);
  await assert.rejects(capturePreparedPage(page, { ...options, expectedUrl: undefined }), /explicit expectedUrl/);
  await page.evaluate(() => { document.body.dataset.prepared = 'yes'; });
  await capturePreparedPage(page, options);
  assert.equal(page.isClosed(), false);
  assert.equal(await page.locator('body').getAttribute('data-prepared'), 'yes');
  await page.setViewportSize({ width: 390, height: 240 });
  await assert.rejects(capturePreparedPage(page, options), /exact viewport/);
  await capturePreparedPage(page, { ...options, width: 390, height: 240, output: process.env.OUTPUT.replace('.png', '-mobile.png') });
  const positionedUrl = process.env.FIXTURE_URL + 'positioned';
  await page.goto(positionedUrl); await page.setViewportSize({ width: 320, height: 180 });
  const styles = () => page.evaluate(() => ['sticky','top','bottom'].map(id => {
    const node = document.getElementById(id), style = getComputedStyle(node);
    return { position:style.position, top:style.top, bottom:style.bottom, visibility:style.visibility, inline:node.style.cssText };
  }));
  const before = await styles();
  const positionedOptions = { ...options, url:positionedUrl, expectedUrl:positionedUrl, output:process.env.OUTPUT.replace('.png','-positioned.png') };
  await capturePreparedPage(page, positionedOptions); assert.deepEqual(await styles(),before);
  const screenshot = page.screenshot.bind(page);
  page.screenshot = async () => { throw new Error('fixture screenshot failure'); };
  await assert.rejects(capturePreparedPage(page, positionedOptions), /fixture screenshot failure/);
  assert.deepEqual(await styles(), before); page.screenshot = screenshot;
  const retina = await browser.newContext({ viewport: { width: 320, height: 180 }, deviceScaleFactor: 2 });
  const retinaPage = await retina.newPage(); await retinaPage.goto(process.env.FIXTURE_URL);
  await assert.rejects(capturePreparedPage(retinaPage, options), /devicePixelRatio 1/);
} finally { await browser.close(); }
"""
			import os
			result = subprocess.run(
				["node", "--input-type=module", "-e", program], cwd=SCRIPT_DIR.parents[2],
				env={**os.environ, "CAPTURE_MODULE": CAPTURE_SCRIPT.as_uri(), "FIXTURE_URL": f"{self.base_url}/", "OUTPUT": str(output)},
				capture_output=True, text=True, timeout=60,
			)
			self.assertEqual(result.returncode, 0, result.stderr)
			for path, width in [(output, 320), (output.with_name("prepared-mobile.png"), 390)]:
				metadata = json.loads(path.with_suffix(".capture.json").read_text())
				self.assertTrue(metadata["readiness"]["documentHeightStable"])
				self.assertEqual(metadata["readiness"]["failedImages"], [])
				with Image.open(path) as image:
					self.assertEqual(image.size, (width, metadata["document"]["scrollHeight"]))

	def test_positioned_elements_are_not_duplicated_across_stitched_tiles(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			output = Path(directory) / "positioned.png"
			result = self.run_capture(f"{self.base_url}/positioned", output)
			self.assertEqual(result.returncode, 0, result.stderr)
			with Image.open(output) as screenshot:
				column = [screenshot.convert("RGB").getpixel((100,y)) for y in range(screenshot.height)]
				self.assertEqual(column.count((255,0,0)),20, "fixed header duplicated")
				self.assertEqual(column.count((0,0,255)),20, "sticky content duplicated")
				self.assertEqual(column.count((0,255,0)),20, "fixed footer duplicated")
				self.assertTrue(all(c == (0,255,0) for c in column[-20:]), "footer belongs at the final viewport")


	def test_fails_closed_when_a_rendered_image_is_broken(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			output = Path(directory) / "broken.png"
			result = self.run_capture(f"{self.base_url}/broken", output)

			self.assertNotEqual(result.returncode, 0)
			self.assertIn("incomplete rendered image", result.stderr.lower())
			self.assertFalse(output.exists())


if __name__ == "__main__":
	unittest.main()

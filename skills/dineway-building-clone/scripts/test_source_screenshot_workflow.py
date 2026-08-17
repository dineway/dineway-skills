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

		if path == "/broken":
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

	def test_fails_closed_when_a_rendered_image_is_broken(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			output = Path(directory) / "broken.png"
			result = self.run_capture(f"{self.base_url}/broken", output)

			self.assertNotEqual(result.returncode, 0)
			self.assertIn("incomplete rendered image", result.stderr.lower())
			self.assertFalse(output.exists())


if __name__ == "__main__":
	unittest.main()

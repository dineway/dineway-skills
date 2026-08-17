#!/usr/bin/env python3
"""Stitch browser viewport tiles using their captured CSS scroll positions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image


def resolve_tile(metadata_path: Path, value: str) -> Path:
	path = Path(value)
	if path.is_absolute():
		return path
	return metadata_path.parent / path


def stitch(metadata_path: Path, output_path: Path) -> None:
	metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
	tiles = metadata.get("tiles")
	if not isinstance(tiles, list) or not tiles:
		raise SystemExit("No screenshot tiles found")

	first_path = resolve_tile(metadata_path, tiles[0]["file"])
	with Image.open(first_path) as image:
		first = image.convert("RGB")

	css_width = tiles[0].get("width")
	if not isinstance(css_width, int) or css_width <= 0:
		raise SystemExit("The first tile has an invalid CSS width")

	scale = first.width / css_width
	document_height = tiles[-1].get("docHeight")
	if not isinstance(document_height, int) or document_height <= 0:
		raise SystemExit("The final tile has an invalid document height")

	canvas = Image.new("RGB", (first.width, round(document_height * scale)), "white")
	for tile_meta in tiles:
		tile_path = resolve_tile(metadata_path, tile_meta["file"])
		with Image.open(tile_path) as image:
			tile = image.convert("RGB")

		if tile.width != first.width:
			raise SystemExit(f"Tile width mismatch: {tile_path}")
		tile_css_width = tile_meta.get("width")
		if not isinstance(tile_css_width, int) or abs(tile.width / tile_css_width - scale) > 1e-9:
			raise SystemExit(f"Tile scale mismatch: {tile_path}")

		y = tile_meta.get("y")
		if not isinstance(y, int) or y < 0:
			raise SystemExit(f"Tile has an invalid CSS scroll position: {tile_path}")

		top = round(y * scale)
		remaining = canvas.height - top
		if remaining <= 0:
			continue
		if tile.height > remaining:
			tile = tile.crop((0, 0, tile.width, remaining))
		canvas.paste(tile, (0, top))

	output_path.parent.mkdir(parents=True, exist_ok=True)
	canvas.save(output_path, optimize=True)


def main() -> None:
	parser = argparse.ArgumentParser()
	parser.add_argument("metadata", type=Path)
	parser.add_argument("output", type=Path)
	args = parser.parse_args()
	stitch(args.metadata.resolve(), args.output.resolve())


if __name__ == "__main__":
	main()

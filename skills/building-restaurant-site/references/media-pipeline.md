# Restaurant Media Pipeline

Restaurant images must be downloaded to local files before design. Gallery is required, so select representative images that show restaurant quality, food, space, service, or atmosphere, then upload Gallery images to Dineway.

## Rules

1. Read media candidates from the enriched JSON in this order:
   - `placeDetails.placeImageList`
   - `placeDetails.photoList`
   - `placeDetails.photos`
   - `placeDetails.reviewImageList`
   - `placeDetails.extImageReviews[].imageUrls`
   - `placeDetails.menuImages`
   - `placeDetails.ugcPosts[].imageUrls`
   - `placeDetails.aiPhotoList`
   - video thumbnails or downloadable stills from `placeDetails.reviewVideoList`, `placeDetails.videoList`, `placeDetails.placeVideoList`, `placeDetails.extraVideos`, and `placeDetails.ugcPosts`
   - selected-place image fallbacks
2. Download actual image bytes to local files before Astro design implementation.
3. Put static Astro images under `public/assets/<restaurant-slug>/` and reference them in markup as `/assets/<restaurant-slug>/<file>`. Do not put browser-referenced static images in a root `assets/` directory.
4. Upload selected local files into the running Dineway site with `dineway media upload` for Gallery and any other CMS-managed image fields.
5. Use the uploaded media values in Dineway image fields.
6. Do not use remote image URLs, Google photo references, photo resource names, or API tokens in markup.
7. If a photo entry has no usable image URL, skip it and record the reason.
8. Every retained image needs specific alt text grounded in the place data and visible image context when inspected.
9. Preserve media context in the manifest when possible: source field, source review/post/menu item, author/title, review link, and intended use (`hero`, `gallery`, `menu`, `review`, `blog`, `news`, or `design-only`).

Do not treat all media equally. Menu images should primarily support Menu/Gallery, review images should support Reviews/Gallery/Blog, post media should support Blog/News/Gallery, and place images should drive hero/atmosphere/gallery decisions.

## Two-Phase Workflow

### Phase 1: Download with Quality Ranking

Download up to 20 image candidates, ranked by source priority and resolution signals. The script sorts candidates by:

1. **Source priority** — `placeImageList` (100) > `photoList` (90) > `photos` (85) > `menuImages` (75) > `reviewImageList` (70) > `extImageReviews` (65) > `ugcPosts` (50) > `aiPhotoList` (40) > video thumbnails (30) > selected-place fallbacks (20)
2. **URL resolution hints** — parsed from Google image URL size parameters (e.g. `=w1200-h800`, `=s1600`)
3. **Original order** — stable tiebreaker

After download, the script reads actual image dimensions (JPEG/PNG/WebP header parsing) and records them in the manifest alongside file size, priority score, and source path.

```bash
node skills/building-restaurant-site/scripts/restaurant_site_data.js download \
  places/PLACE_ID.json \
  --out public/assets/restaurant-slug \
  --max 20 \
  --manifest .plan/building-restaurant-site/restaurant/downloaded-media.json
```

The manifest records downloaded files with their dimensions, priority, and resolution hints, plus skipped candidates.

### Phase 2: Agent Curation

After downloading, the agent inspects the actual image content by viewing the downloaded files. Select 8-10 images based on:

- **Visual quality** — sharp, well-lit, properly composed
- **Content diversity** — cover food, interior, exterior, atmosphere, service
- **Resolution** — prefer higher resolution images (check `width`, `height`, `size` in manifest)
- **Intended use** — ensure coverage for hero, gallery, menu, review, and blog needs

Mark selected images using the `select` subcommand:

```bash
node skills/building-restaurant-site/scripts/restaurant_site_data.js select \
  .plan/building-restaurant-site/restaurant/downloaded-media.json \
  --pick 1,3,5,6,8,10,12,15 \
  --out .plan/building-restaurant-site/restaurant/selected-media.json
```

The `--pick` flag accepts comma-separated 1-based indices matching the `index` field in the manifest. The output manifest marks each item with `selected: true/false`.

### Phase 3: Upload for CMS-Managed Content

Start the local Dineway dev server first if needed:

```bash
bgproc start -n devserver -w -- pnpm dev
```

Then upload. When the manifest contains `selected` flags, only selected items are uploaded:

```bash
node skills/building-restaurant-site/scripts/restaurant_site_data.js upload \
  .plan/building-restaurant-site/restaurant/selected-media.json \
  --url http://localhost:4321 \
  --out .plan/building-restaurant-site/restaurant/uploaded-media.json
```

If no items have the `selected` flag (backwards compatible), all items are uploaded.

The upload output includes `mediaValue` objects suitable for Dineway content:

```json
{
	"provider": "local",
	"id": "01...",
	"filename": "restaurant-photo-01.jpg",
	"mimeType": "image/jpeg",
	"width": 1200,
	"height": 800,
	"alt": "Restaurant name dining room photo",
	"meta": {
		"storageKey": "01....jpg"
	}
}
```

Use those objects in image fields and JSON gallery blocks. Render Dineway-managed images with `Image` from `dineway/ui`. Static Astro promotional pages may keep using `/assets/...` paths backed by files in `public/assets/...`.

## Fallbacks

- If there are no downloadable images, record the blocker and ask for restaurant photos before final delivery because Gallery is required. Do not use fake or stock imagery.
- If only one representative image downloads, still create Gallery with that image and clear source-grounded captioning.
- Gallery is required. Use the strongest available downloaded images, but do not pad it with low-quality or irrelevant images.

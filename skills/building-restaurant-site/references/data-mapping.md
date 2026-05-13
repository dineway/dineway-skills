# Enriched Place Data Mapping

The source of truth is the JSON saved by `enrich-place-details`, normally `places/${placeId}.json`. Prefer `placeDetails`, then fall back to `selectedPlace`, then search/candidate summaries. Do not use legacy payload field names unless handling a compatibility fixture.

## Required Identity Fields

Map fields conservatively:

| Site concept     | Preferred enriched fields                                                                                                                |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Place id         | `placeDetails.placeId`, `selectedPlace.placeId`, `selectedPlace.id`, `search.selectedCandidate.placeId`, `search.selectedCandidate.id`   |
| Name             | `placeDetails.displayName.text`, `placeDetails.displayName`, `placeDetails.name`, `selectedPlace.displayName.text`, `selectedPlace.name` |
| Address          | `placeDetails.formattedAddress`, `placeDetails.shortFormattedAddress`, `selectedPlace.formattedAddress`, `selectedPlace.address`         |
| Phone            | `placeDetails.internationalPhoneNumber`, `placeDetails.nationalPhoneNumber`, `placeDetails.formatted_phone_number`                       |
| Rating           | `placeDetails.rating`, `selectedPlace.rating`                                                                                            |
| Review count     | `placeDetails.userRatingCount`, `placeDetails.user_ratings_total`, `selectedPlace.userRatingCount`                                       |
| Google Maps link | `placeDetails.googleMapsUri`, `placeDetails.url`, `selectedPlace.googleMapsUri`                                                          |
| Website          | `placeDetails.websiteUri` only if present                                                                                                |
| Categories       | `placeDetails.primaryCategories`, `placeDetails.categories`, `placeDetails.types`, `selectedPlace.types`                                 |
| Coordinates      | `placeDetails.latlon`, `placeDetails.location`, `placeDetails.geometry.location`, `selectedPlace.geometry.location`                      |
| Opening hours    | `placeDetails.regularOpeningHours.weekdayDescriptions`, `placeDetails.currentOpeningHours.weekdayDescriptions`                           |
| Reviews          | `placeDetails.reviews`                                                                                                                   |
| Images           | `placeDetails.photos`, `placeDetails.photoList`, `placeDetails.placeImageList`, `placeDetails.aiPhotoList`, selected-place fallbacks     |
| Menu             | `placeDetails.menuList`, `placeDetails.menuImages`                                                                                        |
| UGC posts        | `placeDetails.ugcPosts`                                                                                                                   |
| Other posts      | `placeDetails.posts`, `placeDetails.postList`, `placeDetails.placePostList`, selected-place post fallbacks                               |
| Videos           | `placeDetails.videos`, `placeDetails.videoList`, `placeDetails.placeVideoList`, `placeDetails.extraVideos`, selected-place fallbacks     |
| Review media     | `placeDetails.extImageReviews`, `placeDetails.reviewImageList`, `placeDetails.reviewVideoList`                                           |

## Useful Enriched Signals

Use these only when present:

- `businessStatus`
- `priceLevel`
- `placeType`, `categories`, `primaryCategories`, `primaryTypeDisplayName`, `googleMapsTypeLabel`
- `city`, `state`, `country`, `countryRegion`, `timeZone`, `utcOffsetMinutes`
- `postalAddress`, `addressComponents`, `addressDescriptor.areas`, `addressDescriptor.landmarks`, `viewport`
- `googleMapsLinks.placeUri`, `googleMapsLinks.photosUri`, `googleMapsLinks.reviewsUri`, `googleMapsLinks.directionsUri`, `googleMapsLinks.writeAReviewUri`
- `servesVegetarianFood`
- `dineIn`, `takeout`, `delivery`, `reservable`, `servesLunch`, `servesDinner`, `goodForGroups`, `restroom`, `goodForWatchingSports`, `liveMusic`, `pureServiceAreaBusiness`
- `paymentOptions.acceptsNfc`, `paymentOptions.acceptsDebitCards`, `paymentOptions.acceptsCreditCards`, `paymentOptions.acceptsCashOnly`
- `accessibilityOptions`
- `regularOpeningHours`
- `currentOpeningHours`
- `reviews[].text`, `reviews[].rating`, `reviews[].authorAttribution`, `reviews[].relativePublishTimeDescription`
- `numberReviews` when present as a separate enriched review count signal
- menu fields such as `menuList[].title`, `menuList[].items[].subTitle`, `menuList[].items[].desc`, `menuList[].items[].price`, `menuImages[]`
- post fields such as `ugcPosts[].text`, `title`, `imageUrls`, `videoUrls`, `videos`, `timeUtc`, `postUrl`, `userProfile`, `numLikes`, or `numComments`
- video fields such as title, description, thumbnail, transcript, caption, video URL, review link, or source URL when present
- review media fields such as `extImageReviews[].imageUrls`, `reviewImageList[].imageUrl`, `reviewVideoList[].videoUrl`, and their review/source links

These fields can shape content and page structure, but do not turn them into unsupported claims. For example, `takeout: true` supports a takeaway note; missing `delivery` means omit delivery claims.

## Data Utilization Matrix

Before design or content seeding, create `Data Utilization Matrix` in `.plan/<restaurant-slug>/findings.md`. For each present field family, record one of these outcomes:

- **Public page copy:** useful guest-facing facts for Home, Contact, About/Snapshot, CTA labels, review highlights, or visit guidance.
- **CMS content source:** raw material for Blog, News, Menu, Reviews, or Gallery.
- **Media source:** image/video candidates to download, upload, caption, or use as design inputs.
- **Local SEO/JSON-LD:** structured data, page metadata, internal links, map links, and location signals.
- **Design direction:** visual tone, layout density, color/accent choices, image emphasis, or section priority.
- **Internal guardrail:** fields that prevent unsupported claims, such as false service flags or missing hours.
- **Not used:** only allowed with a specific reason, such as empty value, unusable media URL, duplicate signal, not customer-safe, or unsupported by Dineway/runtime.

Do not force every field into visible copy. "Use" includes SEO, internal guardrails, media selection, and CMS source planning when that is the correct boundary.

## Field Family Usage Rules

- **Identity and status:** use `displayName`, category/type labels, `businessStatus`, city/country, and short/formatted address for hero, metadata, navigation context, and JSON-LD. Do not promote a closed/non-operational place as open.
- **Address and local context:** use `postalAddress`, `addressComponents`, `addressDescriptor.areas`, and `addressDescriptor.landmarks` to improve Contact, "getting here" copy, local SEO, and nearby-area phrasing. Landmarks should be concise guest guidance, not raw descriptor dumps.
- **Coordinates and viewport:** use `latlon`/`location` for maps links and JSON-LD. Use `viewport` only for map framing or internal context; do not render bounding coordinates as public copy.
- **Ratings and review counts:** use `rating`, `userRatingCount`, and `numberReviews` for trust modules and JSON-LD when consistent. If counts differ, prefer the clearest primary count and record the discrepancy internally.
- **Reviews:** use full review text, rating, author attribution, publish time, and links to curate Reviews, Blog themes, Menu support, and trust snippets. Keep public quotes short and attributed; do not expose flag links.
- **Extended review media:** use `extImageReviews`, `reviewImageList`, and `reviewVideoList` to pair real customer themes with Gallery, Reviews, Blog, and visual proof. Download usable media first; never render remote review media URLs directly.
- **Menu data:** use `menuList` sections/items and `menuImages` for the Menu CMS column. Preserve exact item names and source-backed preparation notes. Do not invent prices when `price` is empty.
- **UGC posts:** treat `ugcPosts` as a primary enriched field family when present. Use text, title, timestamp, image/video media, post URL, user profile, likes, and comments for Blog themes, News/update-style ideas, Gallery/media selection, and review-reputation context. Do not collapse it into generic post counts in planning.
- **Other posts:** use `posts`, `postList`, and `placePostList` as additional Blog/News source material. Do not imply official announcements unless the post content supports that framing.
- **Videos:** use `videoList`, `placeVideoList`, `extraVideos`, `reviewVideoList`, and post video fields as design/media inputs and Blog/Gallery/Reviews source context. If video cannot be downloaded or embedded safely, use it as internal content context and record that choice.
- **Place images:** use `photos`, `photoList`, `placeImageList`, and `aiPhotoList` for hero, atmosphere sections, Gallery, and image-informed visual direction. Inspect and select representative images instead of using the first N blindly.
- **Service flags:** use positive flags such as dine-in, takeout, reservable, lunch, dinner, groups, restroom, delivery, or vegetarian support for guest guidance only when true. Use false or missing flags as guardrails against claims.
- **Payment and accessibility:** use payment and accessibility options in Contact/Visit sections when customer-safe and useful. Do not turn internal booleans into awkward raw labels.
- **Map action links:** use `googleMapsLinks.directionsUri` for "Get directions", `reviewsUri` for "Read reviews", `photosUri` for gallery/map-photo context, and `writeAReviewUri` only when a review CTA is appropriate. Prefer `placeUri`/`googleMapsUri` as the canonical same-as link.
- **Time zone and UTC offset:** use for interpreting post/review times or operational context. Do not render raw offsets unless it helps guests.
- **Icon/category colors:** `categoryIcon`, `iconMaskBaseUri`, and `iconBackgroundColor` may inform subtle design accents, but do not use remote icon resources as primary brand assets.

## Content Planning Rules

- Write from verifiable data. Summaries may synthesize review themes, categories, ratings, address context, and service flags.
- Blog, News, Menu, Reviews, and Gallery are required columns. Use source density to control depth, not whether the column exists.
- Blog content uses review themes plus real post/video material. News uses menu-update signals and real post material. Menu uses structured menu data when present plus review-backed dish/flavor/service themes.
- Required columns should prioritize enriched data in this order when present: Menu from `menuList/menuImages`, Reviews from `reviews/extImageReviews/reviewImageList/reviewVideoList`, Gallery from all downloaded representative media, Blog from reviews/posts/videos, and News from posts/menu-update signals.
- When `ugcPosts` is present, Blog and News planning must use at least one customer-safe theme or item from it, unless every `ugcPosts` entry fails the customer visibility gate. Its images and videos must be considered for Gallery or content media before falling back to generic place photos.
- Never fabricate menu items, opening hours, awards, chef names, reservations, social accounts, or FAQs.
- If a field is missing, omit that field or schema property. Do not omit the required Blog, News, Menu, Reviews, or Gallery columns.
- Use exact NAP data for contact sections.
- Use review text for themes, but keep quotes short and attributed.
- Use post/video material as source context, but do not imply recency, new launches, events, or menu changes unless the source proves them.
- Prefer page count based on available data, not a fixed template.

## Optional Summary Command

```bash
node skills/building-restaurant-site/scripts/restaurant_site_data.js \
  summarize places/PLACE_ID.json \
  --out .plan/building-restaurant-site/restaurant/site-summary.json
```

The summary is a planning aid. Inspect the original JSON before final decisions.

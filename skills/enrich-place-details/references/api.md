# Dineway Hosted Places API Notes

Observed against `https://api.dineway.ai` on 2026-05-13. Do not commit live tokens.

## Create Shadow User

`POST /api/auth/users/shadow`

Body:

```json
{
  "placeId": "ChIJs5ydyTiuEmsR0fRSlU0C7k0",
  "language": "en"
}
```

Observed top-level response keys:

- `accessToken`
- `refreshToken`
- `user`
- `isNewUser`
- `quotas`
- `tier`

Observed `user` keys:

- `id`
- `email`
- `emailVerified`
- `isAnonymous`
- `metadata`
- `profile`
- `providers`
- `createdAt`
- `updatedAt`

Arbitrary fake place ids were rejected during probing with `PLACES_UPSTREAM_UNAVAILABLE`, so the script uses a configurable bootstrap place id when the user did not provide a valid place id, then rebinds to the selected result.

## Refresh Token

`POST /api/auth/refresh?client_type=server`

Body:

```json
{
  "refreshToken": "..."
}
```

Observed response keys:

- `accessToken`
- `refreshToken`
- `user`

## Search Places

`POST /api/places/search`

Headers:

- `Content-Type: application/json`
- `Authorization: Bearer <accessToken>`

Body:

```json
{
  "textQuery": "Peace Harmony in Sydney, Australia"
}
```

Observed response keys:

- `places`

Observed `places[]` candidate keys can include:

- `id`
- `displayName`
- `formattedAddress`
- `priceLevel`

`displayName` is an object such as:

```json
{
  "text": "Peace Harmony",
  "languageCode": "en"
}
```

The candidate id is the Google-style place id used for the final detail request.

## Fetch Place Details

`GET /api/places/{placeId}`

Headers:

- `Authorization: Bearer <accessToken>`

Observed detail response is a top-level place object, not nested under `data`. Observed keys include:

- `placeId`
- `displayName`
- `formattedAddress`
- `shortFormattedAddress`
- `internationalPhoneNumber`
- `nationalPhoneNumber`
- `rating`
- `userRatingCount`
- `websiteUri`
- `googleMapsUri`
- `businessStatus`
- `categories`
- `primaryCategories`
- `priceLevel`
- `regularOpeningHours`
- `currentOpeningHours`
- `reviews`
- `photos`
- `photoList`
- `placeImageList`
- `latlon`
- `city`
- `state`
- `country`
- `timeZone`
- `servesVegetarianFood`
- `dineIn`
- `takeout`
- `delivery`
- `reservable`

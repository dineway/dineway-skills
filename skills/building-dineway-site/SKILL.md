---
name: building-dineway-site
description: Build and customize Dineway Agentic Web sites. Use when creating pages, defining collections, writing seed files, querying content, rendering Portable Text, setting up menus/taxonomies/widgets, configuring deployment, or any task involving a Dineway-powered Astro site. Assumes basic Astro knowledge but provides all Dineway-specific patterns.
---

# Building a Dineway Site

Dineway is an Agentic Web builder. It stores schema in the database (not in code), serves content via live content collections, and provides a full admin UI at `/_dineway/admin`. Sites are standard Astro projects with the `dineway` integration.

## Common Gotchas

These are the things that silently break sites. Know them before you start.

1. **Image fields are objects, not strings.** `post.data.featured_image` is `{ id, src, alt }`. Writing `<img src={post.data.featured_image} />` renders `[object Object]`. Use `<Image image={post.data.featured_image} />` from `"dineway/ui"`.

2. **`entry.id` vs `entry.data.id` are different things.** `entry.id` is the slug (use in URLs). `entry.data.id` is the database ULID (use for `getEntryTerms`, `Comments`, and other API calls that need the real ID). Mixing them up causes silent empty results.

3. **Taxonomy names must match the seed exactly.** If your seed defines `"name": "category"`, you must query `getTerm("category", slug)` -- not `"categories"`. Wrong name = empty results, no error.

4. **Always pass `cacheHint` to `Astro.cache.set()`.** Every query returns a `cacheHint`. Call `Astro.cache.set(cacheHint)` on every page that queries content, or cache invalidation won't work when editors publish changes.

5. **No `getStaticPaths` for CMS content.** Dineway content is dynamic. Pages must be server-rendered (`output: "server"` in `astro.config.mjs`).

6. **Discovery endpoints are part of "done".** Production sites must resolve a public origin via `siteUrl` or `DINEWAY_SITE_URL`, layouts must render `DinewayHead`, every routable collection must include `supports: ["seo"]` and `urlPattern`, and the site must expose `/robots.txt`, `/sitemap.xml`, and `/schemamap.xml`.

## File Structure

Every Dineway site has these key files:

```
my-site/
├── astro.config.mjs          # Astro config with dineway() integration
├── src/
│   ├── live.config.ts         # Dineway loader registration (boilerplate)
│   ├── pages/                 # Astro pages (all server-rendered)
│   ├── layouts/               # Layout components
│   └── components/            # Reusable components
├── seed/
│   └── seed.json              # Schema + demo content
├── dineway-env.d.ts          # Generated types (from `dineway types`)
└── package.json
```

## Workflow

### 1. Configure the project

Read **[references/configuration.md](references/configuration.md)** for `astro.config.mjs`, `live.config.ts`, Node deployment and reverse-proxy setup, storage choices, and type generation.

For production builds, set `siteUrl` in `astro.config.mjs` or `DINEWAY_SITE_URL` in the environment. Register `seoGraphPlugin()` and add a public `src/pages/schemamap.xml.ts` route that proxies `/_dineway/api/plugins/seo-graph/schema/map`.

### 2. Design the schema

Read **[references/schema-and-seed.md](references/schema-and-seed.md)** for collection definitions, field types, taxonomies, menus, widget areas, sections, bylines, and the complete seed file format.

Every collection that has public detail pages must include `supports: ["seo"]` and a `urlPattern` matching the Astro route, such as `/posts/{slug}` or `/{slug}`.

### 3. Build the pages

Read **[references/querying-and-rendering.md](references/querying-and-rendering.md)** for content queries, Portable Text rendering, the Image component, visual editing attributes, caching, and common page patterns (list, detail, taxonomy archive, RSS, search, 404).

### 4. Wire up site features

Read **[references/site-features.md](references/site-features.md)** for site settings, navigation menus, taxonomies, widget areas, search, SEO meta, comments, and page contributions.

All layouts must create a public page context and render `DinewayHead`; content-backed pages must pass `content: { collection, id, slug }` so SEO and schema plugins know which entry is being rendered.

### 5. Create the seed file

Write `seed/seed.json` with collections, fields, taxonomies, menus, widgets, and sample content. Validate with:

```bash
npx dineway seed seed/seed.json --validate
```

### 6. Run and verify

```bash
npx dineway dev          # Start dev server (runs migrations + seeds, and generates types)
```

The admin UI is at `http://localhost:4321/_dineway/admin`.

Before final delivery, validate discovery endpoints:

```bash
for path in /robots.txt /sitemap.xml /schemamap.xml; do
	curl -fsSI "http://localhost:4321$path" >/dev/null
done
```

## Quick API Cheat Sheet

```typescript
// Content (entries have .data.byline and .data.bylines eagerly loaded)
import { getDinewayCollection, getDinewayEntry } from "dineway";
const { entries, nextCursor, cacheHint } = await getDinewayCollection("posts", {
	limit: 10,
	cursor,
	orderBy: { published_at: "desc" },
});
const { entry: post, cacheHint } = await getDinewayEntry("posts", slug);

// Site features
import {
	getSiteSettings,
	getMenu,
	getTaxonomyTerms,
	getTerm,
	getEntryTerms,
	getEntriesByTerm,
	getWidgetArea,
	search,
	getSection,
	getSeoMeta,
} from "dineway";

// Bylines (standalone queries -- usually not needed since entries have bylines attached)
import { getEntryBylines, getBylinesForEntries, getByline, getBylineBySlug } from "dineway";

// UI components
import {
	PortableText,
	Image,
	Comments,
	CommentForm,
	WidgetArea,
	DinewayHead,
	DinewayBodyStart,
	DinewayBodyEnd,
} from "dineway/ui";
import LiveSearch from "dineway/ui/search";

// Page context (for plugin contributions)
import { createPublicPageContext } from "dineway/page";
```

## Plugins

Dineway supports plugins for extending the CMS with hooks, storage, settings, admin UI, API routes, and custom Portable Text block types. Consider a plugin when you need to:

- React to content lifecycle events (e.g., send a notification on publish, sync to an external service)
- Add custom admin pages or dashboard widgets
- Add custom block types to the Portable Text editor (e.g., embedded maps, code playgrounds, CTAs)
- Provide a reusable service (e.g., analytics, forms, comments via a third-party provider)

Plugins are registered in `astro.config.mjs`:

```javascript
import { seoGraphPlugin } from "@dineway-ai/plugin-seo-graph";

dineway({
	database: sqlite({ url: "file:./data.db" }),
	storage: local({ directory: "./uploads", baseUrl: "/_dineway/api/media/file" }),
	plugins: [seoGraphPlugin(), myPlugin()],
}),
```

**To build a plugin, load the `creating-plugins` skill** (in `.agents/skills/creating-plugins/`). It covers plugin anatomy, hooks, storage, admin UI, API routes, Portable Text blocks, capabilities, and the full `definePlugin()` API.

## Reference Documents

| File                                                                         | Contents                                                            |
| ---------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| [references/configuration.md](references/configuration.md)                   | Project setup, astro.config, live.config, deployment, types         |
| [references/schema-and-seed.md](references/schema-and-seed.md)               | Collections, fields, taxonomies, menus, widgets, seed format        |
| [references/querying-and-rendering.md](references/querying-and-rendering.md) | Content APIs, PortableText, Image, caching, page patterns           |
| [references/site-features.md](references/site-features.md)                   | Settings, menus, widgets, search, SEO, comments, page contributions |

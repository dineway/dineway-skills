---
name: dineway-building-clone
description: Reverse-engineer and rebuild one or more website URLs as pixel-faithful, CMS-backed Dineway Agentic Web sites. Extract real assets, CSS, content, responsive behavior, and interactions section-by-section; discover one same-origin link layer from each explicitly supplied URL; model editable content in Dineway settings, menus, collections, sections, and seed data; and dispatch focused builders from auditable specifications. Use whenever the user asks to clone, replicate, rebuild, reverse-engineer, copy, or migrate a website into Dineway or Astro.
---

# Build a Website Clone as a Dineway Site

Reverse-engineer the explicitly supplied source URLs and rebuild them as a pixel-faithful Dineway Site.

Treat this as a foreman workflow, not a two-phase inspect-then-build handoff. Inspect each section, write its specification to disk, and dispatch a focused builder as soon as the shared foundation is ready. Keep extraction meticulous and every implementation decision auditable.

## Scope Defaults

Unless the user overrides them, use these defaults:

- **Fidelity:** Pixel-faithful colors, spacing, typography, motion, interactions, and responsive behavior
- **Discovery:** Each explicit URL plus one same-origin link layer discovered directly from each explicit page
- **In scope:** Visual layout, component structure, interactions, responsive design, source content, source assets, Astro SSR routes, and Dineway-managed editable content
- **Out of scope:** Reproducing the source backend, source authentication, payments, real-time services, inaccessible private content, SEO strategy rewrites, and accessibility audits
- **Dineway boundary:** Astro owns presentation and interaction; Dineway owns editable identity, navigation, editorial copy, editorial media, and repeatable content
- **Customization:** None; emulate the source unless the user requests changes

Dineway's required SEO and discovery plumbing remains in scope even though an SEO strategy rewrite is not.

## URL Discovery, Output Isolation, and Route Preservation

Treat every planned source URL as durable output, never as permission to replace earlier work.

### Explicit URLs and one-hop discovery

Parse one or more explicit HTTP(S) URLs from the request. For each explicit URL:

1. Preserve the explicit URL, including a meaningful query or fragment when it represents a visible state.
2. Open that explicit page with browser automation and collect its rendered anchor destinations.
3. Add each unique same-origin HTML pathname as a discovered page after removing its query and fragment.
4. Exclude `mailto:`, `tel:`, `javascript:`, downloads and non-HTML assets, source admin/auth/account routes, search results, and pagination routes.
5. Do not collect links from discovered pages. Discovered pages are build targets, not new crawl roots.

Deduplicate by normalized origin and pathname. Query or fragment variants that share a pathname share a destination route; document their state behavior instead of creating conflicting files. Ignore cross-origin links unless the user explicitly supplied that origin as another target.

### Site and page keys

Choose a `<site-root>` before extraction. Use the current directory only when it is already a Dineway Site or an empty approved target.

Assign each origin and page:

- `<site-key>`: readable normalized origin, including a non-default port, plus the first 8 lowercase hex characters of SHA-256 over the normalized origin
- `<page-key>`: segment-preserving readable pathname plus the first 8 lowercase hex characters of SHA-256 over the normalized pathname and any explicit stateful query/fragment; use `root-<hash>` for `/`
- Origin plan: `<site-root>/docs/research/<site-key>/OUTPUT_PLAN.md`
- Dineway model: `<site-root>/docs/research/<site-key>/DINEWAY_CONTENT_MODEL.md`
- Page research: `<site-root>/docs/research/<site-key>/<page-key>/`
- Screenshots: `<site-root>/docs/design-references/<site-key>/<page-key>/`
- Components: `<site-root>/src/components/sites/<site-key>/<page-key>/`
- Same-site shared components: `<site-root>/src/components/sites/<site-key>/shared/`
- Decorative assets: `<site-root>/public/sites/<site-key>/<page-key>/`
- Same-site shared decorative assets: `<site-root>/public/sites/<site-key>/shared/`
- An exact Astro SSR route or a route-family entry rendered through a dynamic Astro route

Record whether every planned page is explicit or discovered and, for discovered pages, its explicit parent URL. Verify every route, artifact directory, screenshot directory, component directory, asset directory, content slug, collection URL pattern, and downloader filename is unique or intentionally shared.

### Astro routing defaults

- For the first root clone in an untouched blank scaffold, replace `src/pages/index.astro` so the clone remains at `/`.
- Preserve every other normalized pathname with an exact file-based Astro route, such as `/docs/intro` at `src/pages/docs/intro.astro`, or a dynamic family such as `src/pages/posts/[slug].astro`.
- Treat literal brackets and other Astro route syntax in a source pathname as literals and encode the filesystem segment safely; verify the built URL before completion.
- Inspect all existing files under `src/pages/` before writing. Never replace a non-scaffold route, component tree, research artifact, screenshot, asset namespace, collection, or seed entry without explicit approval.
- If a destination route or Dineway content identity already exists, stop and ask whether to update, remap, or skip it.
- Different origins should use separate Dineway Site roots unless the user explicitly approves one combined installation with route-scoped styles, settings, menus, and content models.

## Pre-Flight

1. **Require browser automation.** Use an available Chrome, Playwright, Browserbase, Puppeteer, or agent-browser capability; prefer Chrome when several are available. If no browser automation is available, ask the user how to connect one.
2. **Load Dineway guidance.** Load `$dineway-building-site` and follow its current configuration, schema/seed, querying/rendering, and site-feature references. Do not copy those references into this skill.
3. **Validate targets.** Normalize every explicit URL, verify it is accessible, then perform the one-hop discovery pass only on explicit pages.
4. **Choose the site root.** A Dineway Site has a Dineway dependency, `astro.config.mjs`, and `src/live.config.ts`.
   - If the approved root is empty, scaffold the current blank Dineway template with `npm create dineway@latest . -- --template blank --pm pnpm --install --yes`.
   - If the root is non-empty and is not a Dineway Site, ask for an empty or prepared root. Never use a force-overwrite flag.
5. **Verify the baseline.** Run `pnpm typecheck` and `pnpm build`. Inventory routes, components, seed/schema, research, screenshots, and public assets. Distinguish untouched scaffold files from user-authored work.
6. **Write the output plan.** List every explicit and discovered URL, parent URL, `<site-root>`, keys, destination route, route family, collection/entry mapping, artifact paths, and shared foundation file that must change. Resolve collisions before editing.
7. **Create only planned namespaces.** Use unique downloader names such as `scripts/download-assets-<site-key>-<page-key>.mjs`.
8. **Build shared foundations sequentially.** For multiple pages from one origin, finish the origin's design tokens and Dineway content model before dispatching page/component builders.

## Guiding Principles

### 1. Completeness beats speed

Every builder must receive the screenshot, exact computed CSS, local asset paths, source text, component structure, responsive behavior, interaction states, and Dineway content contract. If a builder has to guess anything — a color, a font size, a padding value, a Dineway field name — you have failed at extraction. Take the extra minute to extract one more property rather than shipping an incomplete brief.

### 2. Small tasks produce exact results

When an agent gets "build the entire features section," it glosses over details — it approximates spacing, guesses font sizes, and produces something "close enough" but clearly wrong. When it gets a single focused component with exact CSS values and a clear Dineway content contract, it nails it every time.

Give one builder a simple section or 1-2 sub-components. Split a complex section with 3 or more independently styled/interactive sub-components into focused component tasks plus a wrapper task.

**Complexity budget rule:** If a builder prompt exceeds roughly 150 lines of specification content, the section is too complex for one agent. Break it into smaller pieces. This is a mechanical check — do not override it with "but it's all related."

### 3. Use real content and real assets

Extract exact source text, images, videos, SVGs, alt text, labels, and states. Do not turn the clone into a generic mockup. Inspect layered compositions for every foreground, background, mask, and overlay.

Classify every asset:

- **Decorative/presentation asset:** Store under the namespaced `public/sites/` root and reference it from Astro/CSS.
- **Editable editorial media:** Ingest through Dineway seed `$media` or Dineway media tooling, model it as an image field, and render the returned object with `Image` from `dineway/ui`.
- **Logo/favicon/site identity:** Model it in Dineway site settings while retaining an auditable source copy when possible.

### 4. Build the foundation first

Do not dispatch component builders until the origin's design tokens, font strategy, shared layout, route plan, Dineway content model, seed/schema, generated types, shared assets, and shared components are stable.

### 5. Extract appearance and behavior

For every component, capture exact computed styles and what changes on scroll, hover, click, resize, or time. Record the trigger, both states, and transition duration/easing. Detect scroll snapping, sticky regions, parallax, viewport reveals, carousels, modals, dropdowns, tabs, and smooth-scroll libraries.

### 6. Identify the interaction model before building

This is the single most expensive mistake in cloning: building a click-based UI when the original is scroll-driven, or vice versa. Getting this wrong means a complete rewrite, not a CSS tweak. A section with a sticky sidebar and scrolling content panels is fundamentally different from a tabbed interface where clicking switches content.

Before writing any builder prompt for an interactive section, definitively answer: **Is this section driven by clicks, scrolls, hovers, time, or some combination?**

How to determine this:

1. **Do not click first.** Scroll through the section slowly and observe if things change on their own as you scroll.
2. If they do, it is scroll-driven. Extract the mechanism: `IntersectionObserver`, `scroll-snap`, `position: sticky`, `animation-timeline`, or JS scroll listeners.
3. If nothing changes on scroll, then click and hover to test for click-driven or hover-driven interactivity.
4. Document the interaction model explicitly in the component spec: "INTERACTION MODEL: scroll-driven with IntersectionObserver" or "INTERACTION MODEL: click-to-switch with opacity transition."
5. Record the actual implementation mechanism: CSS, IntersectionObserver, scroll listener, sticky positioning, animation timeline, or a client-side island.

### 7. Extract every state

Capture every tab/pill state, scrolled/unscrolled header state, hover/focus state, expanded/collapsed state, and responsive state. For each state record content, assets, styles, trigger, transition, and whether Astro can render it statically or a client island is necessary.

### 8. Specifications are the source of truth

Write one component specification under the page research root before dispatch. Inline the entire specification in the builder prompt so the builder never relies on hidden context or memory.

### 9. The Dineway build must remain valid

Every builder runs `pnpm typecheck` for its worktree or assigned surface. After each integration run `pnpm typecheck` and `pnpm build`. Never accept a broken intermediate merge.

## Phase 1: Reconnaissance

Navigate to every explicit and discovered target with browser automation. Research discovered pages, but never extract new crawl targets from them.

### Screenshots

- Capture full-page screenshots at desktop (1440px) and mobile (390px).
- Save them under the page's namespaced screenshot root.
- Later add section-specific screenshots for every component specification.

### Global extraction

Extract and record:

- **Fonts:** Inspect `<link>` tags and `@font-face` rules for hosted or self-hosted fonts. Check computed `font-family` on key elements (headings, body, labels, code). Document every family, weight, and style actually used. For Astro, configure fonts using `@fontsource` packages, local `@font-face` declarations in a global stylesheet, or `<link rel="preload">` in the layout head. When multiple cloned origins require incompatible font stacks, scope each set under a site wrapper class or use Astro's built-in scoped `<style>` within the site's layout rather than polluting the global scope.
- **Colors:** Extract the site's color palette from computed styles across the page. Document semantic use (background, foreground, primary, accent, muted, border, etc.). Merge only truly shared tokens into the site stylesheet as CSS custom properties; scope page/site-specific tokens beneath a wrapper class. In an approved combined multi-site app, use a site wrapper or Astro scoped styles rather than replacing another site's global palette.
- **Favicons and metadata:** Download exact assets and map editable identity into Dineway settings.
- **Global UI behavior:** Scrollbars, scroll snap, keyframes, overlays, filters, theme changes, and smooth-scroll libraries (Lenis, Locomotive Scroll — check for `.lenis` class or custom scroll container wrappers).
- **Content families:** Repeated page shapes, editorial fields, taxonomy signals, navigation structures, and embedded repeaters that must become Dineway-managed data.

### Mandatory interaction sweep

Perform this after master screenshots and before component extraction:

- **Scroll:** Move slowly from top to bottom. Record header changes, reveals, sticky/snap behavior, active-section changes, parallax, and thresholds.
- **Click:** Activate every visible button, tab, pill, link, card, accordion, menu, and modal control. Capture each state.
- **Hover/focus:** Test links, cards, buttons, images, navigation, and controls. Record exact property changes and transitions.
- **Responsive:** Test 1440px, 768px, and 390px. Record layout changes and approximate breakpoints.

Save the findings to `<page-research>/BEHAVIORS.md`.

### Page topology

Map every section top-to-bottom and document:

- Visual order
- Fixed/sticky overlays versus flow content
- Scroll containers, columns, and z-index layers
- Cross-section dependencies
- Each section's interaction model
- Its content source: settings, menu, collection entry, section, embedded JSON/repeater, or static decorative data

Save this to `<page-research>/PAGE_TOPOLOGY.md`.

### Dineway content topology

Group pages by common public parent path and data shape. Write `<site-research>/DINEWAY_CONTENT_MODEL.md` using these rules:

- Put site title, tagline, logo, favicon, and social identity in settings.
- Put primary/footer navigation in named menus.
- Use a dedicated collection for every repeated public route family, with the source's public parent path and `{slug}` in `urlPattern`.
- Root-level editorial pages may share a `pages` collection with `urlPattern: "/{slug}"`.
- Nested editorial pages use a parent-specific collection such as `/docs/{slug}` or `/docs/guides/{slug}` so the public route remains exact.
- Add `supports: ["seo"]` to every public routable collection and include `drafts`, `revisions`, or `search` when the source behavior requires them.
- Use non-routable collections or Dineway sections for editable homepage/embedded blocks that do not have independent detail routes.
- Use typed fields for stable structure, `portableText` for rich editorial bodies, `image` for editorial images, and `json` only for genuine structured repeaters that do not deserve independent entries.
- Seed exact source entries as published content. Do not invent filler when source content exists.

Record every source page, destination route, collection, slug, field mapping, menu item, setting, and media classification.

## Phase 2: Dineway Foundation Build

Build the origin's shared foundation yourself; do not delegate files shared by multiple builders.

1. Configure or preserve Astro SSR, the Dineway integration, database/storage, the SEO Graph plugin, and `src/live.config.ts` according to `$dineway-building-site`.
2. Create the shared layout and public page context. Render `DinewayHead`, `DinewayBodyStart`, and `DinewayBodyEnd`; pass `{ collection, id, slug }` on content-backed detail pages.
3. Merge fonts, design tokens, reset styles, shared keyframes, and global behavior without deleting requirements of existing routes. Scope incompatible styles under the site wrapper.
4. Write or merge `seed/seed.json` from the approved content model. Preserve existing collections and entries unless the user approved replacement.
5. Model exact source settings, menus, collections, fields, sections, taxonomies, entries, and editorial media. Use `$media` for seed image fields.
6. Validate with `npx dineway seed seed/seed.json --validate`.
7. For a fresh site, run migrations and apply the seed. For an existing site, inspect the live schema/content first and merge without overwriting existing data.
8. Start development through the repository's approved background-process mechanism, generate current Dineway types, and keep the generated types as the component data contract.
9. Create same-site shared icons/components under the planned namespace. Prefer Astro components; use React only when client-side state is required.
10. Download decorative assets with unique filenames into planned namespaces. Keep editorial media in Dineway rather than hard-coding URLs into components.
11. Verify all existing routes, then run `pnpm typecheck` and `pnpm build`.

Every page that queries Dineway content must call `Astro.cache.set(cacheHint)`. Every CMS image is an object and must be rendered with the Dineway `Image` component or its resolved `.src`.

### Asset discovery script pattern

Run an equivalent browser-side inspection for each page:

```javascript
JSON.stringify({
  images: [...document.querySelectorAll("img")].map((img) => ({
    src: img.currentSrc || img.src,
    alt: img.alt,
    width: img.naturalWidth,
    height: img.naturalHeight,
    parentClasses: img.parentElement?.className,
    siblings: img.parentElement?.querySelectorAll("img").length ?? 0,
    position: getComputedStyle(img).position,
    zIndex: getComputedStyle(img).zIndex,
  })),
  videos: [...document.querySelectorAll("video")].map((video) => ({
    src: video.currentSrc || video.src || video.querySelector("source")?.src,
    poster: video.poster,
    autoplay: video.autoplay,
    loop: video.loop,
    muted: video.muted,
  })),
  backgroundImages: [...document.querySelectorAll("*")]
    .filter((element) => getComputedStyle(element).backgroundImage !== "none")
    .map((element) => ({
      value: getComputedStyle(element).backgroundImage,
      element: `${element.tagName}.${element.className?.toString().split(" ")[0] ?? ""}`,
    })),
  svgCount: document.querySelectorAll("svg").length,
  fonts: [...new Set([...document.querySelectorAll("*")].slice(0, 200).map((element) => getComputedStyle(element).fontFamily))],
  favicons: [...document.querySelectorAll('link[rel*="icon"]')].map((link) => ({
    href: link.href,
    sizes: link.sizes?.toString(),
  })),
});
```

Download in bounded parallel batches with error handling. Record source URL, local path, media role, dimensions, MIME type, and checksum in `<page-research>/ARTIFACT_MANIFEST.md`.

### Optional generated-asset fallback

Treat image generation as an exception. Use it only when the exact source asset remains unrecoverable after bounded inspection; the asset is not a logo, trademark, product screenshot, legal/certification mark, or distinctive brand artwork; the user explicitly approves a non-identical substitute; and an approved image-generation capability is available. Record approval, prompt, model, output path, and generated status in the artifact manifest. Otherwise report the missing asset without fabricating the source identity.

## Phase 3: Component Specification and Dispatch

For each section, repeat: **extract → write specification → dispatch → integrate**.

### Step 1: Extract

1. Capture a section screenshot in its namespaced screenshot directory.
2. Run one computed-style extraction over the component container rather than estimating CSS.
3. Capture before/after computed styles for every scroll, click, hover, focus, expanded, and active state. Use this workflow:
   - **State A:** Run the computed-style walker at the current/default state.
   - **Trigger the state change** via browser automation (scroll to threshold, click a tab, hover an element).
   - **State B:** Re-run the same extraction script on the same element.
   - **Diff the two** to identify exactly which CSS properties change.
   - Record the diff explicitly in the spec: "Property X changes from VALUE_A to VALUE_B, triggered by TRIGGER, with transition: TRANSITION_CSS."
   - For scroll-dependent elements, capture the exact trigger threshold (scroll position in px, or viewport intersection ratio).
   - For tabbed content, click each tab and extract the content and styles per state.
4. Extract all text, labels, alt text, placeholders, links, and per-state content verbatim.
5. Identify every decorative asset and Dineway editorial media field, including layered compositions.
6. Determine whether the component is server-rendered Astro or requires a focused client island.
7. Identify the exact Dineway source and props: setting, menu, section, collection, entry fields, visual-editing attributes, cache ownership, and empty state.
8. Split the section when it contains 3 or more independently complex sub-components.

Use this browser-side computed-style walker, adapting only the selector:

```javascript
(function (selector) {
  const element = document.querySelector(selector);
  if (!element) return JSON.stringify({ error: `Element not found: ${selector}` });
  const properties = [
    "fontSize", "fontWeight", "fontFamily", "lineHeight", "letterSpacing", "color",
    "textTransform", "textDecoration", "backgroundColor", "background",
    "padding", "paddingTop", "paddingRight", "paddingBottom", "paddingLeft",
    "margin", "marginTop", "marginRight", "marginBottom", "marginLeft",
    "width", "height", "maxWidth", "minWidth", "maxHeight", "minHeight",
    "display", "flexDirection", "justifyContent", "alignItems", "gap",
    "gridTemplateColumns", "gridTemplateRows", "borderRadius", "border",
    "borderTop", "borderBottom", "borderLeft", "borderRight", "boxShadow",
    "overflow", "overflowX", "overflowY", "position", "top", "right", "bottom", "left",
    "zIndex", "opacity", "transform", "transition", "cursor", "objectFit",
    "objectPosition", "mixBlendMode", "filter", "backdropFilter", "whiteSpace",
    "textOverflow", "WebkitLineClamp",
  ];
  function styles(node) {
    const computed = getComputedStyle(node);
    return Object.fromEntries(properties.map((property) => [property, computed[property]]).filter(([, value]) => value && !["none", "normal", "auto", "0px", "rgba(0, 0, 0, 0)"].includes(value)));
  }
  function walk(node, depth) {
    if (depth > 4) return null;
    const children = [...node.children];
    return {
      tag: node.tagName.toLowerCase(),
      classes: node.className?.toString().split(" ").slice(0, 5).join(" "),
      text: node.childNodes.length === 1 && node.childNodes[0].nodeType === 3 ? node.textContent.trim().slice(0, 200) : null,
      styles: styles(node),
      image: node.tagName === "IMG" ? { src: node.src, alt: node.alt, width: node.naturalWidth, height: node.naturalHeight } : null,
      childCount: children.length,
      children: children.slice(0, 20).map((child) => walk(child, depth + 1)).filter(Boolean),
    };
  }
  return JSON.stringify(walk(element, 0), null, 2);
})("SELECTOR");
```

### Step 2: Write the component specification

Write `<page-research>/components/<component-name>.spec.md` before dispatching. Fill every section; use `N/A` only after verifying it is truly inapplicable.

```markdown
# <ComponentName> Specification

## Overview
- Target file: `src/components/sites/<site-key>/<page-key>/<ComponentName>.astro` or a justified `.tsx` island
- Screenshot: `docs/design-references/<site-key>/<page-key>/<screenshot>.png`
- Rendering boundary: Astro server component | React island with exact client directive
- Interaction model: static | click | scroll | hover | time | combination

## DOM Structure
Exact hierarchy and semantic elements.

## Computed Styles
### Container
- Every relevant exact computed value
### <Child>
- Every relevant exact computed value

## States and Behaviors
### <Behavior>
- Trigger and threshold
- State A exact values
- State B exact values
- Transition
- Implementation mechanism

## Per-State Content
Exact text, links, images, and data for every state.

## Dineway Content Contract
- Source: setting | menu | section | collection/entry | static decorative data
- Collection and fields, if applicable
- Generated type/prop shape
- Visual-editing attributes
- Cache ownership and empty state
- Editorial media fields versus static decorative assets

## Assets
- Namespaced paths and exact roles for every layer

## Text Content
All source text verbatim.

## Responsive Behavior
- Desktop 1440px
- Tablet 768px
- Mobile 390px
- Measured breakpoint(s)
```

### Step 3: Dispatch builders

Use isolated worktrees/branches when builder-agent tooling is available. Dispatch simple sections to one builder. For complex sections, dispatch sub-components first and a wrapper builder after their contracts stabilize.

Every builder prompt must inline:

- The complete component specification
- Screenshot path
- Exact namespaced target file and exclusive ownership boundary
- Shared components and generated Dineway types it may import
- Dineway props/content contract and prohibition on hard-coded CMS-owned content
- Exact responsive breakpoints and state behavior
- Instruction not to modify `astro.config.mjs`, shared layouts/styles, `seed/seed.json`, schema, menus, settings, route files, or another builder's namespace
- Instruction to run `pnpm typecheck` before returning

As soon as one section is dispatched, continue extracting the next. Do not wait unless a wrapper depends on unfinished sub-components.

### Step 4: Integrate

As builders finish:

- Review their diff against the specification before merging.
- Reject or repair changes outside the assigned namespace.
- Reject hard-coded values that belong to Dineway content.
- Resolve conflicts without deleting unrelated routes or another clone namespace.
- Run `pnpm typecheck` and `pnpm build` after every integration.

## Phase 4: Page Assembly

After all section components are integrated:

1. Wire them into the exact planned Astro route or route family.
2. Query Dineway settings, menus, sections, collections, or entries in the route/layout rather than inside unrelated presentation components.
3. Call `Astro.cache.set(cacheHint)` for every content query.
4. Pass generated typed data and visual-editing attributes into components.
5. Render editorial image objects with `Image` from `dineway/ui`.
6. Build page-level scroll containers, sticky layers, transitions, smooth scrolling, and client islands from `PAGE_TOPOLOGY.md` and `BEHAVIORS.md`.
7. Create the public page context and content identity required by Dineway plugins.
8. Confirm every previously existing route remains present.
9. Run `pnpm typecheck` and `pnpm build`.

## Phase 5: Visual and Dineway QA

Do not declare completion after assembly.

1. Start the Dineway dev server with the repository-approved background-process tool.
2. Verify every explicit and discovered destination route returns the expected SSR page.
3. Capture original and clone screenshots at identical 1440px and 390px viewports.
4. Compare section-by-section. When a mismatch exists, re-check the specification; re-extract a wrong spec or repair an implementation that diverged from a correct spec.
5. Re-test every scroll, click, hover, focus, responsive, and timed behavior.
6. Verify source-derived settings and menus render from Dineway.
7. Verify every CMS-backed route renders seeded published entries, empty states do not mask missing data, and editorial media resolves through Dineway.
8. Verify the admin UI is reachable and content models are editable.
9. Validate `seed/seed.json`, regenerate types, and rerun typecheck/build.
10. Verify `/robots.txt`, `/sitemap.xml`, and `/schemamap.xml` and confirm public URLs match the source route map.

Only finish when the clone is visually faithful and the Dineway content/runtime contract works.

## Pre-Dispatch Checklist

Before dispatching any builder, verify:

- [ ] A complete component specification exists
- [ ] Every visual value came from computed styles, not estimation
- [ ] Interaction model and every state are documented
- [ ] Scroll thresholds and transitions are exact
- [ ] Hover/focus changes are exact
- [ ] Every asset layer is identified and classified as decorative or editorial
- [ ] Desktop, tablet, and mobile behavior is documented
- [ ] Source text is verbatim
- [ ] Dineway source, fields, props, cache ownership, editing attributes, and empty state are documented
- [ ] Astro versus client-island boundary is justified
- [ ] Builder ownership excludes shared configuration, routes, schema, and seed
- [ ] The inline prompt remains under roughly 150 lines; otherwise split it

## What Not to Do

These are lessons from previous failed clones — each one cost hours of rework:

- **Do not build click tabs when the source is scroll-driven, or scroll behavior when the source is click-driven.** Determine the interaction model FIRST by scrolling before clicking. This is the most expensive mistake — it requires a complete rewrite, not a CSS fix.
- **Do not extract only the default state.** If there are tabs showing "Featured" on load, click every other tab and extract each one's content. If the header changes on scroll, capture styles at position 0 AND position 100+.
- **Do not miss layered images, video, canvas, Lottie, or background assets.** A background watercolor + foreground UI mockup = 2 images. Check every container's DOM tree for multiple `<img>` elements and positioned overlays.
- **Do not build mockup components for content that is actually video or animation.** Check if a section uses `<video>`, Lottie, or canvas before building elaborate HTML mockups of what the video shows.
- **Do not approximate CSS with convenient utility classes.** "It looks like `text-lg`" is wrong if the computed value is `18px` and `text-lg` is `18px/28px` but the actual line-height is `24px`. Extract exact values.
- **Do not build everything in one monolithic commit.** The entire pipeline is designed for incremental progress with verified builds at each step.
- **Do not replace an existing route, schema, seed entry, or asset namespace without approval.** Preserve existing routes and namespaced artifacts; ask before updating a route that already exists.
- **Do not reference specs or docs from builder prompts.** Each builder gets the specification inline in its prompt — never "see the spec file" or "see DESIGN_TOKENS.md for colors." The builder should have zero need to read external docs.
- **Do not skip asset extraction.** Without real images, videos, and fonts, the clone will always look fake regardless of how perfect the CSS is.
- **Do not give a builder agent too much scope.** If you are writing a builder prompt and it is getting long because the section is complex, that is a signal to break it into smaller tasks.
- **Do not bundle unrelated sections into one agent.** A CTA section and a footer are different components with different designs — do not hand them both to one agent and hope for the best.
- **Do not dispatch before the shared Dineway foundation and component specification exist.**
- **Do not let builders edit shared foundation files.**
- Do not hard-code site identity, navigation, editorial copy, repeated content, or editorial media that the content model assigns to Dineway.
- Do not treat Dineway image objects as strings.
- Do not omit `cacheHint`, public page context, plugin contribution components, `supports: ["seo"]`, or matching `urlPattern` values.
- Do not use static path generation for Dineway content; the site is SSR.
- Do not make a static component a client island without an observed interaction requirement.
- Do not skip responsive extraction, visual comparison, seed validation, type generation, or discovery endpoint checks.
- Do not recurse through links found on discovered pages. Only explicit pages produce one-hop targets.
- **Do not forget smooth scroll libraries.** Check for Lenis (`.lenis` class), Locomotive Scroll, or similar. Default browser scrolling feels noticeably different and the user will spot it immediately.

## Completion Report

Report:

- Explicit URLs, one-hop discovered URLs, parent relationships, and destination route mapping
- Existing routes/content preserved and any approved replacements
- Total sections built
- Total components created
- Total spec files written (should match total components)
- Total assets downloaded (images, videos, SVGs, fonts)
- Dineway settings, menus, collections, sections, taxonomies, entries, and editorial media created
- Seed validation, type generation, `pnpm typecheck`, and `pnpm build` results
- Admin UI and CMS render verification
- `/robots.txt`, `/sitemap.xml`, and `/schemamap.xml` status
- Desktop/mobile visual QA and interaction results
- Remaining discrepancies, missing assets, or unsupported source-backend behavior

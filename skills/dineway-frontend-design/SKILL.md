---
name: dineway-frontend-design
description: Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, artifacts, posters, or applications (examples include websites, landing pages, dashboards, React components, HTML/CSS layouts, or when styling/beautifying any web UI). Generates creative, polished code and UI design that avoids generic AI aesthetics.
license: Complete terms in LICENSE.txt
---

This skill guides creation of distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. Implement real working code with exceptional attention to aesthetic details and creative choices.

The user provides frontend requirements: a component, page, application, or interface to build. They may include context about the purpose, audience, or technical constraints.

## Design Thinking

Before coding, understand the context and commit to a BOLD aesthetic direction:

- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Pick an extreme: brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian, etc. There are so many flavors to choose from. Use these for inspiration but design one that is true to the aesthetic direction.
- **Constraints**: Technical requirements (framework, performance, accessibility).
- **Differentiation**: What makes this UNFORGETTABLE? What's the one thing someone will remember?

**CRITICAL**: Choose a clear conceptual direction and execute it with precision. Bold maximalism and refined minimalism both work - the key is intentionality, not intensity.

Design the whole composition as deliberately as its individual elements. Decide what users notice first, read next, and act on. Relate typography, photography, controls, and whitespace to those roles. Before detailing components, establish their shared scale, alignment, spacing, and density. When several elements compete for attention, adjust their hierarchy and grouping before adding another treatment. A memorable interface needs a clear center of attention even when its aesthetic is rich or unconventional.

Then implement working code (HTML/CSS/JS, React, Vue, etc.) that is:

- Production-grade and functional
- Visually striking and memorable
- Cohesive with a clear aesthetic point-of-view
- Meticulously refined in every detail

## Frontend Aesthetics Guidelines

Focus on:

- **Typography**: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter; opt instead for distinctive choices that elevate the frontend's aesthetics; unexpected, characterful font choices. Pair a distinctive display font with a refined body font. Typography should feel intentional, not oversized by default.
- **Color & Theme**: Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes.
- **Motion**: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML. Use Motion library for React when available. Focus on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions. Use scroll-triggering and hover states that surprise.
- **Spatial Composition**: Unexpected layouts. Asymmetry. Overlap. Diagonal flow. Grid-breaking elements. Generous negative space OR controlled density.
- **Backgrounds & Visual Details**: Create atmosphere and depth rather than defaulting to solid colors. Add contextual effects and textures that match the overall aesthetic. Apply creative forms like gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows, decorative borders, custom cursors, and grain overlays.
- **System Coherence**: Carry the chosen direction through navigation, page introductions, repeated cards, and editing flows. Give equivalent roles comparable visual weight across pages. Use shared tokens and components for recurring decisions, while allowing each page's task to shape its composition. Correct inconsistencies at their owning token, component, or page instead of accumulating global `!important` overrides.

## Typography Size Discipline

Bold design does not mean huge text. Do not generate oversized headings unless the user explicitly asks for poster-like, editorial, or billboard typography.

Use a clear type hierarchy with context-specific limits:

- Hero/display `h1`: usually `clamp(2.5rem, ..., 4.5rem)` at most; mobile max around `2.75rem`.
- Standard page `h1`: usually `clamp(2rem, ..., 3rem)` at most.
- Section headings: usually `clamp(1.5rem, ..., 2.25rem)` at most.
- Card, panel, sidebar, table, or tool-surface titles: usually `1rem`-`1.5rem`.
- Body copy: usually `1rem`-`1.125rem`, with readable line height.

Do not reuse hero/display heading styles for ordinary pages, sections, cards, CMS content titles, dashboards, or compact UI panels. Match display text to its container and workflow: operational interfaces, restaurant pages, content pages, and product surfaces need scannable hierarchy more than spectacle.

Avoid viewport-driven text growth. Do not set `font-size` directly with `vw`/`vh`; if responsive scaling is needed, use `clamp()` with conservative `rem` min/max bounds. Any heading above `5rem` or `80px` requires explicit user intent and must not appear in ordinary websites or apps.

Before delivery, check that headings wrap cleanly on mobile and desktop, do not overlap neighboring content, do not dominate non-hero pages, and do not force horizontal scrolling. Letter spacing should normally be `0`; avoid negative letter spacing unless explicitly needed for a specific display face and verified not to harm readability.

Preserve comfortable body and supporting-text readability as well: smaller text is not automatically more refined. Test actual long titles and short action labels together; let their surrounding layout wrap or stack rather than squeeze the action or cause overflow.

NEVER use generic AI-generated aesthetics like overused font families (Inter, Roboto, Arial, system fonts), cliched color schemes (particularly purple gradients on white backgrounds), predictable layouts and component patterns, and cookie-cutter design that lacks context-specific character.

Interpret creatively and make unexpected choices that feel genuinely designed for the context. No design should be the same. Vary between light and dark themes, different fonts, different aesthetics. NEVER converge on common choices (Space Grotesk, for example) across generations.

**IMPORTANT**: Match implementation complexity to the aesthetic vision. Maximalist designs need elaborate code with extensive animations and effects. Minimalist or refined designs need restraint, precision, and careful attention to spacing, typography, and subtle details. Elegance comes from executing the vision well.

## Real Content and Browser Refinement

For substantial page or site work, validate the shared direction on a representative page with real content before expanding it to other page families. For a local refinement, inspect the changed surface and affected shared consumers.

- **Use real content early.** Check long titles, varied image proportions, sparse results, and relevant empty states. Match images, captions, and destinations to the same record. Retain Dineway CMS bindings and structured content rather than replacing them with convenient hardcoded display data. Label fixtures in verification evidence; avoid invented statistics or social proof.
- **Review the actual experience.** Read, scroll, click, type, filter, and use the keyboard at appropriate desktop, tablet, and mobile sizes. For forms or asynchronous flows, include relevant focus, validation, progress, error/recovery, and preview states. Check that actions remain accessible and the visual language carries through the flow.
- **Inspect relationships and small details.** Look at heading/action wrapping, reading order, image height and cropping, horizontal overflow, and the spacing between content groups. Compare related pages together. Ask whether users can identify the main content and next action without competing elements pulling them away.
- **Use reliable evidence.** Wait for fonts and relevant images to load before judging screenshots. Distinguish product defects from capture timing and fixture limitations.

Repair the cause at the appropriate styling owner and retest the affected scope. A passing build and a polished default screenshot do not establish that the complete interaction works; report the states actually checked and any material gaps.

Remember: Claude is capable of extraordinary creative work. Don't hold back, show what can truly be created when thinking outside the box and committing fully to a distinctive vision.

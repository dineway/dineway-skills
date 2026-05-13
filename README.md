# Dineway Skills

Skills for designing, building, and publishing AI-ready restaurant websites with Dineway.

Dineway is the Agentic Website builder for restaurants and local businesses. It combines structured content modeling with the Model Context Protocol (MCP) to create intelligent, AI-powered sites that do more than display information: they understand menus, manage reputation, support marketing workflows, and help restaurant owners keep the site useful over time.

The core thesis is simple: a restaurant website should not be a brochure. It should work more like an employee that understands the business, acts with context, and improves under human oversight.

## What This Skill Pack Covers

This repository packages the agent skills used to create restaurant AI sites with Dineway:

| Skill | Purpose |
| --- | --- |
| `building-restaurant-site` | Builds a polished Astro-first restaurant site from enriched place data, then connects Dineway CMS-managed Blog, News, Menu, Reviews, and Gallery sections. |
| `enrich-place-details` | Fetches enriched restaurant data from the hosted Dineway API and saves it as local JSON for downstream site generation. |
| `dineway-cli` | Guides Dineway CLI usage for schema, content, media, seed files, type generation, authentication, and deployment. |
| `frontend-design` | Produces distinctive, production-grade frontend interfaces for the visible restaurant website. |
| `brainstorming` | Helps compare information architecture, visual direction, content boundaries, and implementation choices before writing the site. |
| `planning-with-files` | Keeps complex builds organized with task, findings, and progress files. |

Together, these skills guide an agent through the full restaurant-site lifecycle:

1. Collect the restaurant name, city, and optional place id.
2. Fetch real place, review, media, menu, and business-profile data.
3. Convert those signals into a guest-facing information architecture and visual direction.
4. Build a responsive Astro website with local SEO and structured data.
5. Add Dineway-managed Blog, News, Menu, Reviews, and Gallery content.
6. Upload media, generate types, seed content, validate routes, and prepare deployment.

## Using These Skills

Install the skill pack with `npx skills`:

```bash
npx skills add https://github.com/dineway/dineway-skills
```

You can also copy or install the `skills/` directories into an agent runtime that supports Codex-style skills, then invoke the relevant skill by name.

For a full restaurant build, start with:

```text
Use building-restaurant-site to build an AI-ready Dineway restaurant site for "Restaurant Name" in "City, Country".
```

For data enrichment only:

```text
Use enrich-place-details for "Restaurant Name" in "City, Country".
```

For an existing Dineway project:

```text
Use dineway-cli to seed content, generate types, upload media, and deploy this Dineway site.
```

## Expected Output

A complete restaurant AI site should include:

- A high-quality public website built around the actual restaurant identity, location, reviews, media, and service details.
- Dineway CMS-managed columns for Blog, News, Menu, Reviews, and Gallery.
- Guest-facing copy that avoids internal provenance notes, placeholders, or unsupported claims.
- Local SEO metadata and JSON-LD using only fields present in the enriched place data.
- Media downloaded locally before design and uploaded into Dineway where CMS-managed content needs it.
- A validated Dineway workflow for schema, seed content, generated types, and deployment.

## License

MIT. See [LICENSE](LICENSE).

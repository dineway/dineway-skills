---
name: dineway-cli
description: Use the Dineway CLI to manage content, schema, media, deployment, and more. Use this skill when you need to interact with a Dineway project or running instance from the command line — deploying a site, creating content, managing collections, uploading media, generating types, or scripting CMS operations.
---

# Dineway CLI

The Dineway CLI (`dineway`) manages Dineway Agentic Web builder projects and instances. Commands fall into three categories:

- **Local commands** — work directly on local project files or a SQLite file, no running server needed: `init`, `dev`, `seed`, `export-seed`, `auth secret`
- **Deployment commands** — orchestrate platform CLIs or generate provider files: `deploy`
- **Remote commands** — talk to a running Dineway instance via HTTP: `types`, `login`, `logout`, `whoami`, `auth setup-link`, `content`, `schema`, `media`, `search`, `taxonomy`, `menu`

## Authentication

Remote commands resolve auth automatically:

1. `--token` flag
2. `DINEWAY_TOKEN` from the shell environment or project `.env`
3. Stored credentials from `dineway login`
4. Dev bypass (localhost only — no token needed)

When `--url` is omitted, remote commands check `DINEWAY_URL` and `DINEWAY_SITE_URL` from the shell environment and project `.env` before falling back to localhost.

For local dev servers, just run the command — auth is handled automatically. For remote instances, run `dineway login --url https://my-site.example.com` first, or rely on the `.env` written by Forgeway deploy.

`dineway deploy` does not use Dineway instance authentication. Forgeway deploy uses a project shadow deploy grant only to upgrade to a verified Dineway account by email; Other deploy targets use provider CLIs such as Railway CLI, flyctl, or gcloud.

## Custom Headers & Reverse Proxies

Sites behind external auth proxies or other reverse proxies may need auth headers on every request. The CLI supports this via `--header` flags and environment variables.

### Forwarded Auth Headers (Recommended for CI/Automation)

```bash
# Single header
npx dineway login --url https://my-site.example.com \
  --header "X-Proxy-Auth: shared-secret"

# Short form
npx dineway login -H "X-Proxy-Auth: shared-secret"

# Via environment (newline-separated)
export DINEWAY_HEADERS="X-Proxy-Auth: shared-secret
X-Forwarded-User: ci-bot@example.com"
npx dineway login --url https://my-site.example.com
```

Headers are persisted to `~/.config/dineway/auth.json` after login, so subsequent commands inherit them automatically.

### Generic Reverse Proxy Auth

The `--header` flag works with any auth scheme:

```bash
# Basic auth
npx dineway login --url https://example.com -H "Authorization: Basic dXNlcjpwYXNz"

# Custom auth header
npx dineway login --url https://example.com -H "X-API-Key: secret123"
```

## Quick Reference

### Database Setup

```bash
# Initialize database with migrations
npx dineway init

# Start dev server (runs migrations, starts Astro)
npx dineway dev

# Start dev server and generate types from remote
npx dineway dev --types

# Apply a seed file
npx dineway seed .dineway/seed.json

# Export database as seed
npx dineway export-seed > seed.json
npx dineway export-seed --with-content > seed.json
```

### Type Generation

```bash
# Generate types from local dev server
npx dineway types

# Generate from remote
npx dineway types --url https://my-site.example.com

# Custom output path
npx dineway types --output src/types/cms.ts
```

Writes `.dineway/types.ts` (TypeScript interfaces) and `.dineway/schema.json`.

### Authentication

```bash
# Login (OAuth Device Flow)
npx dineway login --url https://my-site.example.com

# Check current user
npx dineway whoami

# Logout
npx dineway logout

# Create a one-time browser setup link for the current admin
npx dineway auth setup-link

# Generate auth secret for deployment
npx dineway auth secret
```

### Deployment

`dineway deploy` keeps Dineway on the standard Node.js deployment contract:

```bash
pnpm build
node ./dist/server/entry.mjs
```

Use it to generate provider files and delegate deployment to platform CLIs:

```bash
# First deploy: choose a target interactively
npx dineway deploy

# Stable targets
npx dineway deploy forgeway
npx dineway deploy railway
npx dineway deploy docker
npx dineway deploy fly

# Experimental target
npx dineway deploy gcp

# Self-hosting baseline
npx dineway deploy docker --compose

# Plan without writing files or deploying
npx dineway deploy fly --dry-run
```

Target behavior:

| Target     | Support      | Behavior                                                                                       |
| ---------- | ------------ | ---------------------------------------------------------------------------------------------- |
| `forgeway` | Stable       | Deploys through Dineway's first-party Forgeway platform and bootstraps admin access.           |
| `railway`  | Stable       | Generates `railway.json` and runs `railway up`.                                                |
| `docker`   | Stable       | Generates `Dockerfile`, `.dockerignore`, and optional `docker-compose.yml`; never runs Docker. |
| `fly`      | Stable       | Generates Docker-backed Fly config and runs `fly deploy --remote-only`.                        |
| `gcp`      | Experimental | Runs `gcloud run deploy --source .`; requires remote database defaults.                        |

Provider CLI rules:

- Railway can offer to install `@railway/cli` after interactive confirmation.
- fly.io requires manual flyctl installation.
- GCP requires manual Google Cloud CLI installation.
- `--yes` does not approve global CLI installation.
- `--dry-run` does not require missing provider CLIs.
- First-party deploy targets must not require a Git remote as the only path.
- Docker and fly targets do not require local Docker Desktop.

Persistence and secrets:

- The selected target is stored in `package.json` under `dineway.deploy.target` after a successful deploy or generation.
- Generated provider files are not overwritten when they already exist.
- Generated provider files must not contain secrets.
- Forgeway deploy writes `DINEWAY_SITE_URL` and `DINEWAY_TOKEN` to project `.env`, adds `.env` to `.gitignore`, prints a one-time setup link, and does not print the raw admin API token.
- Forgeway uses the Dineway account email as the initial deployed-site admin email. Shadow users cannot deploy; the CLI upgrades the shadow grant through email verification before deploy.
- First Forgeway browser login should use the setup link, then register a passkey. Magic link login requires a site email provider and is not part of admin bootstrap.
- Regenerate a lost or expired Forgeway setup link with `npx dineway auth setup-link` from the project directory.
- Configure `DINEWAY_AUTH_SECRET`, `DINEWAY_PREVIEW_SECRET`, database auth tokens, and media storage credentials in the provider's secret system.
- File-backed libSQL and local uploads require durable disk; use remote libSQL/PostgreSQL and S3-compatible storage on ephemeral or multi-instance hosts.
- Cloud Run is experimental and should use remote database and object storage by default.

### Content CRUD

The CLI is designed for agents. Create and update auto-publish by default so agents get read-after-write consistency without managing drafts.

```bash
# List content
npx dineway content list posts
npx dineway content list posts --status published --limit 10

# Get a single item (Portable Text fields converted to markdown)
# Returns draft data if a pending draft exists
npx dineway content get posts 01ABC123
npx dineway content get posts 01ABC123 --raw        # skip PT->markdown conversion
npx dineway content get posts 01ABC123 --published   # ignore pending drafts

# Create content (auto-publishes by default)
npx dineway content create posts --data '{"title": "Hello", "content": "# World"}'
npx dineway content create posts --file post.json --slug hello-world
npx dineway content create posts --draft --data '...'  # keep as draft
cat post.json | npx dineway content create posts --stdin

# Update (requires --rev from a prior get, auto-publishes by default)
npx dineway content update posts 01ABC123 --rev MToyMDI2... --data '{"title": "Updated"}'
npx dineway content update posts 01ABC123 --rev MToyMDI2... --draft --data '...'  # keep as draft

# Delete (soft delete)
npx dineway content delete posts 01ABC123

# Lifecycle
npx dineway content publish posts 01ABC123
npx dineway content unpublish posts 01ABC123
npx dineway content schedule posts 01ABC123 --at 2026-03-01T09:00:00Z
npx dineway content restore posts 01ABC123
```

### Schema Management

```bash
# List collections
npx dineway schema list

# Get collection with fields
npx dineway schema get posts

# Create collection
npx dineway schema create articles --label Articles --description "Blog articles"

# Delete collection
npx dineway schema delete articles --force

# Add field
npx dineway schema add-field posts body --type portableText --label "Body Content"
npx dineway schema add-field posts featured --type boolean --required

# Remove field
npx dineway schema remove-field posts featured
```

Field types: `string`, `text`, `number`, `integer`, `boolean`, `datetime`, `image`, `reference`, `portableText`, `json`.

### Media

```bash
# List media
npx dineway media list
npx dineway media list --mime image/png

# Upload
npx dineway media upload ./photo.jpg --alt "A sunset" --caption "Bristol, 2026"

# Get / delete
npx dineway media get 01MEDIA123
npx dineway media delete 01MEDIA123
```

### Search

```bash
npx dineway search "hello world"
npx dineway search "hello" --collection posts --limit 5
```

### Taxonomies

```bash
npx dineway taxonomy list
npx dineway taxonomy terms categories
npx dineway taxonomy add-term categories --name "Tech" --slug tech
npx dineway taxonomy add-term categories --name "Frontend" --parent 01PARENT123
```

### Menus

```bash
npx dineway menu list
npx dineway menu get primary
```

## Drafts and Publishing

The CLI auto-publishes on `create` and `update` by default. This means:

- **`create`** creates the item and immediately publishes it
- **`update`** updates the item and publishes if a draft revision was created
- **`get`** returns draft data if a pending draft exists (e.g. from the admin UI)

Use `--draft` on create/update to skip auto-publishing. Use `--published` on get to ignore pending drafts.

Collections that support revisions store edits as draft revisions. The CLI handles this transparently — agents don't need to know whether a collection uses revisions or not.

## JSON Output

All remote commands support `--json` for machine-readable output. It's auto-enabled when stdout is piped.

```bash
# Pipe to jq
npx dineway content list posts --json | jq '.items[].slug'

# Use in scripts
ID=$(npx dineway content create posts --data '{"title":"Hello"}' --json | jq -r '.id')
```

## Editing Flow

For details on how content editing works — Portable Text/markdown conversion, `_rev` tokens, and raw mode — see **[EDITING-FLOW.md](./EDITING-FLOW.md)**.

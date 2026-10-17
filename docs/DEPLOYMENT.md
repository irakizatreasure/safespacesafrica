# GitHub and production deployment

## GitHub repository

The source is published in [irakizatreasure/safespacesafrica](https://github.com/irakizatreasure/safespacesafrica) on `main`. Do not commit `.env`, database files, or production secrets.

The workflow in `.github/workflows/ci.yml` runs Python syntax checks, the test suite, and a browser JavaScript syntax check on pushes and pull requests to `main`.

GitHub Pages is a static-file host and cannot run the Python WSGI API or SQLite-backed administration. Do not point Pages at this source tree as if it were a complete deployment. Use a Python-capable application host for the full site.

## Render Blueprint deployment

The included `render.yaml` describes a Docker web service with Gunicorn, `/api/health` readiness checks, HTTPS-only session cookies, and a 1 GB persistent disk for the SQLite database. It selects Frankfurt for the Rwanda audience and Render's paid `starter` plan because persistent disks are not available on free web services. After initial setup, it deploys commits from `main` only when GitHub checks pass. Review the current plan and disk charges before creating the Blueprint.

1. In Render, create a new Blueprint and connect `irakizatreasure/safespacesafrica`.
2. When prompted, supply a real administrator email and a unique password of at least 14 characters. Render stores these as service environment secrets; do not put them in GitHub or chat.
3. Review the plan, persistent disk, and region, then create the service.
4. Wait for the deploy to pass its `/api/health` check. Visit the generated service URL and sign in at `/admin`.
5. In the Render dashboard, verify `SISP_COOKIE_SECURE=true`, `SISP_ENV=production`, `SISP_DB_PATH=/var/data/sisp.sqlite3`, and confirm the disk is attached before entering any editorial work.
6. Set up database backups and a restore drill before public use. Render's disk preserves database files across deploys, but it is not a backup.

No hosting account is connected by this workspace, so the Blueprint has not been applied and there is no live URL yet. Public launch still requires reviewed content, privacy/safeguarding review, real support arrangements, referral verification, and operational monitoring. See [HANDOVER.md](HANDOVER.md) for the full launch blockers.

## Development preview

1. Create a protected environment file: `cp .env.example .env`.
2. Set `SISP_ADMIN_EMAIL` and a unique `SISP_ADMIN_PASSWORD` of at least 14 characters before first startup.
3. Run `python app.py` from the project directory for a local preview. The app creates the SQLite schema, seeds content idempotently and serves on `127.0.0.1:8000`.
4. Visit `/api/health`; `deployment_status` remains `not_verified` because the application does not establish that it has been deployed.
5. Run tests with `python -m unittest discover -s tests -v`.

## Production work still required

The production container uses Gunicorn and SQLite on a persistent disk for a single-instance pilot. SQLite and a single application instance are not a production-scale architecture. Before wider public use, migrate to PostgreSQL or another reviewed data store, retain a supported WSGI server, configure secrets outside the app folder, restrict the database and backups, and add monitoring and incident response. Complete a backup and restore drill, load tests, dependency/security scans, privacy/legal review, accessibility evaluation, and content/safeguarding review.

Set `SISP_COOKIE_SECURE=true` only when HTTPS is correctly configured. Bind the app to a private interface behind the reverse proxy. Do not expose the development server directly to the Internet.

The production WSGI entry point validates the first administrator email/password, HTTPS cookie setting, and any configured AI provider before it starts. It does not print secret values in startup errors.

## Optional AI provider setup

Set all of `SISP_AI_PROVIDER`, `SISP_AI_API_KEY`, and `SISP_AI_MODEL` in the hosting secret manager. The provider can be `openai` or `gemini`. Use a model approved by the organization and review current provider terms/privacy settings before sending user questions. For OpenAI, the application sends a server-side Bearer token to the configured Chat Completions endpoint; for Gemini it sends `x-goog-api-key` in the request header. No key is returned to the browser.

AI answers are not enabled just by adding a key: at least one lesson must be reviewed and published, because retrieval is limited to approved, published items. Set model names and any endpoint override intentionally. The local test suite mocks Gemini and does not make provider calls.

## Database backup

See the online SQLite backup example and restore notes in [HANDOVER.md](HANDOVER.md). Before a production rollout, select a supported backup schedule, encryption and retention policy. The example Compose volume is for a local preview only.

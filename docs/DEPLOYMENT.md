# Umucyo Spaces Hub: GitHub and production deployment

## GitHub repository

The source is published in [irakizatreasure/safespacesafrica](https://github.com/irakizatreasure/safespacesafrica) on `main`. Do not commit `.env`, database files, or production secrets.

The workflow in `.github/workflows/ci.yml` runs Python syntax checks, the test suite, and a browser JavaScript syntax check on pushes and pull requests to `main`.

GitHub Pages is a static-file host and cannot run the Python WSGI API or SQLite-backed administration. Do not point Pages at this source tree as if it were a complete deployment. Use a Python-capable application host for the full site.

## Current Render + Supabase pilot

The live pilot at [safespacesafrica.onrender.com](https://safespacesafrica.onrender.com/) runs the Python WSGI app on Render and stores hosted content and admin accounts in Supabase Postgres. Render filesystems are ephemeral, so production startup requires `DATABASE_URL`. Local development continues to use SQLite.

1. The GitHub `main` branch is connected to the Render service through `render.yaml`; commits deploy after the repository checks pass.
2. Production `DATABASE_URL`, `SISP_ADMIN_EMAIL`, and `SISP_ADMIN_PASSWORD` are configured in Render's environment settings. Keep these values in the host secret manager, never in GitHub or chat.
3. The service stores persistent data in Supabase Postgres. Use the Supabase dashboard to manage the project and arrange exports/backups before major editorial work.
4. The live site is [safespacesafrica.onrender.com](https://safespacesafrica.onrender.com/); the administrator sign-in is at `/admin`. Render Free services can sleep after inactivity, and Supabase Free may pause after a period of low activity.

The site seeds learning drafts when the database is initialized. They remain unpublished until authorized review and publication. This is an early pilot: learning content still needs professional review, and human support, reporting, donation handling, privacy/safeguarding review, referral re-verification and operational monitoring remain necessary before wider public use. See [HANDOVER.md](HANDOVER.md) for the current status.

## Development preview

1. Create a protected environment file: `cp .env.example .env`.
2. Set `SISP_ADMIN_EMAIL` and a unique `SISP_ADMIN_PASSWORD` of at least 14 characters before first startup.
3. Run `python app.py` from the project directory for a local preview. The app creates the SQLite schema, seeds content idempotently and serves on `127.0.0.1:8000`.
4. Visit `/api/health`; `deployment_status` remains `not_verified` because the application does not establish that it has been deployed.
5. Run tests with `python -m unittest discover -s tests -v`.

## Production work still required

This free setup is suitable for an early, low-traffic pilot. It does not provide a production availability commitment, automatic backups on the free database plan, or protection against all provider free-tier changes. Before wider public use, choose a production database plan with backups, complete a backup and restore drill, add monitoring and incident response, review privacy and safeguarding, and complete accessibility, content and referral checks.

Set `SISP_COOKIE_SECURE=true` only when HTTPS is correctly configured. Bind the app to a private interface behind the reverse proxy. Do not expose the development server directly to the Internet.

The production WSGI entry point validates the administrator email/password, HTTPS cookie setting, and any configured AI provider before it starts. It does not print secret values in startup errors.

## Optional AI provider setup

Set all of `SISP_AI_PROVIDER`, `SISP_AI_API_KEY`, and `SISP_AI_MODEL` in the hosting secret manager. The provider can be `openai`, `gemini` or `claude`. Configure one at a time with a server-side key and model in Render. Claude uses the Anthropic Messages API; its key is sent only in the `x-api-key` header. Use a model approved by the organization and review current provider terms/privacy settings before sending user questions. For OpenAI, the application sends a server-side Bearer token to the configured Chat Completions endpoint; for Gemini it sends `x-goog-api-key` in the request header. No key is returned to the browser.

AI answers are not enabled just by adding a key: at least one lesson must be reviewed and published, because retrieval is limited to approved, published items. Set model names and any endpoint override intentionally. The automated checks do not make provider calls. A provider must be configured before Cyizere can answer live questions.

## Database backup

See the online SQLite backup example and restore notes in [HANDOVER.md](HANDOVER.md). Before a production rollout, select a supported backup schedule, encryption and retention policy. The example Compose volume is for a local preview only.

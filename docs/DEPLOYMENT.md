# GitHub and production deployment

## GitHub repository

The source is published in [irakizatreasure/safespacesafrica](https://github.com/irakizatreasure/safespacesafrica) on `main`. Do not commit `.env`, database files, or production secrets.

The workflow in `.github/workflows/ci.yml` runs Python syntax checks, the test suite, and a browser JavaScript syntax check on pushes and pull requests to `main`.

GitHub Pages is a static-file host and cannot run the Python WSGI API or SQLite-backed administration. Do not point Pages at this source tree as if it were a complete deployment. Use a Python-capable application host for the full site.

## Free Render + Supabase pilot

The included `render.yaml` deploys the Python WSGI app on Render's free web service. Since free Render filesystems are ephemeral, hosted content and admin accounts live in Supabase Postgres. Local development continues to use SQLite. In production, startup requires `DATABASE_URL` so the app cannot silently store editable content on a container that may be restarted.

1. Create a Supabase project on the Free plan. Choose a region near the people who will use the site.
2. In the Supabase dashboard, open **Connect** and copy the **Session pooler** connection string (port 5432). Render currently requires IPv4, and Supabase documents session pooling as the IPv4-compatible option for a persistent backend. Replace the password placeholder and URL-encode special characters in the password.
3. In Render, create a Blueprint and connect `irakizatreasure/safespacesafrica`. Use the `render.yaml` in the repository.
4. Set the requested `DATABASE_URL`, real `SISP_ADMIN_EMAIL`, and unique `SISP_ADMIN_PASSWORD` of at least 14 characters as Render secrets. Do not place them in the repository, issue comments, or chat.
5. Create the service and wait for `/api/health` to report ready. Visit the Render URL and sign in at `/admin`.
6. Export a database backup before major editorial work. Supabase Free has no automatic backups and can pause after a week with low activity; Render Free services sleep after 15 minutes without traffic.

The service will seed starter data when it first connects. Content is draft-only by default and must be reviewed and explicitly published by authorized people. No hosting account is connected to this workspace, so the Blueprint has not been applied and there is no live URL yet. Public launch still requires reviewed content, privacy/safeguarding review, real support arrangements, referral verification, and operational monitoring. See [HANDOVER.md](HANDOVER.md) for the full launch blockers.

## Development preview

1. Create a protected environment file: `cp .env.example .env`.
2. Set `SISP_ADMIN_EMAIL` and a unique `SISP_ADMIN_PASSWORD` of at least 14 characters before first startup.
3. Run `python app.py` from the project directory for a local preview. The app creates the SQLite schema, seeds content idempotently and serves on `127.0.0.1:8000`.
4. Visit `/api/health`; `deployment_status` remains `not_verified` because the application does not establish that it has been deployed.
5. Run tests with `python -m unittest discover -s tests -v`.

## Production work still required

This free setup is suitable for an early, low-traffic pilot. It does not provide a production availability commitment, automatic backups on the free database plan, or protection against all provider free-tier changes. Before wider public use, choose a production database plan with backups, complete a backup and restore drill, add monitoring and incident response, review privacy and safeguarding, and complete accessibility, content and referral checks.

Set `SISP_COOKIE_SECURE=true` only when HTTPS is correctly configured. Bind the app to a private interface behind the reverse proxy. Do not expose the development server directly to the Internet.

The production WSGI entry point validates the first administrator email/password, HTTPS cookie setting, and any configured AI provider before it starts. It does not print secret values in startup errors.

## Optional AI provider setup

Set all of `SISP_AI_PROVIDER`, `SISP_AI_API_KEY`, and `SISP_AI_MODEL` in the hosting secret manager. The provider can be `openai` or `gemini`. Use a model approved by the organization and review current provider terms/privacy settings before sending user questions. For OpenAI, the application sends a server-side Bearer token to the configured Chat Completions endpoint; for Gemini it sends `x-goog-api-key` in the request header. No key is returned to the browser.

AI answers are not enabled just by adding a key: at least one lesson must be reviewed and published, because retrieval is limited to approved, published items. Set model names and any endpoint override intentionally. The local test suite mocks Gemini and does not make provider calls.

## Database backup

See the online SQLite backup example and restore notes in [HANDOVER.md](HANDOVER.md). Before a production rollout, select a supported backup schedule, encryption and retention policy. The example Compose volume is for a local preview only.

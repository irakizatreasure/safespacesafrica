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

## Cyizere AI setup

Cyizere can use OpenAI (GPT) and Google Gemini, with an optional fallback provider. Each request goes to the primary provider first. The fallback is tried only if the primary request fails; the service does not send the same question to both providers when the first succeeds. Claude remains supported for existing deployments.

In Render, open the `umucyospacehub` web service, choose **Environment**, and add these environment variables. Use API keys created in the provider accounts; do not put them in GitHub, site JavaScript, chat, or this repository.

| Key | Example value | Type |
| --- | --- | --- |
| `SISP_AI_PROVIDER` | `openai` | Text |
| `SISP_AI_API_KEY` | Your OpenAI API key | Secret |
| `SISP_AI_MODEL` | `gpt-4.1-mini` | Text |
| `SISP_AI_FALLBACK_PROVIDER` | `gemini` | Text |
| `SISP_AI_FALLBACK_API_KEY` | Your Gemini API key | Secret |
| `SISP_AI_FALLBACK_MODEL` | `gemini-2.5-flash` | Text |

The model IDs above are examples. Confirm that each selected model is enabled in its API account before saving. To run with one provider, set the primary three values and leave the fallback variables empty. To prefer Gemini, use `gemini` as the primary and `openai` as the fallback, swapping the corresponding key and model variables. In Render, use **Save, rebuild, and deploy** after adding or changing variables.

OpenAI requests use the official Chat Completions API with server-side Bearer authentication and response storage disabled. Gemini requests use the official `generateContent` API with the API key in a server-side header. The key is never returned to the browser. User messages and the recent conversation are sent to whichever provider is called; the site does not save chat transcripts. Review each provider's current privacy, retention and billing settings before enabling the service.

Cyizere retrieves only language-matched `published` and `approved` lessons, FAQs, guides and page copy. Unreviewed drafts and candidate sources are excluded. The assistant will say when no reviewed site material answers the question. It is an educational tool, not clinical advice, legal advice, counselling, staffed support or emergency response. The app provides a simple availability status without revealing provider or key details. The automated checks do not make live provider calls.

## Database backup

See the online SQLite backup example and restore notes in [HANDOVER.md](HANDOVER.md). Before a production rollout, select a supported backup schedule, encryption and retention policy. The example Compose volume is for a local preview only.

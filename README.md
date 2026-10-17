# Safe Informational Spaces

A responsive, multilingual web application for the Safe Informational Spaces project. It includes a public website, learning-path catalogue, review-gated lesson and quiz content, accessible browser read-aloud, private on-device learning progress, sourced Rwanda help contacts, and a role-protected administrator workspace.

**Current handover status:** GitHub-ready source with automated checks and a production WSGI container/hosting blueprint. It has not been pushed to GitHub or deployed. The MVP still needs reviewed public content and real support operations before it can be offered as a complete youth service. See [Feature status and handover](docs/HANDOVER.md).

## Run locally

Requires Python 3.10 or later; the application uses only the Python standard library.

```bash
cd safe-informational-spaces
cp .env.example .env
```

Edit `.env` and replace the sample CEO email/password with a real administrator email and a unique password of at least 14 characters. Do not commit `.env`. On first startup the app creates the SQLite database and seeds starter content. The default database is `./data/sisp.sqlite3`.

Run:

```bash
set -a
. ./.env
set +a
python app.py
```

Open `http://127.0.0.1:8000`. If the database has already been created, changing the initial CEO variables will not reset the existing password. Use the offline account tool to add administrators:

```bash
python manage_admin.py reviewer@example.org --role subject_matter_reviewer
```

The tool prompts for a password without putting it in shell history. Available roles are listed by `python manage_admin.py --help`.

### Docker

```bash
cp .env.example .env
# Edit .env first, then:
docker compose up --build
```

The Compose file binds only to localhost. The container uses Gunicorn; public deployment should use the hosting instructions below, persistent protected storage, HTTPS and monitoring.

## GitHub and hosting

The project is ready to place in a GitHub repository. GitHub Actions runs Python tests and syntax checks on pushes and pull requests to `main`. Create an empty repository on GitHub, then from this project directory run:

```bash
git init -b main
git add .
git commit -m "Prepare Safe Informational Spaces"
git remote add origin https://github.com/OWNER/REPOSITORY.git
git push -u origin main
```

Replace `OWNER/REPOSITORY` with the repository path. Do not commit `.env`, database files, or production secrets.

This is a full-stack Python application. GitHub Pages can serve static files but cannot run this app's Python API, database, admin dashboard, or AI endpoint. For a working deployment, connect the GitHub repository to a compatible application host. The included `render.yaml` is a Render Blueprint for the app, its health check, secure-cookie mode, a persistent database disk, and deploys from `main` after GitHub checks pass. It selects Frankfurt for the Rwanda audience and a paid Starter service because persistent disks are required to retain admin and content data. Review current hosting charges before creating resources. Follow [Deployment and environment configuration](docs/DEPLOYMENT.md).

## Languages and content

The public interface, initial pages, all six age tracks, 30 lesson drafts, five quiz prompts per lesson in each of three languages (450 localized question records), 15 FAQs, 9 guide drafts, and 9 source-candidate records are seeded in English, Kinyarwanda and French. Re-running the seed is idempotent. The educational items are tagged **AI-generated — pending authorized editorial and subject-matter review**. Draft body text and quiz answers are only returned to authorized admins; public pages show the topic outline and review status. A reviewer must approve the item and a CEO or President must publish it before the full text appears publicly or becomes eligible for Cyizere retrieval.

The quizzes are a starter learning aid and use a repeated safety-and-information literacy set per track; they need lesson-specific editorial improvement before launch. Kinyarwanda and French drafts also require a fluent human review.

## Admin workflow

1. Sign in at `/admin` with the configured account.
2. Open **Content review** and select a page, lesson, FAQ, guide or resource candidate.
3. An editor can save drafts or submit for review. A subject-matter reviewer can mark an item approved. A CEO or President can publish approved content.
4. Only CEO and President roles can create, update, reorder, activate or remove public team profiles. This is enforced in the API as well as the interface.
5. Feature statuses can be changed in **Feature status**. Do not mark a feature live unless its real service and launch checks are complete.
6. Provision additional roles through `manage_admin.py`; self-service account creation is disabled.

Page copy, lesson, FAQ, guide and source-candidate text can be edited in the database-backed content review tool. Content changes are not live until published by an authorized account. The homepage hero/layout and navigation structure are code-defined. The admin workspace does not yet include content version history, rollback, role-management UI or autosave.

## Architecture

- Python WSGI application using standard library modules for application code; Docker production serving uses pinned Gunicorn.
- SQLite database with idempotent startup seeding and server-side API authorization.
- Static HTML, CSS and JavaScript frontend with responsive navigation and accessible controls.
- No third-party frontend bundles and no external font dependency.
- Optional server-side AI adapter for OpenAI-compatible Chat Completions or Google Gemini. It uses only approved, published platform lessons, does not store conversations, and will report unavailable when provider configuration or reviewed knowledge is missing.
- LocalStorage learning progress remains on the visitor's device and is not sent to the server.

## Verification

Run the automated checks:

```bash
python -m unittest discover -s tests -v
```

Syntax check:

```bash
python -m py_compile app.py content_seed.py init_db.py manage_admin.py wsgi.py
node --check static/app.js
```

## Security and privacy notes

- No default administrator credentials are created. Initial CEO provisioning requires environment values before first startup.
- Passwords use PBKDF2-HMAC-SHA256; sessions use random opaque tokens stored as hashes, expire after eight hours, and are `HttpOnly` and `SameSite=Strict`.
- Unsafe admin requests require a matching double-submit CSRF token. Basic per-process rate limits cover login and AI requests.
- Response headers include a restrictive CSP and anti-framing/nosniff controls. Set `SISP_COOKIE_SECURE=true` behind HTTPS.
- Use HTTPS, a hardened host, persistent protected database volume, backups and monitoring before any public deployment. The built-in WSGI server is for local evaluation only; the container entry point uses Gunicorn.
- The application does not accept contact or safeguarding narratives while no monitored staff inbox is configured. The AI endpoint does not persist prompts, but application hosting/network logs may still record request metadata; do not enter identifying details.
- Do not use this application to store safeguarding case notes. A restricted safeguarding subsystem has not been implemented.

## Official help contacts shown in the app

The Rwanda Government emergency page lists 112 (Emergency), 3512 (Gender Based Violence) and 116 (Child Help Line): [Government of Rwanda — Emergency](https://www.gov.rw/emergency). The Rwanda Investigation Bureau lists 3029 for Isange One Stop Centre: [RIB — Contact Us](https://www.rib.gov.rw/contact-us). The site records a check date of 17 October 2026 and shows the source next to every number. Reconfirm the service scope and availability directly before launch and on a scheduled review cycle.

The educational source candidates link directly to WHO adolescent health, UNESCO comprehensive sexuality education and UNICEF children's online safety pages. They are labelled candidates and are not treated as approved citations for generated lessons.

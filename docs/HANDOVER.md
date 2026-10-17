# Implementation and handover status

## Implemented in this local MVP

- Responsive public pages for home, about, team, services, learning, resources, search, help, contact, donations and administrator sign-in.
- English, Kinyarwanda and French interface/content seed packages.
- Six age pathways, five lesson drafts in each pathway, five quiz questions attached to each lesson, topic FAQs and guides.
- Review gating: draft text stays behind the administrator API. Public users can see the curriculum map; full lesson body/quizzes appear after authorized approval and publication.
- Guest learning path navigation, quiz UI for published items, read-aloud using the browser speech API, and device-only completion progress. Local XP, learning levels, completion badges, and private text certificates award points only for lesson completion.
- Official help contacts 112, 3512, 116 and 3029 with source links and a verification date.
- Search over public approved content plus public service and learning pathway descriptions.
- Server-side admin sign-in, hashed passwords, expiring hashed sessions, CSRF token checks, rate limits, audit events, content state transition checks and Team CEO/President API enforcement.
- Admin content editing/review, team profile CRUD for CEO/President, feature-status editing and audit view.
- Optional server-side OpenAI-compatible/Gemini request code; no API key is sent to the browser. Retrieval is restricted to approved and published lessons.
- Stateless USSD menu adapter endpoint for short non-sensitive educational/help menu responses; no telecom service code is assigned or connected.
- GitHub Actions CI, a Gunicorn-based production container, production startup checks, and an unapplied Render Blueprint with a persistent SQLite disk.
- Environment example, database setup, administrator guide, backup notes and automated tests.

## Not implemented or not verified; do not represent as operational

- Production deployment to GitHub/Render, HTTPS verification, monitoring, alerting, backup restoration, load testing or independent penetration testing. The GitHub workflow has not run on a remote repository and the Render Blueprint has not been applied.
- PostgreSQL; the local app and Render pilot blueprint use SQLite. A production PostgreSQL migration and operational policy are still required for scale and multi-worker use.
- User registration, account recovery, MFA, user privacy export/deletion, consent ledger, saved resources on an account or server-side learning profiles.
- Human support inbox, staffed chat, notifications, voice calls/WebRTC, call queue or safeguarding case management. The public UI says these are unavailable and does not simulate a human response.
- Contact form submission; donations/payment provider, transaction verification, webhook processing, refunds or receipts.
- Official external reporting integration; no report is submitted by this site.
- Telecom gateway, USSD service code, end-to-end provider testing.
- Verified educational review by local health, legal, safeguarding or curriculum experts. All seed materials are clearly pending review. Emergency numbers are sourced from current official pages but their operational availability still needs pre-launch reconfirmation.
- Complete WCAG 2.2 AA audit, professional translation review, age/curriculum review, AI safety evaluation across all languages, robust multi-process rate limiting, dependency scanning, incident-response operations and data-retention enforcement.
- Content history/version comparison/rollback, autosave, admin role-management UI, translation workflow, file/image upload controls, PDF certificate generation, configurable game thresholds, topic challenges, advanced analytics and external notifications.

## Required environment variables

- `SISP_ADMIN_EMAIL`, `SISP_ADMIN_PASSWORD`: first-run CEO bootstrap; use a unique password of at least 14 characters.
- `SISP_HOST`, `SISP_PORT`, `SISP_DB_PATH`: listen address and database path.
- `SISP_COOKIE_SECURE=true`: set behind HTTPS.
- `SISP_AI_PROVIDER=openai|gemini`, `SISP_AI_API_KEY`, `SISP_AI_MODEL`: all required to enable the AI request path. Approved published source material is also required. `SISP_AI_BASE_URL` optionally changes the OpenAI-compatible endpoint.

Secrets must be supplied by a production secret manager or protected environment configuration. Never commit `.env`.

## Data backup

Stop the local service or use SQLite's online backup API from a trusted shell before copying the database. Example:

```bash
python - <<'PY'
import sqlite3
source = sqlite3.connect('data/sisp.sqlite3')
target = sqlite3.connect('data/sisp-backup.sqlite3')
source.backup(target)
target.close()
source.close()
PY
```

Keep backups encrypted and access-restricted. A successful backup/restore drill has not been performed for a production environment. Restore by stopping the service, preserving the current database, replacing it with the verified backup, then checking `/api/health` and content counts.

## Launch prerequisites

Before any public launch, configure real organization contact and support operations, obtain required legal/privacy review, verify emergency/referral availability, review/approve every sensitive translation and lesson, deploy on a supported production stack with HTTPS and PostgreSQL or another reviewed DB, configure monitoring/backups, and run the security, accessibility and safeguarding tests that this local MVP does not cover.

# Umucyo Spaces Hub: implementation and handover status

## Implemented in this working tree

- Responsive public pages for home, about, team, services, learning, resources, search, help, contact, donations and administrator sign-in.
- English, Kinyarwanda and French interface/content seed packages.
- Six age pathways, five lesson drafts in each pathway, five quiz questions attached to each lesson, topic FAQs and guides.
- Review gating: draft text stays behind the administrator API. Public users can see the curriculum map; full lesson body/quizzes appear after authorized approval and publication.
- Guest learning path navigation, quiz UI for published items, browser read-aloud, and device-only guest progress. Optional pseudonymous accounts can log in, save lesson completion in Postgres, and delete the account and saved progress. Local XP, badges, and private text certificates remain learning aids only.
- Official help contacts 112, 3512, 116 and 3029 with source links and a verification date.
- Search over public approved content plus public service and learning pathway descriptions.
- Server-side admin/staff sign-in, hashed passwords, expiring hashed sessions, CSRF token checks, rate limits, audit events, content state transition checks and role enforcement. CEO-only staff application approval confirms each applicant name and role; the CEO can add/remove leadership positions and disable staff accounts.
- Admin content editing/review, educator lesson-draft creation for professional review, team profile CRUD for CEO/President, feature-status editing, staff approvals, leadership-position management and audit view.
- Optional server-side OpenAI, Gemini and Claude integrations; the organization selects a primary and optional fallback provider and stores API keys on the host. No key is sent to the browser. Cyizere can answer general questions and use approved, published site information when relevant.
- Encrypted client/staff text support: a new request enters an assistant-first queue; clients submit a full name, exact age and opening message encrypted from their browser; assigned staff can exchange encrypted text and up to 3 MB image/audio/video attachments, see online/typing presence, receive optional browser alerts, and transfer the chat with its encrypted history to another staff member. The client can resume with the current staff member or return the conversation to the assistant queue. Closing the client panel clears visible messages and pauses the thread; encrypted server history remains for resuming.
- Human chat status and message updates use four-second polling; notifications require the staff member to opt in in that browser. Browser encryption keys are stored in that browser's IndexedDB and are not recoverable if that browser data is cleared. A staff member who has already read a message may remember or retain it after transfer.
- Stateless USSD menu adapter endpoint for short non-sensitive educational/help menu responses; no telecom service code is assigned or connected.
- GitHub Actions CI, a Gunicorn-based production container, production startup checks, and a live Render deployment connected to Supabase Postgres.
- Keyboard-accessible high contrast, scalable text, browser read-aloud and Escape-to-close controls, plus a lazy-loaded OpenStreetMap reference for the University of Rwanda Huye Campus. Environment example, database setup, administrator guide, backup notes and automated tests.

## Implemented but not verified for live use; do not overstate readiness

- The existing hosted pilot is at [umucyospacehub.onrender.com](https://umucyospacehub.onrender.com/). The human-chat and latest Cyizere changes in this working tree have not been deployed or verified live. Monitoring, alerting, backup restoration, load testing and independent penetration testing are not verified.
- Supabase Postgres is used for hosted data; local development uses SQLite. A production backup and retention policy and multi-worker capacity plan still need review.
- Email/password recovery, MFA, privacy export, consent ledger, and saved resources. Member accounts use pseudonyms rather than email and can delete their account and saved learning progress.
- Staff availability and response coverage, voice calls/WebRTC, call queue, safeguarding case management, chat retention/deletion controls and key recovery are not implemented as operational services. Encrypted chat is a code feature; it does not itself provide qualified or continuously available staff.
- Contact form submission; donations/payment provider, transaction verification, webhook processing, refunds or receipts.
- Official external reporting integration; no report is submitted by this site.
- Telecom gateway, USSD service code, end-to-end provider testing.
- Verified educational review by local health, legal, safeguarding or curriculum experts. All seed materials are clearly pending review. Emergency numbers are sourced from current official pages but their operational availability still needs pre-launch reconfirmation.
- Complete WCAG 2.2 AA audit, professional translation review, age/curriculum review, AI safety evaluation across all languages, robust multi-process rate limiting, dependency scanning, incident-response operations and a formal data-retention schedule. The custom browser encryption has not had an independent security audit; it should not be described as certified or as protecting a user's device from malware or browser compromise.
- Content history/version comparison/rollback, autosave, file/image upload controls, PDF certificate generation, configurable game thresholds, topic challenges, advanced analytics and external notifications. Educators can enter lesson drafts in the staff workspace; file uploads are not implemented.

## Required environment variables

- `SISP_ADMIN_EMAIL`, `SISP_ADMIN_PASSWORD`: first-run CEO bootstrap; use a unique password of at least 14 characters.
- `SISP_HOST`, `SISP_PORT`, `SISP_DB_PATH`: listen address and database path.
- `SISP_COOKIE_SECURE=true`: set behind HTTPS.
- `SISP_AI_PROVIDER=openai|gemini|claude`, `SISP_AI_API_KEY`, `SISP_AI_MODEL`: all required to enable the AI request path. Approved published source material improves answers when available but is not required for general AI responses. `SISP_AI_BASE_URL` optionally changes the selected provider endpoint. Approved support staff must sign in and set up their encryption key in the same browser before accepting chats. Human chat is not emergency care and depends on staff being online; voice/calls remain unavailable.

Human chat asks clients for their full name and exact age, then stores encrypted message bodies and media, encrypted key envelopes, and metadata including language, timestamps, assignment, presence and typing. The chat form describes these practices before submission. Client and staff keys are browser-specific; clearing browser data can make chat history unreadable. The feature still needs organization privacy, legal, safeguarding and independent security review before wider use.

Secrets must be supplied by a production secret manager or protected environment configuration. Never commit `.env`.

## Data backup

For local development, stop the service or use SQLite's online backup API from a trusted shell before copying the database. Hosted data lives in Supabase Postgres; use its dashboard/export tools and establish an appropriate backup plan for that project. Example:

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

## Wider-launch prerequisites

Before wider public use, configure real organization contact and support operations, obtain required legal/privacy review, verify emergency/referral availability, review/approve every sensitive translation and lesson, review the production stack, database plan and HTTPS configuration, configure monitoring/backups, and run the security, accessibility and safeguarding tests that this local MVP does not cover.

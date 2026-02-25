# MedMatch-AI KARAU - AI-Powered Job Search Platform

## Product Requirements Document (PRD)

### Original Problem Statement
Create a comprehensive, AI-powered application named "MedMatch-AI KARAU" to automate remote job search with tools for resume parsing, job matching, and interview preparation. Includes the AI KARAU Meeting Portal for secure video conferencing.

---

## System Status (February 24, 2026)

| Component | Status | Details |
|-----------|--------|---------|
| **Backend** | Healthy | Version 2.2.0, AI Supervisor running |
| **Frontend** | Running | Webpack compiled, no errors |
| **Database** | Optimized | 82 collections, 56K docs, 9+ indexes |
| **Scheduled Maintenance** | Active | Weekly Sundays 9:00 UTC via Dragon Scheduler |
| **AI KARAU Meeting** | Verified | E2E 100% pass, Share Meeting feature |
| **Translations** | **99.2%** | 1,887 keys, 32 languages |

---

## Completed Features (This Session)

### 1. Share Meeting Feature
- Guest Join Page (`/karau-meet/join/{meetingId}`) - no account needed
- ShareMeetingDialog: copy link, .ics download, Google Calendar
- Share buttons on Dashboard, Create Meeting dialog, Meeting Room header
- Backend public endpoint: `GET /api/karau-meet/meetings/{id}/info`

### 2. Database Standardization & Debugging
- Audited 82 collections, verified ID format consistency (no duplicates)
- Fixed _id serialization leak in push.py
- Suppressed Xirsys TURN error logging (graceful STUN fallback)
- Created 9 new indexes for performance

### 3. Automated Scheduled Maintenance
- Extended Dragon Scheduler's `cleanup_old_data()` to also handle:
  - Expired user sessions
  - Stale meetings (waiting 7+ days → expired)
  - ML training data older than 30 days
  - Expired OAuth states and WebAuthn challenges
  - Expired email verification codes
- Runs automatically every Sunday at 9:00 AM UTC
- Manual trigger: `POST /api/admin-audit/database/maintenance`
- Health check: `GET /api/admin-audit/database/health`

---

## Completed Features (February 25, 2026)

### 4. ORCID OAuth Login
- "Sign in with ORCID" button on login page with official ORCID green branding (#A6CE39)
- Full OAuth 2.0 Authorization Code flow via popup window (production orcid.org)
- Backend endpoints: `GET /api/auth/orcid/config`, `GET /api/auth/orcid/login`, `GET /api/auth/orcid/callback`
- Auto-creates user account on first ORCID sign-in, links ORCID iD to profile
- OAuth states stored in MongoDB for load-balancer resilience
- Callback uses postMessage to communicate with opener window (iframe-compatible)
- ORCID Client ID: APP-K9HUYS6GQY2RERX6 (production)

### 5. Translation Hardening & QA Mitigator
- **Fixed hardcoded English in sidebars**: Replaced 20+ raw English strings with translation keys (`nav.*`, `recruiter.*`) in Admin, Job Seeker, and Recruiter sidebars (App.js)
- **Fixed ProfileBadgeShowcase**: All "Verified Badges", "Verified by:", "View all N badges" strings now use `t()` with `badges.*` keys
- **Fixed `{count}` placeholder errors**: Migrated all `{count}` → `{{count}}` in 33 locale files for proper i18n interpolation
- **Added Auto-Fix button**: Translation QA Dashboard now has "Auto-Fix Issues" mitigator button that triggers AI auto-translation for all languages below target KPI
- **Added progress banner**: Real-time progress indicator during auto-fix with language count and key translation stats
- **AI KARAU Meeting Portal language selector**: Added `GlobalLanguageSelector` to KARAU sidebar, translated all nav items (`karau.*` keys)
- **Translated 36 new keys** across all 32 languages using GPT-5.2 AI translation
- **0 missing keys** in all locale files after sync

---

## Backlog (Parked)

### P1
- LinkedIn Profile Sync
- PayPal Integration
- ORCID live user verification (user needs to test full flow)

### P2
- Enterprise SSO/SAML
- iOS Build
- Social Media Sharing (LinkedIn/Twitter share buttons)

---

## Key Technical Info
- **Admin:** admin@medmatch.com / Swampdrainer2026!
- **Scheduler:** Dragon Scheduler, 5 jobs, MongoDB-persisted (apscheduler_jobs)
- **Mocked:** Google and Apple social sign-in
- **ORCID OAuth:** Production (orcid.org), Client ID: APP-K9HUYS6GQY2RERX6
- **i18n:** 32 languages, 0 missing keys, `{{param}}` interpolation syntax, AI auto-fix via Translation QA Dashboard

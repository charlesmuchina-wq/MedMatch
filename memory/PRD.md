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

## Backlog (Parked)

### P1
- LinkedIn Profile Sync
- ORCID OAuth Login
- PayPal Integration

### P2
- Enterprise SSO/SAML
- iOS Build

---

## Key Technical Info
- **Admin:** admin@medmatch.com / Swampdrainer2026!
- **Scheduler:** Dragon Scheduler, 5 jobs, MongoDB-persisted (apscheduler_jobs)
- **Mocked:** Google and Apple social sign-in

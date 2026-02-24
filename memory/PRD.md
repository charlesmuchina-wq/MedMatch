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
| **Database** | Optimized | 82 collections, 56K docs, indexes added |
| **Authentication** | Working | Login, sessions, all view modes |
| **AI KARAU Meeting** | VERIFIED | E2E 100% pass, Share Meeting feature added |
| **Share Meeting** | NEW | Guest join, share dialog, calendar invite |
| **Translations** | **99.2% COVERAGE** | 1,887 UI keys, 32 languages |

---

## Database Standardization (February 24, 2026) - COMPLETE

### ID Format Summary
| Entity | Format | Example | Unique Index |
|--------|--------|---------|--------------|
| Users | `user_{12hex}` | `user_18ce8d3c6541` | Yes (user_id, email) |
| Meetings | 8-char uppercase hex | `D65B1523` | Yes (meeting_id) |
| Applications | UUID v4 | `358d6c4f-d642-...` | Yes (id) |
| Sessions | Token string | `H_A5te5v2B-...` | Yes (session_token) |

### Maintenance Performed
- Cleaned 2,417 expired sessions (2,822 → 408)
- Expired 50 stale meetings (waiting 7+ days)
- Cleaned 4 expired OAuth states
- Created 9 new database indexes
- Fixed _id serialization in push.py
- Suppressed Xirsys TURN error logging (graceful STUN fallback)
- No duplicate IDs found in any collection
- No _id serialization issues in API responses

### New Admin Endpoints
- `POST /api/admin-audit/database/maintenance` - Run cleanup + index creation
- `GET /api/admin-audit/database/health` - DB health report with recommendations

---

## Backlog (Prioritized)

### P1 - Next Up
- LinkedIn Profile Sync
- ORCID OAuth Login
- PayPal Integration

### P2 - Future
- Enterprise SSO/SAML
- iOS Build
- Live multi-user WebRTC test

---

## Key Technical Info
- **Admin credentials:** admin@medmatch.com / Swampdrainer2026!
- **Language localStorage key:** medmatch-language
- **Guest localStorage key:** karau_guest
- **Translation benchmark API:** GET /api/translation-qa/benchmark
- **DB Maintenance API:** POST /api/admin-audit/database/maintenance
- **Mocked:** Google and Apple social sign-in

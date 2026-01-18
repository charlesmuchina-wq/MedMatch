# MedMatch - AI-Powered Job Search Platform

## Product Requirements Document (PRD)

### Original Problem Statement
Create a comprehensive, AI-powered application named "MedMatch" to automate remote job search. The application should parse a resume, find matching jobs from various sources, and provide tools to aid in the application process.

### Core Requirements
1. **Resume Management**: Parse PDF/DOC/DOCX resumes with AI
2. **Job Sourcing**: Aggregate jobs from JobSpy, Google CSE
3. **Authentication**: Google, Apple, Email, Phone (SMS), **Biometric (WebAuthn)**
4. **Membership & Payments**: Stripe integration
5. **AI Features**: KARAU DRAGON AI, Cover Letter Generator, Interview Prep, Voice Coach
6. **Multi-Language Support**: 39 languages across EFIGS, CJK, and Expanding Markets
7. **Biometric Verification**: WebAuthn/FIDO2 passwordless authentication
8. **Offline Capabilities**: IndexedDB caching for offline access

---

## What's Been Implemented

### Session: January 18, 2026

#### ✅ P1: Biometric Login Integration (COMPLETED)
- **Login Page**: Added Biometric tab (3rd tab alongside Email and Phone)
- **BiometricLogin**: Email input + "Login with Biometrics" button integrated
- **BiometricRegistration**: Name/Email inputs + "Register with Biometrics" flow
- **Fixed Bug**: `AttestationConveyancePreference.NONE` enum usage in biometric.py
- **Testing**: 100% pass rate on all biometric endpoints

#### ✅ P1: Offline Capabilities Integration (COMPLETED)
- **OfflineIndicator**: Compact status indicator added to app header (shows Online/Offline)
- **OfflineBanner**: Full-width banner shows when user goes offline/online
- **IndexedDB Caching**: 
  - Jobs caching on fetch
  - Resume caching on fetch
  - User data caching on login
  - Offline action queueing for job saves
- **Auto-sync**: Pending actions sync when back online

#### ✅ Q&A Practice Timeout Fix (VERIFIED)
- `/api/qa-practice/common-questions` endpoint now has fallback questions
- Returns static questions if LLM API times out

### Session: January 17, 2026

#### ✅ Multi-Language Translation System (COMPLETED)
- **Backend**: `/app/backend/routes/translation.py`
  - 39 supported languages organized by strategic clusters
  - EFIGS Foundation: English, Spanish, French, German, Italian
  - CJK Growth Block: Chinese (Simplified/Traditional), Japanese, Korean
  - Rapidly Expanding Markets: Hindi, Portuguese (Brazilian), Arabic
- **Frontend**: 
  - `GlobalLanguageSelector.jsx` - Header language selector
  - `TranslationWidget.jsx` - Inline translation component

#### ✅ Biometric Authentication Backend (COMPLETED)
- **Backend**: `/app/backend/routes/biometric.py`
  - WebAuthn/FIDO2 registration and authentication
  - Challenge-response ceremony implementation
  - Credential storage in MongoDB
  - Bot prevention and fraud detection endpoints

#### ✅ Q&A Interview Practice (COMPLETED)
- **Backend**: `/app/backend/routes/qa_practice.py`
- **Frontend**: `/app/frontend/src/pages/QAPracticePage.jsx`
- AI-driven feedback, voice recording, audio upload, PDF export

---

## Architecture

```
/app/
├── backend/
│   ├── routes/
│   │   ├── auth.py          # Email, Google, Apple, Phone auth
│   │   ├── biometric.py     # WebAuthn/FIDO2 auth
│   │   ├── translation.py   # 39-language support
│   │   ├── qa_practice.py   # Q&A Interview Practice
│   │   ├── dragon.py        # KARAU DRAGON AI
│   │   ├── jobs.py          # Job search & matching
│   │   ├── resume.py        # Resume upload (PDF/DOC/DOCX)
│   │   ├── video_interview.py  # Placeholder
│   │   ├── push_notifications.py  # Placeholder
│   │   ├── id_verification.py  # Placeholder
│   │   └── ... (more route modules)
│   └── server.py            # 226 lines, modular
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── BiometricAuth.jsx
│   │   │   ├── GlobalLanguageSelector.jsx
│   │   │   ├── OfflineIndicator.jsx
│   │   │   ├── TranslationWidget.jsx
│   │   │   └── KarauDragonAI.jsx
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx  # 3 tabs: Email, Phone, Biometric
│   │   │   ├── QAPracticePage.jsx
│   │   │   └── ... (20+ pages)
│   │   ├── utils/
│   │   │   └── offlineStorage.js  # IndexedDB caching
│   │   └── App.js (with OfflineBanner, OfflineIndicator)
└── memory/
    └── PRD.md
```

---

## Prioritized Backlog

### P0 - Critical (DONE)
- [x] Multi-language support (39 languages)
- [x] Biometric authentication backend
- [x] Biometric authentication frontend
- [x] Integrate BiometricLogin into login page ✅ Jan 18

### P1 - High Priority
- [x] Offline capabilities (IndexedDB caching) ✅ Jan 18
- [ ] Apple Sign In (blocked on user Apple Developer Console config)
- [ ] OneDrive integration (needs Microsoft app registration)
- [ ] Dropbox integration (needs Dropbox app registration)

### P2 - Medium Priority (READY FOR IMPLEMENTATION)
- [ ] Video Interview Recording (placeholder at `/app/backend/routes/video_interview.py`)
- [ ] Push Notifications (placeholder at `/app/backend/routes/push_notifications.py`)
- [ ] Recruiter ID Verification - Persona + Jumio (placeholder at `/app/backend/routes/id_verification.py`)
- [ ] PayPal integration (deprioritized, blocked on credentials)

### P3 - Future
- [ ] Native Windows/Desktop widget
- [ ] LinkedIn profile sync
- [ ] Application feedback learning
- [ ] Advanced fraud scoring

---

## Test Reports
- `/app/test_reports/iteration_14.json` - 92% pass rate (before P1 fix)
- `/app/test_reports/iteration_15.json` - 100% pass rate (after P1 implementation)

## Test Credentials
- **Admin**: admin@medmatch.com / MedMatch2026!
- **Recruiter**: recruiter@medmatch-test.com / test123

---

## Technical Notes

### Biometric Implementation
- Uses py_webauthn library for FIDO2 compliance
- Platform authenticator preference (fingerprint/face)
- Challenge expiration: 10 minutes
- Sign count tracking for clone detection
- Fixed: Uses `AttestationConveyancePreference.NONE` enum

### Offline Storage Architecture
- Database: IndexedDB (medmatch-offline)
- Stores: cached_jobs, cached_resume, cached_user, cached_messages, pending_actions, sync_metadata
- Auto-sync on reconnection
- Action queueing for offline saves

### Dependencies
- webauthn: 2.7.0
- slowapi: 0.1.9
- python-docx: 1.2.0
- idb (frontend): IndexedDB wrapper
- jsPDF (frontend): PDF generation

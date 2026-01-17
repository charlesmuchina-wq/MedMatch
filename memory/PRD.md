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

---

## What's Been Implemented

### Session: January 17, 2026

#### ✅ Multi-Language Translation System (COMPLETED)
- **Backend**: `/app/backend/routes/translation.py`
  - 39 supported languages organized by strategic clusters
  - EFIGS Foundation: English, Spanish, French, German, Italian
  - CJK Growth Block: Chinese (Simplified/Traditional), Japanese, Korean
  - Rapidly Expanding Markets: Hindi, Portuguese (Brazilian), Arabic
  - Additional: Tamil, Telugu, Marathi, Urdu, Persian, Swahili, etc.
- **Frontend**: 
  - `GlobalLanguageSelector.jsx` - Header language selector with context
  - `TranslationWidget.jsx` - Inline translation component
  - Integrated into CoverLetterPage, JobCard, MessagesPage, SkillAssessmentsPage

#### ✅ Biometric Authentication (COMPLETED)
- **Backend**: `/app/backend/routes/biometric.py`
  - WebAuthn/FIDO2 registration and authentication
  - Challenge-response ceremony implementation
  - Credential storage in MongoDB
  - Bot prevention and fraud detection endpoints
- **Frontend**: `/app/frontend/src/components/BiometricAuth.jsx`
  - BiometricRegistration component
  - BiometricLogin component
  - SecurityBadge for verified users

#### ✅ Resume Upload Enhancement (COMPLETED)
- DOC/DOCX file support added to backend
- Updated ResumePage to accept PDF, DOC, DOCX files
- Improved file validation and error messages

#### ✅ Cloud Storage Integration (VERIFIED)
- Google Drive picker working (green checkmark)
- OneDrive/Dropbox placeholders ready for configuration

---

## Architecture

```
/app/
├── backend/
│   ├── routes/
│   │   ├── auth.py          # Email, Google, Apple, Phone auth
│   │   ├── biometric.py     # NEW: WebAuthn/FIDO2 auth
│   │   ├── translation.py   # 39-language support
│   │   ├── dragon.py        # KARAU DRAGON AI
│   │   ├── jobs.py          # Job search & matching
│   │   ├── resume.py        # Resume upload (PDF/DOC/DOCX)
│   │   ├── cloud.py         # Cloud storage integration
│   │   └── ... (14 more route modules)
│   └── server.py            # 220 lines, modular
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── BiometricAuth.jsx     # NEW
│   │   │   ├── GlobalLanguageSelector.jsx  # NEW
│   │   │   ├── TranslationWidget.jsx
│   │   │   ├── KarauDragonAI.jsx
│   │   │   └── CloudStorageUpload.jsx
│   │   └── pages/ (20+ pages)
│   └── App.js (with LanguageProvider)
└── memory/
    └── PRD.md
```

---

## API Endpoints

### Biometric Authentication
- `GET /api/biometric/supported` - Check WebAuthn support
- `POST /api/biometric/register/start` - Start registration
- `POST /api/biometric/register/complete` - Complete registration
- `POST /api/biometric/authenticate/start` - Start login
- `POST /api/biometric/authenticate/complete` - Complete login
- `GET /api/biometric/credentials` - List user's credentials
- `DELETE /api/biometric/credentials/{id}` - Remove credential

### Translation
- `GET /api/translate/languages` - List 39 supported languages
- `POST /api/translate/text` - Translate text
- `POST /api/translate/detect` - Detect language

---

## Prioritized Backlog

### P0 - Critical
- [x] Multi-language support (39 languages)
- [x] Biometric authentication backend
- [x] Biometric authentication frontend
- [ ] Integrate BiometricLogin into login page

### P1 - High Priority
- [ ] Apple Sign In (blocked on user Apple Developer Console config)
- [ ] OneDrive integration (needs Microsoft app registration)
- [ ] Dropbox integration (needs Dropbox app registration)
- [ ] Push notifications for job alerts

### P2 - Medium Priority
- [ ] PayPal integration (deprioritized)
- [ ] ID verification for recruiters (Persona/Veriff)
- [ ] LinkedIn profile sync

### P3 - Future
- [ ] Native Windows/Desktop widget
- [ ] Application feedback learning
- [ ] Advanced fraud scoring

---

## Test Credentials
- **Admin**: admin@medmatch.com / MedMatch2026!
- **Recruiter**: recruiter@medmatch-test.com / test123

---

## Technical Notes

### Language Clusters Strategy
1. **EFIGS Foundation** - Core global reach (EN, ES, FR, DE, IT)
2. **CJK Growth Block** - High spend markets (ZH, JA, KO)
3. **Rapidly Expanding** - Next wave growth (HI, PT-BR, AR)

### Biometric Implementation
- Uses py_webauthn library for FIDO2 compliance
- Platform authenticator preference (fingerprint/face)
- Challenge expiration: 10 minutes
- Sign count tracking for clone detection

### Dependencies Added
- webauthn: 2.7.0
- slowapi: 0.1.9
- python-docx: 1.2.0

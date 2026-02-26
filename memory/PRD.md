# MedMatch-AI KARAU - Product Requirements Document

## Original Problem Statement
MedMatch-AI KARAU: AI-powered Life Sciences & Engineering Talent Ecosystem with enterprise video conferencing (AI KARAU portal).

---

## System Status (February 26, 2026)

| Component | Status |
|-----------|--------|
| Backend | Healthy - All routes return proper auth codes |
| Frontend | Running - 5-tab Settings, 3-step Guest Flow |
| AI KARAU Meeting | Full enterprise video platform |
| Translations | 99%+ (50 languages) |
| PWA/iOS | Configured with KARAU branding |

---

## All Completed Features

### Core Video Meeting
- Pre-Meeting Lobby with device preview + host waiting room
- Skin Tone Protection for inclusive video
- Host Moderation: Mute Participant, Mute All, Pass Mic
- Active Speaker Highlighting (Web Audio API)
- Breakout Rooms with AI auto-assignment + timers
- Screen Sharing

### Enterprise (Phase 1-2)
- 5-tier licensing model (Free → Enterprise)
- Company branding (logo/watermark)
- Verified email domains
- Conference room management
- Employee directory with CSV import + LDAP/AD sync
- Organization admin panel

### Guest Security (Phase 3)
- 3-step guest verification: Email → OTP → Age declaration (16+)
- Production email via Resend (fallback _dev_otp for testing)
- 6-digit OTP with 10-min expiry, 5-attempt limit, 60s resend cooldown

### Calendar & Sharing (Backlog)
- ICS calendar export
- Social sharing: LinkedIn, Twitter/X, WhatsApp, Email
- Google Calendar direct link
- Enhanced ShareMeetingDialog

### Calendar Integration
- Microsoft Outlook/365 OAuth infrastructure (needs Azure AD credentials)
- Google Calendar OAuth infrastructure (needs Google Cloud credentials)
- Apple Calendar always available via .ics
- Calendar Settings tab with connect/disconnect UI

### Enterprise SSO/SAML
- Full SAML 2.0 Service Provider implementation
- SSO configuration CRUD (admin only)
- SAML login flow + Assertion Consumer Service
- SP metadata XML endpoint
- Email-based SSO discovery
- Supports: Okta, Azure AD, OneLogin, Google Workspace, PingIdentity, Auth0, Duo, JumpCloud
- SSO/SAML Settings tab with IdP configuration form

### Auth Error Fix
- Created `require_auth` dependency (raises 401 instead of returning None)
- Applied to ALL 54+ route files
- Protected endpoints now return proper 401/403 instead of 500

### PWA/iOS
- Updated manifest.json with KARAU branding
- iOS-specific meta tags (apple-mobile-web-app-capable, status-bar-style)
- Meeting-focused shortcuts

### Testing & Documentation
- LDAP integration test scripts
- Live multi-user test guide (/app/memory/docs/live-test-guide.md)
- 3 test iterations this session: 114, 115, 116 (all 100% pass)

---

## Remaining Tasks

### Activation Required (User Action)
- **Microsoft Calendar**: Set `MS_CALENDAR_CLIENT_ID` + `MS_CALENDAR_CLIENT_SECRET` in backend .env
- **Google Calendar**: Set `GOOGLE_CALENDAR_CLIENT_ID` + `GOOGLE_CALENDAR_CLIENT_SECRET` in backend .env
- **SSO/SAML**: Configure IdP in Settings → SSO/SAML tab
- **LDAP**: Test against live Active Directory server

### Human-Led Testing
- Live multi-user E2E meeting test (see /app/memory/docs/live-test-guide.md)

---

## Key Info
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test User: test@medmatch.io / TestPassword123!
- Org: org_5a18c854f810 (MedMatch Inc)
- Mocked: Microsoft/Google Calendar OAuth, SSO/SAML IdP, Resend email (test key), LDAP sync

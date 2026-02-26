# MedMatch-AI KARAU - Product Requirements Document

## Original Problem Statement
MedMatch-AI KARAU: AI-powered Life Sciences & Engineering Talent Ecosystem with secure video conferencing.

---

## System Status (February 26, 2026)

| Component | Status |
|-----------|--------|
| Backend | Healthy |
| Frontend | Running |
| AI KARAU Meeting | Full-featured enterprise video platform |
| Translations | 99%+ (50 languages) |

---

## Completed This Session

### Auth Error Fix (P2 → DONE)
- Created `require_auth` dependency in auth.py that raises HTTPException(401) instead of returning None
- Applied to karau_ai, karau_organizations, karau_recordings, karau_security routes
- /api/auth/me and /api/auth/preferences now return proper 401 for unauthenticated requests

### Calendar Integration (P1 → DONE)
- Backend: `/api/karau-meet/calendar/status` - Shows connected providers and configuration status
- Backend: `/api/karau-meet/calendar/microsoft/connect` - Microsoft OAuth flow (needs Azure credentials)
- Backend: `/api/karau-meet/calendar/sync` - Push meetings to connected calendar
- Backend: `/api/karau-meet/calendar/disconnect` - Remove calendar connection
- Frontend: New "Calendar" tab in Settings with Microsoft Outlook, Apple Calendar, Google Calendar providers
- Apple Calendar always available via .ics export, Google via direct link

### Enterprise SSO/SAML (P1 → DONE)
- Backend: Full SAML 2.0 SP implementation
  - `/api/karau-meet/sso/configure` - Admin configures IdP settings
  - `/api/karau-meet/sso/config/{org_id}` - CRUD for SSO config
  - `/api/karau-meet/sso/login/{org_id}` - Initiates SAML login
  - `/api/karau-meet/sso/acs` - Assertion Consumer Service
  - `/api/karau-meet/sso/metadata` - SP metadata XML
  - `/api/karau-meet/sso/discover` - Email-based SSO discovery
- Frontend: New "SSO/SAML" tab in Settings with SP details and IdP configuration form
- Supports: Okta, Azure AD, OneLogin, Google Workspace, PingIdentity, Auth0, Duo, JumpCloud

### Phase 3: Guest 2FA + Age Verification (DONE)
- Multi-step guest verification: Email+Name → OTP → Age declaration (16+)
- Backend endpoints: register, verify-otp, age-declaration, resend-otp, status

### Backlog: Calendar & Social Sharing (DONE)
- ICS export, social sharing (LinkedIn, Twitter/X, WhatsApp, Email, Facebook)
- Enhanced ShareMeetingDialog

### Previously Completed
- Phase 1: Enterprise Tier System (5 tiers, domain verification, conference rooms, branding)
- Phase 2: Employee Directory + LDAP (CSV import, LDAP/AD sync, employee CRUD)
- Video Features: Pre-Meeting Lobby, Skin Tone Protection, Host Controls, Active Speaker, Breakout Rooms

---

## Next Tasks

### P1: Live Multi-User KARAU Meeting Test
- Guide user through E2E test with multiple users/devices
- Validate WebRTC, lobby, host controls, breakout rooms in real-world

### P1: Microsoft Calendar Activation
- User needs to provide Azure AD app credentials (MS_CALENDAR_CLIENT_ID, MS_CALENDAR_CLIENT_SECRET)
- Then Microsoft OAuth flow will be fully functional

### P1: SSO/SAML Activation
- User needs to configure their Identity Provider and provide IdP details
- Then SAML login flow will be fully functional

### P2: Extend require_auth to remaining routes
- Apply require_auth to all remaining route files (40+ files) for consistent auth behavior

### P2: iOS App Build

### P3: MeetingHeader Component Refactoring

## Key Info
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test User: test@medmatch.io / TestPassword123!
- Org: org_5a18c854f810 (MedMatch Inc, Grande, 17 employees)
- Mocked: Google/Apple social sign-in, LDAP sync, Email OTP (_dev_otp), Microsoft Calendar (no Azure creds), SSO (no live IdP)

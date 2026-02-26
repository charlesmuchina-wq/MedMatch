# MedMatch-AI KARAU - Product Requirements Document

## Original Problem Statement
MedMatch-AI KARAU: AI-powered Life Sciences & Engineering Talent Ecosystem with secure video conferencing.

---

## System Status (February 26, 2026)

| Component | Status |
|-----------|--------|
| Backend | Healthy |
| Frontend | Running |
| AI KARAU Meeting | Lobby, Skin Tone, Mute, Active Speaker, Breakout Rooms, Enterprise Tiers, Employee Directory, Guest 2FA, Calendar/Social Sharing |
| Translations | 99%+ (50 languages) |

---

## Completed This Session

### Phase 3: Guest 2FA + Age Verification (DONE)
- Multi-step guest verification flow (3 steps: Details → Verify → Confirm)
- Email OTP verification with 6-digit code, 10-min expiry, 5-attempt limit
- Age self-declaration gate (16+ per Zoom/Teams standard)
- Resend OTP with 60s cooldown, paste support for OTP codes
- Backend: `/api/karau-meet/guest/register`, `/verify-otp`, `/age-declaration`, `/resend-otp`, `/status`

### Backlog: Calendar & Social Sharing (DONE)
- ICS calendar export: `/api/karau-meet/share/calendar/{meetingId}.ics`
- Social sharing links API: `/api/karau-meet/share/social/{meetingId}`
- Enhanced ShareMeetingDialog with LinkedIn, Twitter/X, WhatsApp, Email buttons
- Google Calendar integration link
- Backend + frontend fully integrated

### Previously Completed
- **Phase 1: Enterprise Tier System** - 5 tiers, domain verification, conference rooms, company branding
- **Phase 2: Employee Directory + LDAP** - CSV import, LDAP/AD sync, employee CRUD
- **Video Features** - Pre-Meeting Lobby, Skin Tone Protection, Host Mute Controls, Active Speaker, Breakout Rooms

---

## Next Tasks

### P1: Live Multi-User KARAU Meeting Test
- Guide user through E2E test with multiple users/devices
- Validate WebRTC, lobby, host controls, breakout rooms in real-world

### P1: Calendar Integration (Microsoft, iOS)
- Two-way sync with Microsoft Outlook/365
- iOS Calendar integration

### P1: Enterprise SSO/SAML
- SAML 2.0 integration for enterprise single sign-on

### P2: Auth Error Status Codes Fix
- Refactor `get_current_user` to raise HTTPException (401/403) instead of returning None
- Fix all protected routes returning 500 on auth failure

### P2: iOS App Build
- Complete mobile app build for iOS

### P3: MeetingHeader Component Refactoring
- Remove code duplication in MeetingHeader

## Key Info
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test User: test@medmatch.io / TestPassword123!
- Org: org_5a18c854f810 (MedMatch Inc, Grande, 17 employees)
- Mocked: Google/Apple social sign-in, LDAP sync (no real AD server), Email OTP (returned in _dev_otp)

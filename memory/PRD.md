# MedMatch-AI KARAU - Product Requirements Document

## Original Problem Statement
MedMatch-AI KARAU: AI-powered Life Sciences & Engineering Talent Ecosystem with secure video conferencing.

---

## System Status (February 26, 2026)

| Component | Status |
|-----------|--------|
| Backend | Healthy |
| Frontend | Running |
| AI KARAU Meeting | Lobby, Skin Tone, Mute, Active Speaker, Breakout Rooms, Enterprise Tiers, Employee Directory |
| Translations | 99%+ (50 languages) |

---

## Completed This Session

### Phase 1: Enterprise Tier System
- 5 tiers (Basic/Professional/Grande/Recruiter/Personal)
- Domain verification, conference rooms (physical/virtual/hybrid), company branding
- IT Admin panel at /karau-meet/enterprise

### Phase 2: Employee Directory + LDAP
- **CSV Import**: Upload CSV with auto-column detection, duplicate handling, tier limit enforcement
- **LDAP/AD Integration**: Server configuration, test connection, sync employees
- **Employee Management**: Add/delete/update, status toggle (active/inactive), source tracking
- **Stats Dashboard**: Active/inactive counts, department breakdown, source breakdown
- **Last Name Search**: Find employees by typing last name

### Video Features (also this session)
- Pre-Meeting Lobby, Skin Tone Protection, Host Mute Controls, Active Speaker, Breakout Rooms

---

## Next: Phase 3 — Guest 2FA + Age Verification
- Guest registration with email verification
- Two-step verification (email OTP or authenticator)
- Age self-declaration (16+, per Zoom/Teams standard)

## Phase 4 — Recruiter Tier + SSO
- Recruiter-specific features and verification
- Enterprise SSO/SAML integration

## Calendar Integration (upcoming)
- Microsoft Outlook/365, Google Calendar, iOS (.ics export)

## Backlog
- P1: Live multi-user meeting test
- P2: iOS Build, Social Media Sharing
- P3: MeetingHeader refactoring

## Key Info
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test User: test@medmatch.io / TestPassword123!
- Org: org_5a18c854f810 (MedMatch Inc, Grande, 17 employees)
- Mocked: Google/Apple social sign-in, LDAP sync (no real AD server)

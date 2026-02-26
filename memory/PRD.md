# MedMatch-AI KARAU - AI-Powered Job Search Platform

## Product Requirements Document (PRD)

### Original Problem Statement
Create a comprehensive, AI-powered application named "MedMatch-AI KARAU" to automate remote job search with tools for resume parsing, job matching, and interview preparation. Includes the AI KARAU Meeting Portal for secure video conferencing.

---

## System Status (February 26, 2026)

| Component | Status | Details |
|-----------|--------|---------|
| **Backend** | Healthy | Version 2.2.0, AI Supervisor running |
| **Frontend** | Running | Webpack compiled, no errors |
| **Database** | Optimized | 82 collections, 56K docs, 9+ indexes |
| **Scheduled Maintenance** | Active | Weekly Sundays 9:00 UTC via Dragon Scheduler |
| **AI KARAU Meeting** | Enhanced | Pre-Meeting Lobby, Skin Tone Protection, Guest Admission |
| **Translations** | **99%+** | 1,940+ keys, 50 languages, all bundled |

---

## Completed Features (February 26, 2026)

### 10. Pre-Meeting Lobby (Teams-style)
- **New route**: `/karau-meet/lobby/{meetingId}` - intercepts all meeting joins
- **Video preview**: Live camera feed with device selection (camera, mic, speaker)
- **Virtual background picker**: 7 preset backgrounds selectable before joining
- **Guest admission control**: Host can require guests to wait for admission
  - Guests see "Waiting for host" with progress indicator
  - Host receives WebSocket toast notification with "Admit" action button
  - Host can admit individual guests, admit all, or deny
- **Auto-admission**: Host always auto-admitted, guests auto-admitted when waiting room disabled
- **Navigation flow**: Dashboard → Lobby → Room (join links also route through lobby)
- **8 new backend API endpoints** for lobby management

### 11. Skin Tone Protection (Automatic AI Enhancement)
- **Integrated into**: `useVirtualBackground.js` compositeFrame pipeline
- **Algorithm**: HSL-based per-pixel skin tone detection and enhancement
  - Detects skin tone range (hue 8-50°, saturation > 0.15, lightness 0.15-0.85)
  - Darker skin tones: +8% saturation boost, +3% luminance lift
  - Medium tones: +5% saturation, +1.5% luminance
  - Light tones: +2% saturation, -1% luminance (prevents overexposure)
- **Automatic**: No user toggle needed, activates when virtual background is active
- **Inclusive**: Ensures natural rendering for all skin tones, inspired by Agora SDK

---

## Previous Completed Features

### 1-9. See CHANGELOG.md for full history
- Share Meeting, Database Standardization, Scheduled Maintenance
- ORCID OAuth, Translation Hardening, Full Translation Sweep
- Translation Health Monitor, Implementation Roadmap, P1 Integration Verification

---

## Backlog (Parked)

### P1
- Live Multi-User KARAU Meeting Test (pending - user needs to test)
- LinkedIn Profile Sync (implemented, needs user verification)
- PayPal Integration (implemented, sandbox tested)
- ORCID live user verification

### P2
- Enterprise SSO/SAML
- iOS Build
- Social Media Sharing (LinkedIn/Twitter share buttons)

### P3
- MeetingHeader component refactoring

---

## Key Technical Info
- **Admin:** admin@medmatch.com / Swampdrainer2026!
- **Test User:** test@medmatch.io / TestPassword123!
- **Scheduler:** Dragon Scheduler, 5 jobs, MongoDB-persisted
- **Mocked:** Google and Apple social sign-in
- **ORCID OAuth:** Production (orcid.org), Client ID: APP-K9HUYS6GQY2RERX6
- **i18n:** 50 languages, 1,940 keys, 0 missing keys, all pre-bundled

## New API Endpoints (February 26, 2026)
- `POST /api/karau-meet/meetings/{id}/lobby/join` - Guest joins lobby
- `POST /api/karau-meet/meetings/{id}/lobby/join-auth` - Authenticated user joins lobby
- `GET /api/karau-meet/meetings/{id}/lobby/status?user_id=` - Poll admission status
- `GET /api/karau-meet/meetings/{id}/lobby/waiting` - Host views waiting list
- `POST /api/karau-meet/meetings/{id}/lobby/admit` - Host admits guest
- `POST /api/karau-meet/meetings/{id}/lobby/admit-all` - Host admits all
- `POST /api/karau-meet/meetings/{id}/lobby/deny` - Host denies guest
- `PUT /api/karau-meet/meetings/{id}/settings/waiting-room?enabled=` - Toggle waiting room

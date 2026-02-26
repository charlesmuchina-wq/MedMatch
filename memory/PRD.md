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
| **AI KARAU Meeting** | Enhanced | Lobby, Skin Tone Protection, Mute Controls, Active Speaker |
| **Translations** | **99%+** | 1,940+ keys, 50 languages, all bundled |

---

## Recently Completed Features (February 26, 2026)

### 10. Pre-Meeting Lobby (Teams-style)
- New route: `/karau-meet/lobby/{meetingId}` - intercepts all meeting joins
- Video preview with device selection (camera, mic, speaker)
- Virtual background picker before joining
- Guest admission control: Host can require guests to wait for admission
  - Host receives WebSocket notification with "Admit" action
  - Host can admit individual, admit all, or deny guests
- 8 new backend API endpoints for lobby management

### 11. Skin Tone Protection (Automatic AI Enhancement)
- HSL-based per-pixel skin tone detection in virtual background pipeline
- Boosts darker skin tones (+8% saturation, +3% luminance)
- Prevents overexposure on lighter tones

### 12. Host Mute Controls
- **Mute Individual**: Host can force-mute any participant via dropdown menu
- **Mute All**: Host button mutes all participants except self
- **Pass Mic**: Host passes mic to a participant — auto-unmutes target, mutes others
- Force-mute and pass-mic sent via WebSocket, handled automatically on client

### 13. Active Speaker Detection & Highlighting
- AudioContext-based audio level analysis on 500ms interval
- Active speaker gets emerald ring + shadow in ParticipantGrid tile
- ParticipantsPanel shows "Speaking" label + green indicator on active participant
- Works for both local and remote participant streams

---

## Backlog

### P0 (Next Up)
- **Breakout Rooms with Auto-Assign**: Manual drag/assign + AI auto-assign, max 10/room, timer with auto-return

### P1
- Live Multi-User KARAU Meeting Test (pending user test)
- LinkedIn Profile Sync, PayPal, ORCID verification

### P2
- Enterprise SSO/SAML, iOS Build, Social Media Sharing

### P3
- MeetingHeader component refactoring

---

## Key Technical Info
- **Admin:** admin@medmatch.com / Swampdrainer2026!
- **Test User:** test@medmatch.io / TestPassword123!
- **Mocked:** Google and Apple social sign-in
- **i18n:** 50 languages, 1,940 keys, 0 missing keys

## API Endpoints Added (February 26, 2026)
- `POST /api/karau-meet/meetings/{id}/lobby/join` - Guest joins lobby
- `POST /api/karau-meet/meetings/{id}/lobby/join-auth` - Auth user joins lobby
- `GET /api/karau-meet/meetings/{id}/lobby/status?user_id=` - Poll admission
- `GET /api/karau-meet/meetings/{id}/lobby/waiting` - Host views waiting list
- `POST /api/karau-meet/meetings/{id}/lobby/admit` - Host admits guest
- `POST /api/karau-meet/meetings/{id}/lobby/admit-all` - Host admits all
- `POST /api/karau-meet/meetings/{id}/lobby/deny` - Host denies guest
- `PUT /api/karau-meet/meetings/{id}/settings/waiting-room?enabled=` - Toggle

## WebSocket Message Types Added
- `mute_participant` - Host force-mutes a specific participant
- `mute_all` - Host mutes all participants except self
- `pass_mic` - Host passes mic (auto-unmutes target, mutes others)
- `force_mute` (host_action) - Client receives and disables audio track
- `pass_mic` (host_action) - Client receives and enables audio track

# MedMatch-AI KARAU - AI-Powered Job Search Platform

## Product Requirements Document (PRD)

### Original Problem Statement
Create a comprehensive, AI-powered application named "MedMatch-AI KARAU" to automate remote job search with tools for resume parsing, job matching, and interview preparation. Includes the AI KARAU Meeting Portal for secure video conferencing.

---

## System Status (February 26, 2026)

| Component | Status | Details |
|-----------|--------|---------|
| **Backend** | Healthy | AI Supervisor running |
| **Frontend** | Running | Webpack compiled, no errors |
| **Database** | Optimized | 82 collections, 56K docs, 9+ indexes |
| **AI KARAU Meeting** | Enhanced | Lobby, Skin Tone, Mute Controls, Active Speaker, Breakout Rooms |
| **Translations** | **99%+** | 1,940+ keys, 50 languages |

---

## Features Completed This Session (February 26, 2026)

### 10. Pre-Meeting Lobby (Teams-style)
- New route `/karau-meet/lobby/{meetingId}`, camera/mic preview, device selection
- Guest admission control with host notification + admit/deny/admit-all
- 8 lobby API endpoints

### 11. Skin Tone Protection (Automatic AI)
- HSL-based per-pixel enhancement in virtual background pipeline
- Darker skin: +8% saturation/+3% luminance. Light skin: prevents overexposure

### 12. Host Mute Controls
- Mute Individual, Mute All, Pass Mic (auto-unmutes target, mutes others)
- Force-mute/pass-mic via WebSocket

### 13. Active Speaker Detection & Highlighting
- AudioContext-based 500ms audio level analysis
- Emerald ring + shadow on active speaker in video grid and participants panel

### 14. Breakout Rooms with Auto-Assign
- **Manual assignment**: Host creates rooms, drags/assigns participants
- **AI auto-assign**: Round-robin distribution, excludes host, respects room count
- **Max 10 per room** enforced
- **Timer with auto-return**: Presets (3/5/10/15/20 min), countdown display, expires notification
- **Full session lifecycle**: Start → Active → Close (returns everyone to main room)
- **Move participant**: Host can move participants between rooms during active session
- **BreakoutRoomManager UI**: Setup mode (room cards, unassigned pool, timer toggle), Active mode (countdown, room list), Closed mode
- **WebSocket broadcasts**: session_started, session_closed, room_assigned, room_moved

---

## Backlog

### P1
- Live Multi-User KARAU Meeting Test (pending user test)
- LinkedIn Profile Sync, PayPal, ORCID verification

### P2
- Enterprise SSO/SAML, iOS Build, Social Media Sharing

### P3
- MeetingHeader component refactoring
- Auth dependency improvement (return 401 instead of 500 for missing tokens)

---

## Key Technical Info
- **Admin:** admin@medmatch.com / Swampdrainer2026!
- **Test User:** test@medmatch.io / TestPassword123!
- **Mocked:** Google and Apple social sign-in
- **i18n:** 50 languages, 1,940 keys, 0 missing keys

## Breakout Room API Endpoints
- `POST /api/karau-meet/meetings/{id}/breakout-session/start` - Start session
- `GET /api/karau-meet/meetings/{id}/breakout-session` - Get session status
- `POST /api/karau-meet/meetings/{id}/breakout-session/close` - Close all rooms
- `POST /api/karau-meet/meetings/{id}/breakout-session/move` - Move participant
- `POST /api/karau-meet/meetings/{id}/breakout-session/auto-assign` - AI preview
- `POST /api/karau-meet/meetings/{id}/breakout-rooms` - Create single room

# AI KARAU Changelog

## Mar 2, 2026 — Distance Zero Feature Suite

### Bug Fix
- **P2 Fix**: Gamification endpoints (`/api/karau/webinar/{id}/reaction`, `/api/karau/webinar/{id}/leaderboard/track`) now return 401 for unauthenticated requests (was 500). Changed `get_current_user` to `require_auth`.

### New Features

#### Cinematic Director Mode
- AI-powered automatic camera view switching between Panoramic, Speaker Close-Up, Conversation, and Manual modes
- Backend: `karau_director.py` with 3 endpoints (set mode, get mode, analyze patterns)
- Frontend: `DirectorModePanel.jsx`, `useDirectorMode.js` hook
- Integrated into WebinarLiveRoom with control button

#### QR Code Touchless Meeting Entry
- Generate QR codes for instant meeting join
- Token-based validation with expiry and max-use tracking
- Backend: `karau_qr_entry.py` with CRUD endpoints
- Frontend: `QRCodePanel.jsx` with copy link and deactivation

#### Ghost Booking Prevention
- Activity pinging system (60s intervals)
- Idle meeting detection with configurable timeout
- Auto-release and manual keep-alive functionality
- Backend: `karau_ghost_booking.py` with 5 endpoints
- Frontend: `GhostBookingAlert.jsx`, `useGhostBooking.js` hook

#### Enhanced Real-Time Sentiment Dashboard
- Per-participant heatmap with attention/confusion/engagement/energy metrics
- AI recommendations: clarify, engage, break, energize based on aggregate scores
- History tracking with sliding window (last 30 data points per participant)
- Backend: `karau_enhanced_sentiment.py`
- Frontend: `SentimentDashboard.jsx` with real-time polling

#### Multiplayer AI Copilots
- Cross-meeting intelligence using Emergent LLM
- Context from current meeting, past meeting summaries, shared documents
- Query history tracking per meeting
- Frontend: `CopilotPanel.jsx` with suggestion prompts and chat interface

### Files Created
- `backend/routes/karau_director.py`
- `backend/routes/karau_qr_entry.py`
- `backend/routes/karau_ghost_booking.py`
- `backend/routes/karau_enhanced_sentiment.py`
- `frontend/src/hooks/useDirectorMode.js`
- `frontend/src/hooks/useGhostBooking.js`
- `frontend/src/components/KarauMeet/DirectorModePanel.jsx`
- `frontend/src/components/KarauMeet/QRCodePanel.jsx`
- `frontend/src/components/KarauMeet/GhostBookingAlert.jsx`
- `frontend/src/components/KarauMeet/SentimentDashboard.jsx`
- `frontend/src/components/KarauMeet/CopilotPanel.jsx`

### Files Modified
- `backend/routes/karau_gamification.py` — require_auth fix
- `backend/server.py` — 4 new routers registered
- `frontend/src/pages/KarauMeet/WebinarLiveRoom.jsx` — new imports, hooks, controls, panels

### Testing
- 36/36 backend tests passed (100%)
- Frontend components verified clean
- Test report: `/app/test_reports/iteration_152.json`

---

## Mar 1, 2026 — Gamification, Video Framing, Spatial Audio

### New Features
- AI-Powered Video Framing (active speaker main stage)
- Gamification Suite (emoji reactions, participation leaderboard)
- Spatial Audio Integration (Web Audio API with HRTF PannerNode)

---

## Prior History
See `/app/docs/GAP_ASSESSMENT.md` for full competitive benchmarking.

# MedMatch-AI KARAU Platform - Product Requirements Document

## Original Problem Statement
Build "MedMatch-AI KARAU" - a dual-purpose platform featuring:
1. **AI KARAU** - Premium video meeting portal with AI-powered features
2. **MedMatch Job Toolkit** - AI-powered life sciences talent ecosystem

## Core Architecture
- **Frontend**: React + Tailwind CSS + Shadcn UI + react-i18next (52 locales)
- **Backend**: FastAPI + MongoDB + Motor (async)
- **AI**: Emergent LLM Key for assistant, summaries, translation
- **Theme**: Purple/violet/emerald karau palette
- **WebRTC**: Full signaling server + peer connection management
- **Object Storage**: Emergent Object Storage for cloud recordings

## What's Implemented

### AI KARAU Portal
- **Dashboard**: Single-page horizontal layout with real-time stats, activity feed, upcoming meetings, trending topics, Meeting Effectiveness Score, Gamification (XP, levels, badges, streaks), collapsible Team Leaderboard (top 50), Quick Analytics, auto-refresh every 30s

- **Meeting Room**: Full-featured video conferencing with WebRTC, dual-engine noise cancellation (RNNoise WASM + Web Audio API), screen share, breakout rooms, polls, whiteboard, live captions, virtual backgrounds, recording with cloud auto-upload, AI assistant, **In-Meeting File Sharing** (P2P via WebSocket, 10MB limit)

- **Cloud Recording Storage**: Auto-upload recordings to Emergent Object Storage after meeting ends. Download from cloud. Stats showing cloud vs local counts, total duration, storage used. Graceful fallback to local if cloud fails.

- **Webinar Mode** (WebEx-style, 1000+ attendees): Management page with create/list/start/end. Public registration (no login). Host controls. Q&A system. **Enhanced Analytics Dashboard** with: Engagement score (0-100), Registration-to-Attendance funnel (registered/attended/missed with drop-off rate), Q&A stats (total/pending/answered/dismissed/anonymous/top questions by upvotes), Organization breakdown (top 10), Registration timeline bar chart.

- **Settings**: 6 tabs (Accessibility, Calendar, Security, SSO/SAML, Compliance, Webhooks)
- **Recordings**: Cloud/Local distinction, stat cards, download cloud recordings
- **Guest Join**: 3-step OTP verification

### MedMatch Job Toolkit
- Semantic search, resume parser/builder, AI job matching, recruiter network, admin panel, analytics, trust score

### Internationalization (52 Languages)
- 384+ karauMeet i18n keys, all propagated to 51 locales via AI translation
- Cloud recording & webinar analytics keys translated (1443 translations in latest batch)

## Key API Endpoints
- `GET /api/karau-meet/recordings/` - List recordings (cloud + local)
- `GET /api/karau-meet/recordings/stats` - Recording statistics
- `POST /api/karau-meet/recordings/upload` - Upload recording to cloud (multipart)
- `GET /api/karau-meet/recordings/download/{id}` - Download cloud recording
- `DELETE /api/karau-meet/recordings/{id}` - Soft-delete recording
- `GET /api/karau/webinar/{id}/analytics` - Enhanced webinar analytics (funnel, Q&A, engagement, org breakdown, timeline)
- `GET /api/karau/webinar/list` - List webinars
- `POST /api/karau/webinar/create` - Create webinar
- `POST /api/karau/webinar/{id}/start` - Start webinar
- `POST /api/karau/webinar/{id}/end` - End webinar
- `GET /api/karau/analytics/leaderboard` - Team leaderboard
- `GET /api/karau/analytics/gamification` - XP, levels, badges

## Backlog

### P1 - Upcoming
- Refinement of rnnoise-wasm noise cancellation
- UI polish & UX refinements

### P2 - Future
- Payment gateway live keys (Stripe/PayPal)
- Additional AI analytics enhancements
- Meeting recording transcription

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test User: test@medmatch.io / TestPassword123!

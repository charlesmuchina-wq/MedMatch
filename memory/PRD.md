# MedMatch-AI KARAU Platform - Product Requirements Document

## Original Problem Statement
Build "MedMatch-AI KARAU" - a dual-purpose platform:
1. **AI KARAU** - Premium video meeting portal with AI-powered features
2. **MedMatch Job Toolkit** - AI-powered life sciences talent ecosystem

## Core Architecture
- **Frontend**: React + Tailwind CSS + Shadcn UI + react-i18next (52 locales)
- **Backend**: FastAPI + MongoDB + Motor (async)
- **AI**: Emergent LLM Key for assistant, summaries, translation
- **Theme**: Purple/violet/emerald karau dark palette
- **WebRTC**: Full signaling server + peer connection management
- **Object Storage**: Emergent Object Storage for cloud recordings

## What's Implemented

### AI KARAU Portal
- **Dashboard**: Data-driven with real-time stats, gamification (XP/levels/badges/streaks), collapsible Team Leaderboard (top 50), Meeting Effectiveness Score, Quick Analytics, auto-refresh

- **Meeting Room**: WebRTC video conferencing, dual noise cancellation (RNNoise WASM), screen share, breakout rooms, polls, whiteboard, live captions, virtual backgrounds, AI assistant, In-Meeting File Sharing (P2P, 10MB), cloud recording auto-upload

- **Cloud Recording Storage**: Auto-upload to Emergent Object Storage. Download from cloud. Stats (cloud vs local, duration, storage). Local fallback.

- **Webinar Mode (WebEx-style, 1000+ attendees)**:
  - **Multi-Role System**: Host (full control) > Presenter (video/audio/screen share) > Panelist (video/audio) > Attendee (view-only with hand raise)
  - **Live Webinar Room**: Full-screen layout, video stage, bottom controls, side panels (Q&A, Participants, Settings)
  - **Host Controls**: Start/End webinar, Practice session (blocks attendees), Mute all, Selective unmute, Enable/disable chat, Promote/Demote participants
  - **Hand Raise**: Attendees request to speak, host sees raised hands and can promote
  - **Q&A System**: Submit, answer, upvote, dismiss, anonymous questions
  - **Enhanced Analytics**: Engagement score (0-100), Registration-Attendance funnel (registered/attended/missed/drop-off), Q&A stats (total/pending/answered/dismissed/anonymous/top questions), Organization breakdown (top 10), Registration timeline
  - **Management Page**: Create/list/start/end webinars, copy registration links, analytics dialog per webinar
  - **Public Registration**: No login required for registration page

- **Settings**: 6 tabs, **Recordings**: Cloud/Local with stats, **Guest Join**: 3-step OTP

### Internationalization: 384+ keys across 52 locales (AI-translated)

## Key API Endpoints
### Webinar Role Management
- `GET /api/karau/webinar/{id}/room-info` - User role & permissions for live room
- `POST /api/karau/webinar/{id}/roles/promote` - Promote to presenter/panelist
- `POST /api/karau/webinar/{id}/roles/demote` - Demote to attendee
- `GET /api/karau/webinar/{id}/roles` - All active roles
- `POST /api/karau/webinar/{id}/hand-raise` / `hand-lower` - Hand raise toggle
- `GET /api/karau/webinar/{id}/hand-raises` - List raised hands
- `POST /api/karau/webinar/{id}/practice/start` / `end` - Practice session
- `POST /api/karau/webinar/{id}/controls/unmute-user` - Selective unmute
- `POST /api/karau/webinar/{id}/controls/mute-all` - Mute all
### Cloud Recordings
- `POST /api/karau-meet/recordings/upload` - Upload to cloud (multipart)
- `GET /api/karau-meet/recordings/download/{id}` - Download cloud recording
- `GET /api/karau-meet/recordings/stats` - Recording statistics

## Backlog
### P1 - Upcoming
- rnnoise-wasm noise cancellation refinement
- UI polish & UX refinements

### P2 - Future
- Payment gateway live keys (Stripe/PayPal)
- Meeting recording transcription
- Real-time WebSocket signaling for webinar role changes

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test User: test@medmatch.io / TestPassword123!

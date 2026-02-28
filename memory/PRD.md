# MedMatch-AI KARAU Platform - Product Requirements Document

## Original Problem Statement
Build "MedMatch-AI KARAU" - a dual-purpose platform:
1. **AI KARAU** - Premium video meeting portal with AI-powered features
2. **MedMatch Job Toolkit** - AI-powered life sciences talent ecosystem

## Core Architecture
- **Frontend**: React + Tailwind CSS + Shadcn UI + react-i18next (52 locales)
- **Backend**: FastAPI + MongoDB + Motor (async)
- **AI**: Emergent LLM Key for assistant, summaries, translation, transcription
- **Theme**: Purple/violet/emerald karau dark palette
- **WebRTC**: Full signaling server + peer connections for webinars/meetings
- **Object Storage**: Emergent Object Storage for cloud recordings
- **Speech-to-Text**: OpenAI Whisper via emergentintegrations for auto-transcription

## What's Implemented

### AI KARAU Portal
- **Dashboard**: Data-driven with real-time stats, gamification (XP/levels/badges/streaks), collapsible Team Leaderboard (top 50), Meeting Effectiveness Score, Quick Analytics, auto-refresh

- **Meeting Room**: WebRTC video conferencing, dual noise cancellation (RNNoise WASM), screen share, breakout rooms, polls, whiteboard, live captions, virtual backgrounds, AI assistant, In-Meeting File Sharing (P2P, 10MB), cloud recording auto-upload

- **Cloud Recording Storage**: Auto-upload to Emergent Object Storage. Auto-transcription via Whisper on upload. Recordings page with Cloud/Local badges, transcription status (Queued/Transcribing/Completed), expandable timestamped transcript. Download from cloud.

- **Webinar Mode (WebEx-style, 1000+ attendees)**:
  - **Multi-Role Hierarchy**: Host > **Coordinator** > Presenter > Panelist > Attendee
  - **Coordinator Role (Proxy Host)**: Can monitor webinar, drive presentation slides, manage Q&A, promote/demote (except other coordinators), mute all. NO video capability. Cannot start/end webinar. Assignable at webinar creation.
  - **Live Webinar Room**: Full-screen layout with WebRTC peer-to-peer video, slide drive bar, Q&A panel, Participants panel, Controls panel
  - **Host Controls**: Start/End, Practice session, Mute all, Selective unmute, Promote/Demote, Enable/disable chat
  - **WebRTC P2P Video**: Host/Presenter/Panelist stream video. Attendees view-only. WebSocket signaling at /api/karau-meet/ws/webinar-{id}
  - **Slide Drive**: Host/Coordinator/Presenter can navigate slides with prev/next, synced via WebSocket
  - **Hand Raise**: Attendees request to speak
  - **Q&A System**: Submit, answer, upvote, dismiss, anonymous
  - **Enhanced Analytics**: Engagement score, Registration-Attendance funnel, Q&A stats, Org breakdown, Timeline

### MedMatch Job Toolkit
- Semantic search, resume parser/builder, AI job matching, recruiter network, admin panel

### Internationalization: 384+ keys across 52 locales

## Key API Endpoints
### Webinar Role Management
- `POST /api/karau/webinar/create` - Now accepts coordinator_emails
- `GET /api/karau/webinar/{id}/room-info` - Returns my_role, can_stream_video, can_control, can_drive_slides
- `POST /api/karau/webinar/{id}/roles/promote` - Promote to coordinator/presenter/panelist
- `POST /api/karau/webinar/{id}/roles/demote` - Demote to attendee
- `GET /api/karau/webinar/{id}/roles` - Returns roles + coordinator_emails + panelist_emails
### Recording Transcription
- `POST /api/karau-meet/recordings/upload` - Auto-triggers Whisper transcription
- `GET /api/karau-meet/recordings/transcript/{id}` - Get transcript (status/text/segments)

## Backlog
### P1
- rnnoise-wasm refinement, UI polish

### P2
- Payment gateway live keys (Stripe/PayPal)
- Additional AI analytics

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test User: test@medmatch.io / TestPassword123!

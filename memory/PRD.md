# MedMatch-AI KARAU Platform - Product Requirements Document

## Original Problem Statement
Build "MedMatch-AI KARAU" - a dual-purpose platform:
1. **AI KARAU** - Premium video meeting portal with AI-powered features
2. **MedMatch Job Toolkit** - AI-powered life sciences talent ecosystem

## Core Architecture
- **Frontend**: React + Tailwind CSS + Shadcn UI + react-i18next (52 locales)
- **Backend**: FastAPI + MongoDB + Motor (async)
- **AI**: Emergent LLM Key (GPT-4o-mini for translation, Whisper for STT)
- **WebRTC**: Full signaling server + peer connections for webinars/meetings
- **Object Storage**: Emergent Object Storage for cloud recordings

## What's Implemented

### AI KARAU Portal
- **Dashboard**: Real-time stats, gamification, Team Leaderboard, auto-refresh
- **Meeting Room**: WebRTC conferencing, noise cancellation, screen share, breakout rooms, polls, whiteboard, virtual backgrounds, AI assistant, P2P file sharing, cloud recording auto-upload
- **Cloud Recordings**: Auto-upload, auto-transcription via Whisper
- **AI Meeting Notes**: Generate/view/copy/send notes from recording transcripts
- **Real-time Live Transcription**: CC toggle, audio chunk capture, caption overlay
- **Multi-language Captions**: 16 languages, GPT-4o-mini translation, language picker
- **Speaker Identification**: Audio level monitoring, speaker labels with colors, active speaker indicator
- **Organization-based Access Control** (Mar 1, 2026):
  - Admin defines company email domains at webinar creation (e.g., acme.com, acme.org)
  - Internal attendees: Full name + job title + department displayed
  - External attendees: Shown as "External Guest" with limited info visibility
  - Document sharing restricted to internal members by default
  - External download blocked by default
  - Host can grant upload/download permission to specific external guests
  - All guest permissions auto-expire when meeting ends (cleared on POST /end)
  - Privacy status panel in Participants view with ShieldCheck/ShieldOff indicators
  - Internal/External badge on top bar of webinar room
- **Webinar Mode (WebEx-style, 1000+ attendees)**:
  - Multi-Role: Host > Coordinator > Presenter > Panelist > Attendee
  - Live Room with WebRTC P2P video, slide driving, Q&A, controls
  - Presentation Slide Driving (PDF/PPTX, canvas, annotations)
  - Noise Cancellation toggle (RNNoise WASM + Web Audio fallback)
  - Enhanced Analytics

### MedMatch Job Toolkit
- Semantic search, resume parser/builder, AI job matching, recruiter network, admin panel

## Key API Endpoints
### Organization Access Control
- `POST /api/karau/webinar/create` - Now accepts org_domains, internal_only_docs, external_download_blocked
- `GET /api/karau/webinar/{id}/room-info` - Returns is_internal, attendee_type, can_download, can_upload_docs, org_privacy, employee_info, guest_permissions
- `POST /api/karau/webinar/{id}/guest-permission/grant` - Host grants upload/download to guest
- `POST /api/karau/webinar/{id}/guest-permission/revoke` - Host revokes permission
- `GET /api/karau/webinar/{id}/attendees-classified` - Internal/external classification with counts
- `POST /api/karau/webinar/{id}/end` - Auto-clears all guest permissions

### Caption Translation
- `POST /api/karau/webinar/translate-caption` - GPT-4o-mini translation
- `GET /api/karau/webinar/caption-languages` - 16 supported languages

### Live Transcription & Notes
- `POST /api/realtime-stt/transcribe-base64` - Whisper STT
- `POST /api/karau/webinar/{id}/live-transcript/save` - Save transcript
- `POST /api/karau-meet/recordings/{id}/notes/generate` - AI notes

## Backlog
### P1
- Subscription UI polish (backend Stripe exists)
### P2
- Live Stripe API keys for production
- Speaker analytics dashboard

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test User: test@medmatch.io / TestPassword123!

# MedMatch-AI KARAU Platform - Product Requirements Document

## Original Problem Statement
Build "MedMatch-AI KARAU" - a dual-purpose platform:
1. **AI KARAU** - Premium video meeting portal with AI-powered features
2. **MedMatch Job Toolkit** - AI-powered life sciences talent ecosystem

## Core Architecture
- **Frontend**: React + Tailwind CSS + Shadcn UI + react-i18next (52 locales)
- **Backend**: FastAPI + MongoDB + Motor (async)
- **AI**: Emergent LLM Key (GPT-4o-mini for translation, Whisper for STT)
- **Theme**: Purple/violet/emerald karau dark palette
- **WebRTC**: Full signaling server + peer connections for webinars/meetings
- **Object Storage**: Emergent Object Storage for cloud recordings

## What's Implemented

### AI KARAU Portal
- **Dashboard**: Data-driven with real-time stats, gamification, Team Leaderboard, auto-refresh
- **Meeting Room**: WebRTC video conferencing, dual noise cancellation, screen share, breakout rooms, polls, whiteboard, virtual backgrounds, AI assistant, P2P file sharing, cloud recording auto-upload
- **Cloud Recording Storage**: Auto-upload to Object Storage, auto-transcription via Whisper
- **AI Meeting Notes**: Generate/view/copy/send notes from recording transcripts
- **Real-time Live Transcription**: CC toggle, useLiveTranscription hook, caption overlay
- **Multi-language Live Captions** (Mar 1, 2026):
  - 16 supported languages: EN, ES, FR, DE, IT, PT, JA, KO, ZH, NL, AR, HI, RU, TR, PL, SV
  - Language picker panel (Globe button) with Speaker Language + Display Language selectors
  - Real-time translation via GPT-4o-mini when source != display language
  - Translation badge on captions when translating
  - Backend: POST /api/karau/webinar/translate-caption
  - Backend: GET /api/karau/webinar/caption-languages
- **Webinar Mode (WebEx-style, 1000+ attendees)**:
  - Multi-Role: Host > Coordinator > Presenter > Panelist > Attendee
  - Live Webinar Room with WebRTC P2P video, slide driving, Q&A, controls
  - Presentation Slide Driving (PDF/PPTX, canvas rendering, annotations)
  - Noise Cancellation toggle (RNNoise WASM + Web Audio fallback)
  - Enhanced Analytics

### MedMatch Job Toolkit
- Semantic search, resume parser/builder, AI job matching, recruiter network, admin panel

### Internationalization: 384+ keys across 52 locales

## Key API Endpoints
### Caption Translation
- `POST /api/karau/webinar/translate-caption` - Translate text between 16 languages via GPT-4o-mini
- `GET /api/karau/webinar/caption-languages` - Get supported languages list
### Live Transcription
- `POST /api/realtime-stt/transcribe-base64` - Transcribe audio chunk via Whisper
- `POST /api/karau/webinar/{id}/live-transcript/save` - Save live transcript
- `GET /api/karau/webinar/{id}/live-transcript` - Get saved transcript
### Recording Notes
- `POST /api/karau-meet/recordings/{id}/notes/generate` - Generate AI notes
- `POST /api/karau-meet/recordings/{id}/notes/send` - Send notes to participants

## Backlog
### P1
- Subscription UI polish (backend Stripe integration exists)
### P2
- Live Stripe API keys for production payments
- Additional AI analytics

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test User: test@medmatch.io / TestPassword123!

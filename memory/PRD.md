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
- **Meeting Room**: WebRTC conferencing, dual noise cancellation, screen share, breakout rooms, polls, whiteboard, virtual backgrounds, AI assistant, P2P file sharing, cloud recording auto-upload
- **Cloud Recordings**: Auto-upload to Object Storage, auto-transcription via Whisper
- **AI Meeting Notes**: Generate/view/copy/send notes from recording transcripts
- **Real-time Live Transcription**: CC toggle, useLiveTranscription hook, caption overlay
- **Multi-language Live Captions** (Mar 1, 2026):
  - 16 languages (EN, ES, FR, DE, IT, PT, JA, KO, ZH, NL, AR, HI, RU, TR, PL, SV)
  - Language picker panel (Globe button) with Speaker + Display language selectors
  - Real-time translation via GPT-4o-mini
- **Speaker Identification** (Mar 1, 2026):
  - useSpeakerDetection hook monitors audio levels via Web Audio API AnalyserNode
  - Maps each WebRTC stream to participant name with distinct color (10 colors)
  - Captions labeled with speaker name + color (e.g., "John: Welcome...")
  - Active speaker indicator badge in top-left of video stage
  - Dynamic speaking border on local and remote video tiles
  - Audio level polling at 200ms, threshold avg > 15 for speaking state
- **Webinar Mode (WebEx-style, 1000+ attendees)**:
  - Multi-Role: Host > Coordinator > Presenter > Panelist > Attendee
  - Live Room with WebRTC P2P video, slide driving, Q&A, controls
  - Presentation Slide Driving (PDF/PPTX, canvas, annotations)
  - Noise Cancellation toggle (RNNoise WASM + Web Audio fallback)
  - Enhanced Analytics

### MedMatch Job Toolkit
- Semantic search, resume parser/builder, AI job matching, recruiter network, admin panel

### Internationalization: 384+ keys across 52 locales

## Key API Endpoints
- `POST /api/karau/webinar/translate-caption` - Translate captions (GPT-4o-mini)
- `GET /api/karau/webinar/caption-languages` - 16 supported languages
- `POST /api/realtime-stt/transcribe-base64` - Whisper STT
- `POST /api/karau/webinar/{id}/live-transcript/save` - Save transcript
- `POST /api/karau-meet/recordings/{id}/notes/generate` - AI notes
- `POST /api/karau-meet/recordings/{id}/notes/send` - Send notes

## Backlog
### P1
- Subscription UI polish (backend Stripe exists)
### P2
- Live Stripe API keys for production
- Additional AI analytics

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test User: test@medmatch.io / TestPassword123!

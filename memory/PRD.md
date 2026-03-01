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

- **AI Meeting Notes** (Mar 1, 2026):
  - Generate AI-powered meeting notes from recording transcripts
  - Backend: POST /api/karau-meet/recordings/{id}/notes/generate
  - View existing notes: GET /api/karau-meet/recordings/{id}/notes
  - Send notes to participants: POST /api/karau-meet/recordings/{id}/notes/send
  - Frontend: Notes buttons in Recordings page, copy to clipboard, send via email input

- **Real-time Live Transcription** (Mar 1, 2026):
  - CC (Closed Captions) toggle button in webinar control bar
  - useLiveTranscription hook captures audio via MediaRecorder, sends 8-second chunks to Whisper
  - Live caption overlay bar at bottom of video stage
  - Host can save accumulated transcript: POST /api/karau/webinar/{id}/live-transcript/save
  - Saved transcript enables immediate AI notes generation post-meeting

- **Webinar Mode (WebEx-style, 1000+ attendees)**:
  - **Multi-Role Hierarchy**: Host > Coordinator > Presenter > Panelist > Attendee
  - **Coordinator Role (Proxy Host)**: Can monitor webinar, drive presentation slides, manage Q&A, promote/demote (except other coordinators), mute all. NO video capability.
  - **Live Webinar Room**: Full-screen layout with WebRTC peer-to-peer video, slide drive bar, Q&A panel, Participants panel, Controls panel
  - **Presentation Slide Driving** (Mar 1, 2026):
    - Upload PDF/PPTX presentations via SlideRenderer component
    - Backend converts to slide images using pdf2image/python-pptx
    - Canvas-based rendering with laser pointer, pen, highlighter, eraser annotations
    - Slide navigation synced via WebSocket to all participants
  - **Noise Cancellation in Live Room** (Mar 1, 2026):
    - AudioLines toggle button in webinar control bar
    - Dual-engine: RNNoise WASM (preferred) + Web Audio API fallback
    - Green indicator dot when active
  - **Host Controls**: Start/End, Practice session, Mute all, Selective unmute, Promote/Demote
  - **WebRTC P2P Video**: Host/Presenter/Panelist stream video
  - **Hand Raise, Q&A System, Enhanced Analytics**

### MedMatch Job Toolkit
- Semantic search, resume parser/builder, AI job matching, recruiter network, admin panel

### Internationalization: 384+ keys across 52 locales

## Key API Endpoints
### Live Transcription
- `POST /api/realtime-stt/transcribe-base64` - Transcribe audio chunk
- `GET /api/realtime-stt/status` - STT service status
- `POST /api/karau/webinar/{id}/live-transcript/save` - Save live transcript
- `GET /api/karau/webinar/{id}/live-transcript` - Get saved transcript
### Presentation Slides
- `POST /api/karau/webinar/{id}/presentation/upload` - Upload PDF/PPTX
- `GET /api/karau/webinar/{id}/presentation/slides` - Get slide info
- `GET /api/karau/webinar/{id}/presentation/slide/{idx}` - Get slide image
### Recording Notes
- `POST /api/karau-meet/recordings/{id}/notes/generate` - Generate AI notes
- `GET /api/karau-meet/recordings/{id}/notes` - Get notes
- `POST /api/karau-meet/recordings/{id}/notes/send` - Send notes

## Backlog
### P1
- Subscription UI polish (backend Stripe integration exists)

### P2
- Payment gateway live keys (Stripe/PayPal)
- Additional AI analytics

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test User: test@medmatch.io / TestPassword123!

# MedMatch-AI KARAU Platform - Product Requirements Document

## Original Problem Statement
Build "MedMatch-AI KARAU" - a dual-purpose platform:
1. **AI KARAU** - Premium video meeting portal with AI-powered features rivaling Zoom/WebEx
2. **MedMatch Job Toolkit** - AI-powered life sciences talent ecosystem

The user's vision is "Distance Zero" — making every participant feel physically present, regardless of location.

## Core Architecture
- **Frontend**: React + Tailwind CSS + Shadcn UI + react-i18next (52 locales)
- **Backend**: FastAPI + MongoDB + Motor (async)
- **AI**: Emergent LLM Key (GPT-4o-mini for translation/commands/sentiment/research/coaching, Whisper for STT)
- **WebRTC**: Full signaling server + peer connections
- **Object Storage**: Emergent Object Storage for cloud recordings

## Implemented Features

### AI Intelligence Suite
- **Agentic AI Participant**: Real-time topic research, auto action items, follow-up suggestions
- **Voice-First Interface**: Natural language voice commands (mute/record/summarize/schedule/search/assign)
- **Sentiment & Engagement Analytics**: Real-time engagement scoring (1-10), energy detection, auto-alerts, Meeting Pulse dashboard
- **Predictive Scheduling**: AI suggests optimal meeting times based on patterns/timezone
- **AI Meeting Coach** (Mar 1, 2026): Real-time private coaching tips for presenters
- **Multiplayer AI Copilots** (Mar 2, 2026): Cross-meeting intelligence with context from past meetings, shared documents, and previous decisions

### Immersive Meeting Features
- **Eye-Contact Correction**: CSS perspective transform on local video feed
- **Enhanced Digital Whiteboard**: Infinite canvas with tools, zoom/pan, export
- **Speaker Identification**: Audio level monitoring per stream, speaker labels with colors
- **Multi-language Live Captions**: 16 languages, GPT-4o-mini translation
- **AI-Powered Video Framing** (Mar 1, 2026): Active speaker auto-promoted to main stage
- **Spatial Audio** (Mar 1, 2026): Web Audio API with HRTF PannerNode for directional audio
- **Cinematic Director Mode** (Mar 2, 2026): AI auto-switches between Panoramic/Speaker Close-Up/Conversation/Manual views

### Distance Zero Features (Mar 2, 2026)
- **QR Code Touchless Entry**: Generate QR codes for instant meeting join, token-based validation with expiry
- **Ghost Booking Prevention**: Activity pinging, idle meeting detection, auto-release, configurable timeouts
- **Enhanced Sentiment Dashboard**: Real-time per-participant heatmap with attention/confusion/engagement/energy metrics, AI recommendations (clarify/engage/break/energize)

### Gamification (Mar 1, 2026)
- **Emoji Reactions**: 8 types with floating animated bubbles, real-time polling, 800ms cooldown
- **Participation Leaderboard**: Real-time ranking by score (questions=5pts, reactions=2pts, speaking=1pt/s, chat=1pt)

### Organization & Privacy
- Internal/External attendee classification by email domain
- Document sharing restrictions, guest permissions with auto-expiry

### Webinar Mode (1000+ attendees)
- Multi-Role: Host > Coordinator > Presenter > Panelist > Attendee
- Presentation slide driving, Q&A, hand raises, noise cancellation

### Core Meeting Features
- WebRTC video conferencing, screen share, cloud recording, auto-transcription
- AI meeting notes from recordings, virtual backgrounds, P2P file sharing

## Key API Endpoints

### Cinematic Director Mode
- `POST /api/karau/director/{meeting_id}/mode` - Set director mode (auto/panoramic/speaker_closeup/conversation/manual)
- `GET /api/karau/director/{meeting_id}/mode` - Get current director mode
- `POST /api/karau/director/{meeting_id}/analyze` - AI analyze speaking patterns, recommend view

### QR Code Touchless Entry
- `POST /api/karau-meet/qr/generate` - Generate QR code for meeting
- `GET /api/karau-meet/qr/validate/{qr_token}` - Validate QR code
- `GET /api/karau-meet/qr/meeting/{meeting_id}` - List QR codes
- `DELETE /api/karau-meet/qr/{qr_token}` - Deactivate QR code

### Ghost Booking Prevention
- `POST /api/karau-meet/ghost/ping` - Activity ping
- `GET /api/karau-meet/ghost/check/{meeting_id}` - Check idle status
- `POST /api/karau-meet/ghost/release/{meeting_id}` - Release idle meeting
- `POST /api/karau-meet/ghost/keep/{meeting_id}` - Keep alive
- `POST /api/karau-meet/ghost/settings/{meeting_id}` - Update settings

### Enhanced Sentiment Dashboard & AI Copilot
- `POST /api/karau/sentiment-dash/update` - Batch update participant sentiment
- `GET /api/karau/sentiment-dash/heatmap/{meeting_id}` - Get heatmap with AI recommendations
- `POST /api/karau/sentiment-dash/copilot/query` - AI copilot cross-meeting query
- `GET /api/karau/sentiment-dash/copilot/history/{meeting_id}` - Copilot query history

### Gamification
- `POST /api/karau/webinar/{id}/reaction` - Send emoji reaction
- `GET /api/karau/webinar/{id}/reactions/recent` - Get recent reactions
- `GET /api/karau/webinar/{id}/reactions/summary` - Aggregated reaction counts
- `GET /api/karau/webinar/{id}/leaderboard` - Participation leaderboard
- `POST /api/karau/webinar/{id}/leaderboard/track` - Track participation action

### AI Coach
- `POST /api/karau-features/ai-coach/tip` - Real-time coaching tip
- `GET /api/karau-features/ai-coach/report/{id}` - Post-meeting report

### AI Intelligence  
- `POST /api/karau-features/ai-agent/research` - Topic research
- `POST /api/karau-features/voice-command/execute` - Voice commands
- `POST /api/karau-features/sentiment/analyze` - Sentiment analysis
- `GET /api/karau-features/sentiment/dashboard/{id}` - Engagement dashboard
- `POST /api/karau-features/scheduling/predict` - Predictive scheduling

## Backlog
### P1
- Virtual breakout lounges with avatar movement
- Interactive challenges/polls
### P2
- Live Stripe API keys
- Dynamic meeting environments
- Biometric feed verification (anti-deepfake)
### P3
- Holographic presence, 360 room capture
- SLAM-based spatial awareness
- Apple Vision Pro spatial integration
- IoT room environmental control
- Adaptive beamforming audio (hardware-dependent)

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test User: test@medmatch.io / TestPassword123!

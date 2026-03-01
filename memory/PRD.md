# MedMatch-AI KARAU Platform - Product Requirements Document

## Original Problem Statement
Build "MedMatch-AI KARAU" - a dual-purpose platform:
1. **AI KARAU** - Premium video meeting portal with AI-powered features
2. **MedMatch Job Toolkit** - AI-powered life sciences talent ecosystem

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

### Immersive Meeting Features
- **Eye-Contact Correction**: CSS perspective transform on local video feed
- **Enhanced Digital Whiteboard**: Infinite canvas with tools, zoom/pan, export
- **Speaker Identification**: Audio level monitoring per stream, speaker labels with colors
- **Multi-language Live Captions**: 16 languages, GPT-4o-mini translation
- **AI-Powered Video Framing** (Mar 1, 2026): Active speaker auto-promoted to main stage with 1.5s debounce, PiP layout for local video, click-to-spotlight remote participants
- **Spatial Audio** (Mar 1, 2026): Web Audio API with HRTF PannerNode for directional audio based on speaker tile position, toggle on/off

### Gamification (Mar 1, 2026)
- **Emoji Reactions**: 8 types (thumbsup, clap, heart, laugh, fire, mindblown, wave, 100) with floating animated bubbles, real-time polling, 800ms cooldown
- **Participation Leaderboard**: Real-time ranking by score (questions=5pts, reactions=2pts, speaking=1pt/s, chat=1pt), reaction summary aggregation

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
- Virtual breakout lounges, interactive challenges
- Predictive scheduling enhancement
### P2
- Live Stripe API keys, dynamic meeting environments
### P3
- Holographic presence, 360 room capture

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test User: test@medmatch.io / TestPassword123!

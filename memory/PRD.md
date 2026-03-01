# MedMatch-AI KARAU Platform - Product Requirements Document

## Original Problem Statement
Build "MedMatch-AI KARAU" - a dual-purpose platform:
1. **AI KARAU** - Premium video meeting portal with AI-powered features
2. **MedMatch Job Toolkit** - AI-powered life sciences talent ecosystem

## Core Architecture
- **Frontend**: React + Tailwind CSS + Shadcn UI + react-i18next (52 locales)
- **Backend**: FastAPI + MongoDB + Motor (async)
- **AI**: Emergent LLM Key (GPT-4o-mini for translation/commands/sentiment/research, Whisper for STT)
- **WebRTC**: Full signaling server + peer connections
- **Object Storage**: Emergent Object Storage for cloud recordings

## What's Implemented

### AI KARAU Portal

#### AI Intelligence Features (Mar 1, 2026)
- **Agentic AI Participant**: Active meeting AI that researches topics in real-time, auto-assigns action items, provides instant answers with follow-up suggestions
- **Voice-First Interface**: Natural language voice commands via Web Speech API + GPT-4o-mini parsing. Commands: mute all, start/stop recording, summarize, schedule follow-up, set timer, search topics, assign actions, toggle captions, end meeting
- **Sentiment & Engagement Analytics**: Real-time engagement scoring (1-10) from transcript sentiment analysis. Dominant energy detection (high/medium/low). Auto-alerts when engagement drops or confusion detected. Meeting Pulse dashboard with sentiment breakdown
- **Predictive Scheduling**: AI suggests optimal meeting times based on meeting type, duration, team patterns, timezone

#### Organization Access Control (Mar 1, 2026)
- Internal/External attendee classification by email domain
- Document sharing restricted to internal by default
- Host grants upload/download permissions to specific guests
- Guest permissions auto-expire when meeting ends

#### Real-time Communication
- Multi-language live captions (16 languages, GPT-4o-mini translation)
- Speaker identification with colors and labels
- Live transcription with Whisper STT
- AI meeting notes from recordings

#### Webinar Mode (WebEx-style, 1000+ attendees)
- Multi-Role: Host > Coordinator > Presenter > Panelist > Attendee
- Presentation slide driving, Q&A, hand raises
- Noise cancellation (RNNoise WASM + Web Audio)
- Enhanced analytics

#### Core Meeting Features
- WebRTC conferencing, screen share, breakout rooms, polls, whiteboard
- Virtual backgrounds, P2P file sharing
- Cloud recording with auto-upload and auto-transcription

### MedMatch Job Toolkit
- Semantic search, resume parser/builder, AI job matching, admin panel

## Key API Endpoints
### AI Intelligence
- `POST /api/karau-features/ai-agent/research` - Real-time topic research
- `POST /api/karau-features/ai-agent/assign-action` - Assign action items
- `GET /api/karau-features/ai-agent/actions/{id}` - Get action items
- `POST /api/karau-features/voice-command/execute` - Parse/execute voice commands
- `POST /api/karau-features/sentiment/analyze` - Sentiment analysis
- `GET /api/karau-features/sentiment/dashboard/{id}` - Engagement dashboard
- `POST /api/karau-features/scheduling/predict` - Predictive scheduling

### Organization & Privacy
- `POST /api/karau/webinar/{id}/guest-permission/grant` - Grant guest permissions
- `POST /api/karau/webinar/{id}/guest-permission/revoke` - Revoke permissions
- `GET /api/karau/webinar/{id}/attendees-classified` - Classified attendees

### Captions & Translation
- `POST /api/karau/webinar/translate-caption` - Multi-language translation
- `GET /api/karau/webinar/caption-languages` - 16 supported languages

## Backlog
### P1
- Subscription UI polish
- Immersive features: Eye-contact correction, enhanced whiteboard
### P2
- Live Stripe API keys, Virtual breakout lounges, Interactive challenges
- Spatial audio, dynamic meeting environments

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test User: test@medmatch.io / TestPassword123!

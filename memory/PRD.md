# MedMatch-AI KARAU Platform - Product Requirements Document

## Original Problem Statement
Build "MedMatch-AI KARAU" - a futuristic meeting platform achieving "Distance Zero" — making every participant feel physically present, regardless of location. Rivals Cisco WebEx and Zoom with AI, immersive tech, and hardware readiness.

## Core Architecture
- **Frontend**: React + Tailwind CSS + Shadcn UI + react-i18next (52 locales)
- **Backend**: FastAPI + MongoDB + Motor (async)
- **AI**: Emergent LLM Key (GPT-4o-mini)
- **WebRTC**: Full signaling server + peer connections
- **Object Storage**: Emergent Object Storage for cloud recordings

## Implemented Features

### AI Intelligence Suite
- Agentic AI Participant (research, action items, follow-ups)
- Voice-First Interface (mute/record/summarize/schedule/assign)
- Sentiment & Engagement Analytics (1-10 scoring, energy detection)
- Predictive Scheduling (AI optimal meeting times)
- AI Meeting Coach (real-time presenter coaching)
- Multiplayer AI Copilots (cross-meeting context memory)

### Distance Zero - Immersive Features
- Eye-Contact Correction (CSS perspective transform)
- Enhanced Digital Whiteboard (infinite canvas)
- Speaker Identification (per-stream audio monitoring)
- Multi-language Live Captions (16 languages)
- AI-Powered Video Framing (active speaker main stage)
- Spatial Audio (Web Audio API HRTF PannerNode)
- Cinematic Director Mode (auto Panoramic/Speaker/Conversation/Manual)

### Distance Zero - Hardware Integration Layer
- **SLAM Spatial Tracking**: 3D room mapping, user positions, face confidence, auto-frame adjustments
- **360 Multi-Focus Framing**: Panoramic headshot extraction, crop regions, quality scoring
- **Apple Vision Pro / WebXR**: Spatial personas, 3D room layouts (boardroom/amphitheater/lounge), hand/eye tracking
- **IoT Room Control**: Voice-activated lights/temp/shades/display, presets (presentation/discussion/break/focus)
- **Adaptive Beamforming**: Directional audio, polar beam patterns (auto/directional/omni/interview), per-user SNR profiles

### Meeting Replay with Director Cuts
- Cinematic replay with AI-optimized camera angles
- Key moments timeline (intro, presentation, discussion, decision, action_item, wrap_up)
- AI Highlights generation (executive_summary, action_items, full_replay styles)
- View distribution analytics (Gallery/Close-Up/Dialogue percentages)

### Gamification
- Emoji Reactions (8 types, floating animations)
- Participation Leaderboard (questions=5pts, reactions=2pts, chat=1pt)

### QR Code Touchless Entry & Ghost Booking Prevention
- QR code generation/validation with expiry and max-use tracking
- Activity pinging, idle detection, auto-release, configurable timeouts

### Enhanced Sentiment Dashboard
- Per-participant heatmap (attention/confusion/engagement/energy)
- AI recommendations (clarify/engage/break/energize)

### Organization & Privacy
- Internal/External attendee classification
- Document sharing restrictions, guest permissions

### Webinar Mode (1000+ attendees)
- Multi-Role: Host > Coordinator > Presenter > Panelist > Attendee
- Presentation slides, Q&A, hand raises, noise cancellation

### Core Meeting Features
- WebRTC conferencing, screen share, cloud recording, auto-transcription
- AI meeting notes, virtual backgrounds, P2P file sharing

## Key API Routes (New)
### SLAM & 360 Framing: `/api/karau/spatial/`
### WebXR: `/api/karau/webxr/`
### IoT Control: `/api/karau/iot/`
### Beamforming: `/api/karau/beamforming/`
### Replay: `/api/karau/replay/`

## Backlog
### P1
- Virtual breakout lounges with avatar movement
- Interactive challenges/polls
### P2
- Live Stripe API keys
- Biometric feed verification (anti-deepfake)
### P3
- Hardware manufacturer partnerships for SLAM/360/beamforming devices

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test User: test@medmatch.io / TestPassword123!

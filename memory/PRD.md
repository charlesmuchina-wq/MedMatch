# AI KARAU - Distance Zero Platform

## Product Overview
AI KARAU is an intelligent, immersive video meeting platform with "Distance Zero" design philosophy - making every participant feel physically present regardless of location.

## Core Features Implemented

### Foundation
- Multi-role webinar system (Host, Panelist, Attendee)
- Cloud recordings with transcription (OpenAI Whisper)
- Stripe payment integration (test keys)
- i18n internationalization
- Noise cancellation (rnnoise-wasm)
- Speaker detection (hark.js)

### Distance Zero - Phase 1 (Core AI)
- AI Assistant with voice commands
- AI Meeting Coach (real-time presentation tips)
- Eye contact correction
- Spatial audio
- Live transcription with multi-language captions
- AI-powered video framing
- Gamification (leaderboard, emoji reactions)
- Cinematic Director Mode (AI camera switching)
- QR Code touchless entry
- Ghost Booking prevention
- Enhanced Sentiment Dashboard
- Multiplayer Copilot (cross-meeting context)

### Distance Zero - Phase 2 (Hardware Layer - MOCKED)
- SLAM Spatial Tracking
- 360° Multi-Focus Camera
- Adaptive Beamforming Audio
- WebXR / Vision Pro
- IoT Room Control
- Hardware Discovery
- Biometric Verification

### Distance Zero - Phase 3 (Interactive Tools)
- Proactive AI-Driven Agenda
- Predictive Resource Allocation (MOCKED)
- Real-time Polls & Quizzes (4 types: poll, quiz, word cloud, rating)
- Automated Action Item Tracker
- Cinematic Meeting Replay

### UI Polish (Feb 2026)
- **FeatureToolbar:** Redesigned bottom control bar with categorized groups (Media, AI Suite, Collaborate, Spatial & Hardware) replacing flat icon row
- **Feature Command Bar:** Searchable Cmd+K palette listing all features with descriptions
- **"More Tools" Expandable Tray:** Secondary features in collapsible tray with category labels
- **Enhanced Panel Designs:** Consistent gradient header system, animated gauge charts, type-selector cards, animated vote bars
- **CSS Animation System:** Panel slide-in, command bar, gauge fill, vote flash, tooltip animations
- **Routing Fix:** Meeting join now routes to WebinarLiveRoom (with all features) instead of basic MeetingRoom

## Architecture
- **Frontend:** React + Tailwind + Shadcn UI
- **Backend:** FastAPI + MongoDB
- **Auth:** JWT-based
- **LLM:** Emergent LLM Key (OpenAI)
- **Payments:** Stripe (test mode)

## Key Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test User: test@medmatch.io / TestPassword123!

## Mocked Integrations
- Stripe (test keys)
- Hardware APIs: slam.py, beamforming.py, envcontrol.py, webxr.py
- Resource prediction: resources.py

## Backlog
- P2: Transition mocked hardware features to real implementations
- P3: Live Stripe payment keys
- P2: Refactor WebinarLiveRoom.jsx (1200+ lines) into smaller components

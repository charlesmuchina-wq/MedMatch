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
- Cinematic Director Mode
- QR Code touchless entry
- Ghost Booking prevention
- Enhanced Sentiment Dashboard
- Multiplayer Copilot (cross-meeting context)

### Distance Zero - Phase 2 (Hardware Layer - MOCKED)
- SLAM, 360° Camera, Beamforming, WebXR, IoT, Hardware Discovery, Biometric

### Distance Zero - Phase 3 (Interactive Tools)
- AI Agenda, Resource Allocation, Polls & Quizzes, Action Items, Meeting Replay

### UI Polish (Feb 2026)
- FeatureToolbar with grouped categories
- Feature Command Bar (Cmd+K)
- More Tools expandable tray
- Enhanced panel designs with animations
- Routing fix: meeting join → WebinarLiveRoom

### Production-Ready Refactor (Feb 2026)
- **WebinarLiveRoom.jsx:** 1197 → 475 lines (60% reduction)
- **Extracted hooks:** useWebRTC.js (128 lines), useWebinarActions.js (140 lines)
- **Extracted components:** TopBar (52), VideoStage (125), SidePanel (61), QAPanel (64), ParticipantsPanel (92), ControlsPanel (38)
- **React.memo** on all extracted components
- **useCallback** for all event handlers
- **useMemo** for derived state (canStream, canControl, isHost, pendingQs)
- **React.lazy + Suspense** for 15+ side panels (lazy-loaded on demand)
- **Throttled polling:** Q&A 4s, engagement 30s, sentiment 10s, coach 60s

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
- Stripe (test keys), Hardware APIs, Resource prediction

## Backlog
- P2: Transition mocked hardware features to real implementations
- P3: Live Stripe payment keys

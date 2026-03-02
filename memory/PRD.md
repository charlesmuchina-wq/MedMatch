# AI KARAU - Distance Zero Platform

## Product Overview
AI KARAU is an intelligent, immersive video meeting platform with "Distance Zero" design philosophy - making every participant feel physically present regardless of location.

## Core Features Implemented

### Foundation
- Multi-role webinar system (Host, Panelist, Attendee)
- Cloud recordings with transcription (OpenAI Whisper)
- Stripe payment integration (test keys)
- Noise cancellation (rnnoise-wasm)
- Speaker detection (hark.js)

### i18n Internationalization (Mar 2026)
- **Full i18n coverage**: All KarauMeet pages use `t()` translation function - no hardcoded English
- **Language selector on login page**: Users choose language before authentication
- **40+ languages supported**: English, Portuguese (PT+BR), German, Swahili, Spanish, French, Japanese, Arabic, Hindi, Chinese, and 30+ more
- **473 karauMeet translation keys** in en.json with manually translated keys for pt-PT, de, sw
- **AI runtime translation**: Missing translations are dynamically translated via Emergent LLM
- **Per-user language persistence**: Each user can have their own UI language independent of meeting host

### Distance Zero - Phase 1 (Core AI)
- AI Assistant with voice commands
- AI Meeting Coach (real-time presentation tips)
- Eye contact correction, Spatial audio
- Live transcription with multi-language captions
- AI-powered video framing, Cinematic Director Mode
- Gamification (leaderboard, emoji reactions)
- QR Code touchless entry, Ghost Booking prevention
- Enhanced Sentiment Dashboard, Multiplayer Copilot

### Distance Zero - Phase 2 (Hardware Layer - MOCKED)
- SLAM, 360 Camera, Beamforming, WebXR, IoT, Hardware Discovery, Biometric

### Distance Zero - Phase 3 (Interactive Tools)
- AI Agenda, Resource Allocation, Polls & Quizzes, Action Items, Meeting Replay

### UI/UX Complete Redesign (Mar 2026)
- **KarauMeetLogin**: Split layout with AI feature showcase, language selector, trust badges
- **KarauMeetDashboard**: Bento grid, AI Capabilities banner (8 features), stats, Meeting Insights card (AI summaries/decisions/actions), featured Next Meeting with countdown, collapsible upcoming
- **KarauMeetPortal**: Redesigned sidebar with gradient icons, AI POWERED badge
- **MeetingLobby**: Immersive pre-meeting lobby with AI feature badges
- **How-To Guide** (`/karau-meet/guide`): 9 sections, 50 articles, role-based filters (Enterprise, Admin, Host, Attendee), searchable
- **Seed Data**: 5 past + 5 upcoming meetings, 5 past + 5 upcoming webinars, enriched AI notes

### Performance Refactor (Feb 2026)
- WebinarLiveRoom: 1197 -> 475 lines (60% reduction)
- React.lazy for 15+ side panels, useCallback/React.memo memoization
- Custom hooks: usePanelManager, useWebinarState, useWebinarLifecycle, usePolling

## Architecture
- **Frontend:** React + Tailwind + Shadcn UI + react-i18next
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
- P2: Enhance mocked hardware APIs (interactive connection states, calibration flows)
- P2: Add UI micro-animations across panels
- P3: Transition mocked hardware features to real implementations
- P3: Live Stripe payment keys

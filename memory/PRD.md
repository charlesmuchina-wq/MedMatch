# AI KARAU - Distance Zero Platform

## Product Overview
AI KARAU is an intelligent, immersive video meeting platform with "Distance Zero" design philosophy - making every participant feel physically present regardless of location.

## Core Features Implemented

### Foundation
- Multi-role webinar system (Host, Panelist, Attendee)
- Cloud recordings with transcription (OpenAI Whisper)
- Stripe payment integration (test keys)
- Noise cancellation (rnnoise-wasm), Speaker detection (hark.js)

### i18n Internationalization
- **Full i18n coverage**: All KarauMeet pages use `t()` — no hardcoded English
- **Language selector on login page**: Users choose language before authentication
- **53 locale files, 60 language variants**: en, pt-PT, pt-BR, de, sw, es, fr, ja, ar, hi, zh, and 40+ more
- **473 karauMeet translation keys** with manual translations for pt-PT, de, sw
- **AI runtime translation** for missing keys via Emergent LLM
- **Language preference sync**: Caption display language auto-set from user's i18n locale

### Distance Zero - AI Features
- AI Assistant, AI Meeting Coach, Eye contact correction, Spatial audio
- Live transcription (35+ caption languages), Cinematic Director Mode
- Gamification, QR Code entry, Ghost Booking prevention
- Sentiment Dashboard, Multiplayer Copilot

### Hardware Integrations (Enhanced Mocked - Mar 2026)
- **SLAM Spatial Tracking**: Phased connect flow (scanning → initializing → connected)
- **360° Camera / Panoramic**: Speaker pulse simulation, auto-tracking preview
- **Beamforming Mics**: Radar sweep animation, beam direction visualization
- **IoT Room Controls**: Voice-activated, presets, animated loading
- **Biometric Verification**: Staggered trust card entries with animations
- **Hardware Discovery**: Animated scan with pulse-glow effects

### UI/UX
- Complete redesign: Login, Dashboard, Portal sidebar, Lobby, How-To Guide
- **Meeting Insights card**: AI summaries, decisions, action items from past meetings
- **Next Meeting**: Featured countdown card, collapsible rest
- **How-To Guide** (`/karau-meet/guide`): 9 sections, 50 articles, role-based filters
- **Micro-animations** (`animations.css`): 17 keyframes, 15+ utility classes
  - Entrance: fade-in-up, scale, slide-up with stagger delays
  - Interaction: hover-lift, hover-glow, hover-scale, card-interactive
  - Hardware: pulse-ring, radar-sweep, scan-rotate, bar-grow, shimmer

### Performance
- WebinarLiveRoom: 1197 → 475 lines, React.lazy for 15+ panels, memoization

## Architecture
- Frontend: React + Tailwind + Shadcn UI + i18n (53 locales)
- Backend: FastAPI + MongoDB
- Auth: JWT | LLM: Emergent LLM Key | Payments: Stripe (test)

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test: test@medmatch.io / TestPassword123!

## Mocked: Stripe (test keys), Hardware APIs (enhanced), Resource prediction

## Backlog
- P3: Live Stripe payment keys (waiting on user)
- P3: Transition mocked hardware to real implementations

# AI KARAU + ENZI - Product Requirements Document

## Original Problem Statement
Build a dual-platform communication suite: "AI KARAU" (webinar tool) and "ENZI" (professional-grade messenger). ENZI is the primary focus — a futuristic, AI-driven "Actionable Intelligence" hub with liquid glass aesthetics, bento grid layouts, and predictive behavior.

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + react-markdown + react-syntax-highlighter
- Backend: FastAPI + MongoDB + emergentintegrations + msal + resend
- Real-time: WebSocket at /api/lumi/ws/{user_id}
- AI: GPT-4.1-mini via Emergent LLM Key
- Payments: Stripe via emergentintegrations (LIVE test mode)

## Unified Authentication (All 3 Portals)
All portals share the same `/api/auth/login` backend. Standardized auth providers:
- **Google SSO** (Emergent-managed) - All portals
- **Microsoft SSO** (MSAL) - All portals
- **Apple Sign-In** - All portals (config-ready)
- **GitHub SSO** (MOCKED demo) - All portals
- **Passkeys/WebAuthn** - ENZI + AI KARAU
- **Phone OTP** - ENZI (planned)
- **Email/Password** - All portals
- Credentials: admin@medmatch.com / Swampdrainer2026!, test@medmatch.io / TestPassword123!

## Completed Features

### Cross-Portal Meeting Integration
- Create AI KARAU meetings from ENZI, instant + scheduled, channel notifications

### Bot Store/Marketplace
- 8 pre-built bots with quick-trigger Bot Actions Bar in channels

### End-to-End Encryption (E2EE)
- ECDH P-256 + AES-GCM, client-side keys, DM indicators

### Live Stripe Payments
- 4 premium tiers ($9.99-$99.99), real Stripe checkout (test mode)

### Advanced Behavioral Modeling
- Context-aware triggers, smart suggestions, usage insights, engagement scoring

### Predictive Zero-Click Navigation
- Channels/DMs sorted by predicted usage with Zap indicators

### Screen Sharing (WebRTC)
- Already in MeetingRoom.jsx with getDisplayMedia

### Other Features
- Rich Markdown + code blocks, Sentiment Analysis, AI Summaries, Scheduled Messages
- AI Writing Assistant, Invite System, Channel/Webhook Templates, Kinetic Typography
- Notification customization, Domain colleague discovery, Meeting History

## Test Results (All 100%)
- Auth Duplicate: 12/12 BE, all 3 portals FE
- Batch A-C: All passed 100%

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test: test@medmatch.io / TestPassword123!

## Remaining Enhancements
- Voice/Video improvements (noise cancellation, virtual backgrounds)
- Advanced ML for better predictions
- Mobile optimization
- Team Analytics Dashboard (premium feature idea)

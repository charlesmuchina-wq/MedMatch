# AI KARAU + ENZI - Product Requirements Document

## Original Problem Statement
Build a dual-platform communication suite: "AI KARAU" (webinar tool) and "ENZI" (professional-grade messenger, formerly LUMI). ENZI is the primary focus — a futuristic, AI-driven "Actionable Intelligence" hub.

## What's Been Implemented

### Phase 1 - Bot Store/Marketplace (Completed - March 8, 2026)
- Bot catalog with 8 pre-built bots: Standup, Reminder, Poll, Meeting, Welcome, Summary, Translator, GitHub Notify
- Browse/install/uninstall bots per channel with category filtering and search
- Installed bots tab with remove functionality
- Backend: `/api/lumi/bots/catalog`, `/api/lumi/bots/install`, `/api/lumi/bots/installed`, `/api/lumi/bots/uninstall/{id}`
- Frontend: BotStoreModal component with Browse/Installed tabs, category chips, channel selector

### Meeting History Panel (Completed - March 8, 2026)
- Full meeting history with status badges (Waiting, Active, Scheduled, Ended)
- Paginated API with total count
- "New Meeting" shortcut to create meetings from history view
- Backend: `/api/lumi/meetings/history`
- Frontend: MeetingHistoryPanel component

### Legacy Admin Display Fix (Completed - March 8, 2026)
- Auth method badges for ALL providers: Google SSO, Microsoft SSO, GitHub SSO, Passkey Auth, Password Auth
- Admin user now correctly shows "Password Auth" badge instead of blank

### Expanded Authentication (Completed - March 8, 2026)
- GitHub SSO (MOCKED/demo mode)
- Passkeys/WebAuthn: register + login endpoints
- 6 auth providers on login page: Google, Microsoft, Apple, GitHub, Phone OTP, Passkey
- Backend: `/api/auth/github/*`, `/api/auth/passkey/*`

### Cross-Portal Integration (Completed - March 8, 2026)
- Create AI KARAU meetings from ENZI messenger
- Instant + scheduled meeting creation with channel notifications
- Dashboard bento tile + chat header toolbar button
- Backend: `/api/lumi/meetings/quick`, `/api/lumi/meetings/schedule`, `/api/lumi/meetings/active`

### Previous Session Features
- Rich Message Formatting (markdown, code blocks, tables)
- Sentiment Analysis, AI Summaries, Scheduled Messages
- Channel Templates, Webhook Templates, Kinetic Typography
- Advanced Invite System (Email, SMS, social media)
- Sidebar restructure, Notification customization
- Google SSO + Microsoft SSO + email/password auth
- AI Writing Assistant, Smart Buckets, MS Calendar Sync, Predictive Nav
- Compliance (HIPAA/GDPR), Dark/Light mode, Keyboard shortcuts

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + react-markdown + react-syntax-highlighter
- Backend: FastAPI + MongoDB + emergentintegrations + msal + resend
- Real-time: WebSocket at /api/lumi/ws/{user_id}
- AI: GPT-4.1-mini via Emergent LLM Key

## Pending / Backlog
### P1
- Full Predictive Zero-Click Navigation: reorder UI elements by predicted user intent

### P2
- End-to-End Encryption (E2EE) — client-side key gen, key exchange, encrypted DMs
- Screen Sharing in Calls (WebRTC)
- Live Stripe Payment Gateway
- Advanced Behavioral Modeling

### Refactoring
- LumiMessenger.jsx (1250+ lines) -> smaller components + custom hooks

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test: test@medmatch.io / TestPassword123!
- Azure AD: Client ID 40a72049..., Tenant d4e8b623...

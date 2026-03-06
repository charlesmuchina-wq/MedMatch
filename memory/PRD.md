# AI KARAU + LUMI - Product Requirements Document

## Original Problem Statement
Build a dual-platform communication suite: "AI KARAU" (webinar tool) and "LUMI" (professional-grade messenger). LUMI is the primary focus — a futuristic, AI-driven "Actionable Intelligence" hub with Liquid Glass aesthetics and predictive design.

## What's Been Implemented

### Core Infrastructure
- Full LUMI messenger with channels, DMs, WebSocket real-time messaging
- Google SSO + **Microsoft SSO (Azure AD)** + email/password authentication
- Content moderation, compliance framework (HIPAA/GDPR/PIPL/APPI/UK DPA)
- Message retention & holds system, admin audit logs
- Dark/Light mode toggle, keyboard shortcuts

### Microsoft SSO (Completed - March 6, 2026)
- Full OAuth2 flow: Login → Microsoft auth → Callback → Session creation → LUMI redirect
- Backend: `/api/auth/microsoft/login`, `/api/auth/microsoft/callback`, `/api/auth/microsoft/config`
- Generic session validation: `/api/auth/session/validate` (works for both Google and MS SSO)
- Frontend: "Sign in with Microsoft" button on LUMI login page
- Scopes: openid, profile, email, User.Read, Calendars.Read
- **Testing**: 100% (9/9 backend, all frontend verified)

### AI Writing Assistant + Templates (Completed)
- **Refine**: 4 tones (Professional, Friendly, Assertive, Concise)
- **Smart Reply**: Context-aware suggestions
- **Translate**: 10 languages
- **Voice-to-Text**: Whisper + LLM polishing
- **Save as Template**: CRUD + library UI, auto-appears after AI actions
- Backend: `/api/lumi/ai/*`, `/api/lumi/templates/*`

### Smart Buckets (Completed)
- AI-powered categorization: Urgent, Action Required, Meeting Requests, FYI, Social
- Clickable dashboard buckets with real counts, detail panel with dismiss
- Auto-scan on dashboard load using GPT-4.1-mini
- Backend: `/api/lumi/buckets/*`

### Channel Invite System (Completed)
- 2-step channel creation (details → invite emails)
- Private channels, requires_approval flag, accept/decline invites
- Backend: `/api/lumi/channels/{id}/invite`, `/api/lumi/invites/*`

### Futuristic UI (Liquid Glass Phase)
- Bento Grid Command Center, Liquid Glass CSS, Outfit font
- LUMI logo: pixel-analyzed icon crops, transparent versions
- Dark mode scoped via `lumi-light-panel` class

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + Outfit font
- Backend: FastAPI + MongoDB + emergentintegrations + msal
- Real-time: WebSocket at /api/lumi/ws/{user_id}
- Auth: Google SSO (Emergent) + Microsoft SSO (Azure AD) + email/password

## Pending / Backlog
- **P2:** User Status Sync (Microsoft Calendar) — now possible with MS SSO + Calendars.Read scope
- **P2:** Predictive Zero-Click Navigation
- **P2:** Behavioral Modeling & Context-Aware Triggers
- **P2:** Kinetic Typography & Micro-interactions
- **P2:** End-to-End Encryption (E2EE)
- **P2:** Live Payment Gateway (Stripe)
- **P2:** Passkeys & Biometric Authentication
- **P2:** Template Sharing (team-wide template library)
- **P3:** Legacy Admin User Display fix

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test: test@medmatch.io / TestPassword123!
- Azure AD: Client ID 40a72049..., Tenant d4e8b623...

# AI KARAU + LUMI - Product Requirements Document

## Original Problem Statement
Build a dual-platform communication suite: "AI KARAU" (webinar tool) and "LUMI" (professional-grade messenger). LUMI is the primary focus — a futuristic, AI-driven "Actionable Intelligence" hub with Liquid Glass aesthetics and predictive design.

## What's Been Implemented

### Core Infrastructure
- Full LUMI messenger with channels, DMs, WebSocket real-time messaging
- Google SSO authentication, Microsoft SSO placeholder
- Content moderation, compliance framework (HIPAA/GDPR/PIPL/APPI/UK DPA)
- Message retention & holds system, admin audit logs
- Dark/Light mode toggle, keyboard shortcuts

### Futuristic UI (Liquid Glass Phase)
- **Bento Grid Command Center**: Dashboard with Quick Actions, Recent Conversations (channels + DMs), AI Intelligence, Smart Buckets
- **Liquid Glass CSS System**: glass-surface, glass-card, bento-tile utility classes
- **Official LUMI Logo**: Pixel-analyzed icon-only crop (526x273) for clean rendering; transparent versions for light backgrounds
- Dark mode scoped via `lumi-light-panel` class to prevent text visibility issues

### AI Writing Assistant (Completed)
- **Refine**: 4 tones (Professional, Friendly, Assertive, Concise)
- **Smart Reply**: Context-aware suggestions from conversation history
- **Translate**: 10 languages
- **Voice-to-Text**: Whisper transcription + LLM polishing
- Backend: `/api/lumi/ai/refine`, `smart-reply`, `translate`, `voice-to-text`

### Save as Template (Completed - March 6, 2026)
- Save AI-refined/translated messages as reusable templates
- Template library UI in AI toolbar (browse, apply, delete)
- "Save" button appears automatically after AI refine/translate actions
- Templates sorted by use_count (most used first)
- Backend: `/api/lumi/templates` (full CRUD + apply endpoint)
- **Testing**: 100% (21/21 backend, all frontend verified)

### Smart Buckets (Completed - March 6, 2026)
- AI-powered message categorization: Urgent, Action Required, Meeting Requests, FYI, Social
- Clickable dashboard buckets with real-time counts
- Bucket detail panel with dismissible message items
- Auto-scan on dashboard load using GPT-4.1-mini
- Backend: `/api/lumi/buckets/counts`, `/{category}`, `/scan`, `/{category}/{id}/dismiss`
- **Testing**: 100% (part of iteration 187)

### Channel Invite System (Completed)
- 2-step channel creation (details → invite emails)
- Private channels, requires_approval flag
- Invite by email, accept/decline on dashboard
- Backend: `/api/lumi/channels/{id}/invite`, `/api/lumi/invites`, `/api/lumi/invites/{id}/respond`

### Navigation
- Return to Portal link in both LUMI and AI KARAU sidebars
- LUMI Mini Messenger panel inside meeting rooms with unread badges

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + Outfit font
- Backend: FastAPI + MongoDB + emergentintegrations (LLM)
- Real-time: WebSocket at /api/lumi/ws/{user_id}
- CSS: Liquid Glass design system; dark mode scoped via lumi-light-panel

## Pending / Backlog
- **P1:** Microsoft SSO finalization (blocked on Azure API keys)
- **P2:** User Status Sync (Microsoft Calendar)
- **P2:** Predictive Zero-Click Navigation
- **P2:** Behavioral Modeling & Context-Aware Triggers
- **P2:** Kinetic Typography & Micro-interactions
- **P2:** End-to-End Encryption (E2EE)
- **P2:** Live Payment Gateway (Stripe)
- **P2:** Passkeys & Biometric Authentication
- **P3:** Legacy Admin User Display fix

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test: test@medmatch.io / TestPassword123!

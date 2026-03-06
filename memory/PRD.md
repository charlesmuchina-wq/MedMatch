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
- **Bento Grid Command Center**: Modular dashboard with glass-morphism tiles for Quick Actions, Recent Conversations, AI Intelligence stats, Smart Buckets preview
- **Liquid Glass CSS System**: glass-surface, glass-card, bento-tile utility classes
- **Outfit Font**: Imported for futuristic heading typography
- **Official LUMI Logo**: Icon-only crops for scalable rendering; transparent versions for light backgrounds
- **Portal Title**: Vibrant cyan-purple-pink gradient for "MedMatch-AI KARAU"

### AI Writing Assistant (Completed - March 6, 2026)
- **Refine**: Tone adjustment (Professional, Friendly, Assertive, Concise) via LLM
- **Smart Reply**: Context-aware reply suggestions based on conversation history
- **Translate**: Real-time translation to 10 languages
- **Voice-to-Text**: Whisper transcription with LLM polishing
- Backend: `/api/lumi/ai/refine`, `/api/lumi/ai/smart-reply`, `/api/lumi/ai/translate`, `/api/lumi/ai/voice-to-text`
- **Testing**: 100% pass rate (18/18 backend, all frontend verified)

### Dashboard & Channel Invite System (Completed - March 6, 2026)
- **Enhanced Dashboard**: Recent Conversations panel combining channels + DMs with unread counts
- **Pending Invites Panel**: Shows channel invites with Accept/Decline buttons on dashboard
- **Channel Creation with Authorization**: 2-step flow (details → invite emails), supports private channels, requires_approval flag
- **Channel Invite System**: Invite by email, accept/decline invites, join approval for restricted channels
- Backend: `/api/lumi/channels/{id}/invite`, `/api/lumi/invites`, `/api/lumi/invites/{id}/respond`
- **Testing**: 100% pass rate (12/12 backend tests, all frontend verified)

### Logo & Dark Mode Accessibility Fix (Completed - March 6, 2026)
- **Logo Fix**: Created icon-only PNG crops from full logo (just chat bubble, no text). Renders properly as icons at any size.
- **Dark Mode Root Cause Fix**: CSS rules `html.dark .bg-white/bg-slate-50 { color: #111827 }` were overriding Tailwind text-white with higher specificity. Fix: restructured LumiMessenger JSX so dashboard renders in its own dark container (bg-[#0D1117]), while chat area wraps in scoped `lumi-light-panel` class.
- **Testing**: 100% pass rate (11/11 frontend features verified)

### Navigation
- Return to Portal link in both LUMI and AI KARAU sidebars
- LUMI Messenger link in AI KARAU sidebar
- LUMI Mini Messenger panel inside meeting rooms with unread badges

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + Outfit font
- Backend: FastAPI + MongoDB + emergentintegrations (LLM)
- Real-time: WebSocket at /api/lumi/ws/{user_id}
- CSS: Liquid Glass design system (glass-surface, bento-tile)
- Dark Mode: Scoped via `lumi-light-panel` class for white-background sections

## Pending / Backlog
- **P1:** Save as Template - Allow saving refined AI messages as reusable templates
- **P1:** Task-Driven Side Layout with Smart Buckets (Urgent, Action Required, Meeting Requests) - backend ML categorization
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

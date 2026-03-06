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
- **Bento Grid Command Center**: Modular dashboard with Quick Actions, Recent Conversations (channels + DMs), AI Intelligence stats, Smart Buckets
- **Liquid Glass CSS System**: glass-surface, glass-card, bento-tile utility classes
- **Outfit Font**: Imported for futuristic heading typography
- **Official LUMI Logo**: Pixel-analyzed icon-only crop (526x273, rows 108-371) for clean rendering at any size. Transparent versions for light backgrounds.
- **Portal Title**: Vibrant cyan-purple-pink gradient for "MedMatch-AI KARAU"

### AI Writing Assistant (Completed - March 6, 2026)
- **Refine**: Tone adjustment (Professional, Friendly, Assertive, Concise) via LLM
- **Smart Reply**: Context-aware reply suggestions based on conversation history
- **Translate**: Real-time translation to 10 languages
- **Voice-to-Text**: Whisper transcription with LLM polishing
- Backend: `/api/lumi/ai/refine`, `/api/lumi/ai/smart-reply`, `/api/lumi/ai/translate`, `/api/lumi/ai/voice-to-text`

### Dashboard & Channel Invite System (Completed - March 6, 2026)
- **Enhanced Dashboard**: Recent Conversations panel combining channels + DMs with unread counts
- **Pending Invites Panel**: Shows channel invites with Accept/Decline buttons on dashboard
- **Channel Creation with Authorization**: 2-step flow (details → invite emails), private channels, requires_approval flag
- **Channel Invite System**: Invite by email, accept/decline invites, join approval for restricted channels
- Backend: `/api/lumi/channels/{id}/invite`, `/api/lumi/invites`, `/api/lumi/invites/{id}/respond`

### Logo & Dark Mode Accessibility (Final Fix - March 6, 2026)
- **Logo Root Cause**: Original PNG (512x523) contained full logo + "LUMI" text. When squeezed into icon containers, text was chopped. Fix: pixel-analyzed crop to just chat bubble (rows 108-371), applied across PortalSelector, LumiBrand, LumiMiniMessenger.
- **Dark Mode Root Cause**: CSS `html.dark .bg-white/.bg-slate-50 { color: #111827 }` had higher specificity than Tailwind `text-white`. Fix: Restructured JSX — dashboard renders in own dark container (bg-[#0D1117]), chat area uses scoped `lumi-light-panel` class.
- **Testing**: 100% pass rate across 4 test iterations (iterations 183-186)

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + Outfit font
- Backend: FastAPI + MongoDB + emergentintegrations (LLM)
- Real-time: WebSocket at /api/lumi/ws/{user_id}
- CSS: Liquid Glass design system; dark mode scoped via `lumi-light-panel` class

## Pending / Backlog
- **P1:** Save as Template - save refined AI messages as reusable templates
- **P1:** Task-Driven Smart Buckets - ML-powered message categorization (Urgent, Action Required, Meeting Requests)
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

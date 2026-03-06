# AI KARAU + LUMI - Product Requirements Document

## Original Problem Statement
Build a dual-platform communication suite: "AI KARAU" (webinar tool) and "LUMI" (professional-grade messenger). LUMI is the primary focus — a futuristic, AI-driven "Actionable Intelligence" hub with Liquid Glass aesthetics and predictive design.

## What's Been Implemented (March 2026)

### Core Infrastructure
- Full LUMI messenger with channels, DMs, WebSocket real-time messaging
- Google SSO authentication, Microsoft SSO placeholder
- Content moderation, compliance framework (HIPAA/GDPR/PIPL/APPI/UK DPA)
- Message retention & holds system, admin audit logs
- Dark/Light mode toggle, keyboard shortcuts

### Futuristic UI (Liquid Glass Phase)
- **Bento Grid Command Center**: Modular dashboard with glass-morphism tiles for Quick Actions, Recent Channels, AI Intelligence stats, Smart Buckets preview
- **Liquid Glass CSS System**: glass-surface, glass-card, bento-tile utility classes
- **Outfit Font**: Imported for futuristic heading typography
- **Official LUMI Logo**: Integrated throughout (sidebar, login, portal, welcome, mini messenger)
- **Portal Title**: Vibrant cyan-purple-pink gradient for "MedMatch-AI KARAU"

### AI Writing Assistant (Completed - March 6, 2026)
- **Refine**: Tone adjustment (Professional, Friendly, Assertive, Concise) via LLM
- **Smart Reply**: Context-aware reply suggestions based on conversation history
- **Translate**: Real-time translation to 10 languages (Spanish, French, German, Japanese, Chinese, Korean, Portuguese, Arabic, Hindi, Russian)
- **Voice-to-Text**: Whisper transcription with LLM polishing to remove filler words
- Backend: `/api/lumi/ai/refine`, `/api/lumi/ai/smart-reply`, `/api/lumi/ai/translate`, `/api/lumi/ai/voice-to-text`
- Frontend: `AIWritingToolbar.jsx` component integrated above message input
- **Testing**: 100% pass rate (18/18 backend tests, all frontend features verified)

### Navigation
- Return to Portal link in both LUMI and AI KARAU sidebars
- LUMI Messenger link in AI KARAU sidebar
- LUMI Mini Messenger panel inside meeting rooms with unread badges

### Accessibility Fixes
- Fixed `e.key.toLowerCase()` crash on mobile
- Fixed global dark mode CSS variables overriding Tailwind utilities
- All text readable in both dark and light modes

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + Outfit font
- Backend: FastAPI + MongoDB + emergentintegrations (LLM)
- Real-time: WebSocket at /api/lumi/ws/{user_id}
- CSS: Liquid Glass design system (glass-surface, bento-tile)

## Pending / Backlog
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

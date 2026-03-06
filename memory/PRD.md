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
- **Bento Grid Command Center**: Modular dashboard replacing simple welcome text, with glass-morphism tiles for Quick Actions, Recent Channels, AI Intelligence stats, and Smart Buckets preview
- **Liquid Glass CSS System**: glass-surface, glass-card, bento-tile utility classes with backdrop-blur, hover transitions, and depth layering
- **Outfit Font**: Imported for futuristic heading typography
- **Official LUMI Logo**: Integrated throughout (sidebar, login, portal, welcome screen, mini messenger)
- **Portal Title**: Vibrant cyan→purple→pink gradient for "MedMatch-AI KARAU"

### Navigation
- Return to Portal link in both LUMI and AI KARAU sidebars
- LUMI Messenger link in AI KARAU sidebar
- LUMI Mini Messenger panel inside meeting rooms with unread badges

### Accessibility Fixes
- Fixed `e.key.toLowerCase()` crash on mobile devices (guard for touch events)
- Fixed global dark mode CSS variables overriding Tailwind utilities on light-background panels
- Comprehensive `html.dark .bg-white` CSS reset for modals/panels
- All text readable in both dark and light modes across all pages

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + Outfit font
- Backend: FastAPI + MongoDB
- Real-time: WebSocket at /api/lumi/ws/{user_id}
- CSS: Liquid Glass design system (glass-surface, bento-tile)

## Pending / Backlog
- **P1:** AI Writing Assistant (tone refinement, summarization, co-creation model)
- **P1:** Smart Buckets engine (backend ML categorization: Urgent, Action Required, Meeting Requests)
- **P1:** Predictive/Behavioral modeling (suggest actions based on conversation context)
- **P1:** Real-time translation (DeepL/Google free tier)
- **P1:** Voice-to-text with polishing (OpenAI Whisper)
- **P0:** Microsoft SSO finalization (blocked on Azure API keys)
- **P2:** Full Knowledge Graph + MS Project/SharePoint integration
- **P2:** End-to-End Encryption (E2EE)
- **P3:** Stripe live payment transition

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test: test@medmatch.io / TestPassword123!

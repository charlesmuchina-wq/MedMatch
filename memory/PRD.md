# AI KARAU + ENZI - Product Requirements Document

## Original Problem Statement
Build a dual-platform communication suite: "AI KARAU" (webinar tool) and "ENZI" (professional-grade messenger), plus "MedMatch AI" (job-seeking toolkit). ENZI is the primary focus — a futuristic, AI-driven "Actionable Intelligence" hub with liquid glass aesthetics, bento grid layouts, and predictive behavior. The platform offers bundled packages with a unified workspace for running portals side-by-side.

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + react-markdown + react-syntax-highlighter
- Backend: FastAPI + MongoDB + emergentintegrations + msal + resend
- Real-time: WebSocket at /api/lumi/ws/{user_id}
- AI: GPT-4o via Emergent LLM Key (for bot actions)
- Payments: Stripe via emergentintegrations (LIVE test mode)

## Unified Authentication (All 3 Portals)
All portals share `/api/auth/login`. Auth providers: Google SSO, Microsoft SSO, Apple, GitHub (mocked), Passkeys/WebAuthn, Email/Password. Cross-portal sync via `/api/portal/sync-session`.
- Credentials: admin@medmatch.com / Swampdrainer2026!, test@medmatch.io / TestPassword123!

## Portal Packaging System (COMPLETED)
3 packages: Standard (KARAU+ENZI), Standalone (MedMatch), Enterprise (all 3).

## Portal Workspace (COMPLETED)
Unified multi-portal workspace with side-by-side portal support.

## Bot Marketplace — AI-Powered (COMPLETED - Mar 12, 2026)
Full bot lifecycle management with 18 specialized AI-powered bots across 4 categories:
- **Job Toolkit** (5 bots): Talent Matcher, Resume Architect, Interview Copilot, EZ Sourcing, Salary Negotiator
- **AI Meeting** (5 bots): Note-Taker, Smart Scheduler, Search Copilot, Attendance Tracker, Summary Generator
- **AI Messenger** (3 bots): Knowledge Layer, Multilingual Translator, Omnichannel Assistant
- **Security & QA** (5 bots): Compliance Audit, Visual Testing, Bias Auditor, Threat Scanner, Translation QA

Features:
- Browse catalog with category filters, ratings, install counts
- Install/uninstall/configure bots per channel
- **AI-powered responses** via GPT-4o (Emergent LLM Key) — not mocked
- **Quick action buttons** in BotActionsBar (expands to show per-bot actions)
- **Slash commands** in chat (e.g., /summarize, /match <query>, /audit)
- **SlashCommandAutocomplete** dropdown when typing / in message input
- Each bot has specialized system prompts for contextual, channel-aware responses
- Backend: `enzi_bots.py` — catalog, install, configure, action (AI), slash-commands
- Frontend: `BotStoreModal.jsx`, `BotActionsBar.jsx`, `SlashCommandAutocomplete.jsx`

## Channel Templates & Webhooks (COMPLETED)
6 channel templates, 5 webhook templates.

## Team Analytics Dashboard (COMPLETED)
Premium team analytics with engagement scores, heatmaps, period selectors.

## Meeting-to-Channel Conversion (COMPLETED - Mar 11, 2026)
KARAU meetings auto-create ENZI channels with admin approval for external members.

## Domain-Aware Routing System (COMPLETED - Mar 11, 2026)
Multi-domain routing: aikarau.com, medmatch.aikarau.com, enzilink.com, etc.

## LumiMessenger Refactoring (COMPLETED - Mar 11, 2026)
Extracted EnziSidebar.jsx and EnziDashboard.jsx from LumiMessenger.jsx (~1400→802 lines).
Verified with testing agent — no regressions.

## Other Completed Features
- End-to-End Encryption (ECDH P-256 + AES-GCM)
- Live Stripe Payments (4 tiers, test mode)
- Predictive Zero-Click Navigation
- Screen Sharing, Noise Cancellation, Virtual Backgrounds
- Rich Markdown, Sentiment Analysis, AI Summaries, Scheduled Messages
- AI Writing Assistant, Invite System, Kinetic Typography
- Cross-Portal Meeting Integration, Meeting History
- Advanced Behavioral Modeling with User Insights Panel

## Test Results
- iteration_207: 100% (14/14 BE, all FE - P1 AI Bot Marketplace)
- iteration_206: 100% (all FE - P0 Messenger Refactoring Verification)
- iteration_205: 100% (19/19 BE, all FE - Bot Marketplace UI)
- iteration_204: 100% (12/12 BE, 6/6 FE - Domain Routing)

## Remaining Tasks
- **P2**: Further refactor LumiMessenger.jsx (~802 lines) — extract chat view component
- **P2**: Voice/Video Call enhancements (recording, transcription, background effects)
- **P3**: Advanced Writing Assistant with co-editing
- **P3**: Mobile-first optimization
- **P3**: Advanced ML for channel predictions

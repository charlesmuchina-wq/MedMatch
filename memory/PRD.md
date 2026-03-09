# AI KARAU + ENZI - Product Requirements Document

## Original Problem Statement
Build a dual-platform communication suite: "AI KARAU" (webinar tool) and "ENZI" (professional-grade messenger), plus "MedMatch AI" (job-seeking toolkit). ENZI is the primary focus — a futuristic, AI-driven "Actionable Intelligence" hub with liquid glass aesthetics, bento grid layouts, and predictive behavior. The platform offers bundled packages with a unified workspace for running portals side-by-side.

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + react-markdown + react-syntax-highlighter
- Backend: FastAPI + MongoDB + emergentintegrations + msal + resend
- Real-time: WebSocket at /api/lumi/ws/{user_id}
- AI: GPT-4.1-mini via Emergent LLM Key
- Payments: Stripe via emergentintegrations (LIVE test mode)

## Unified Authentication (All 3 Portals)
All portals share `/api/auth/login`. Auth providers: Google SSO, Microsoft SSO, Apple, GitHub (mocked), Passkeys/WebAuthn, Email/Password. Cross-portal sync via `/api/portal/sync-session`.
- Credentials: admin@medmatch.com / Swampdrainer2026!, test@medmatch.io / TestPassword123!

## Portal Packaging System (COMPLETED)
3 packages: Standard (KARAU+ENZI), Standalone (MedMatch), Enterprise (all 3).
- Landing: `PortalSelector.jsx`, Management: `PackageSelector.jsx` at /packages
- Backend: `portal_access.py` — packages, access, set-package, sync-session, check-access

## Portal Workspace (COMPLETED)
Unified multi-portal workspace with side-by-side portal support.
- Dock bar at bottom showing bundle portals (Main/Side/Dock states)
- Side panel: 3 presets (narrow/wide/half) + drag-to-resize with DragHandle
- Swap button exchanges main and side portals
- Mobile: side panel becomes full-width overlay
- Files: `PortalWorkspace.jsx`, `EnziCompactPanel.jsx`, `KarauCompactPanel.jsx`

## Bot Store/Marketplace (COMPLETED)
Full bot lifecycle management with 8 pre-built bots.
- Browse catalog with category filters (Productivity, Engagement, AI, etc.)
- Install to specific channels, uninstall, toggle active/paused
- Config panel with editable fields per bot
- Bot Actions Bar for quick commands in chat
- Backend: `enzi_bots.py` — catalog, install, uninstall, toggle, configure

## Channel Templates & Webhooks (COMPLETED)
- 6 channel templates (Project, Sprint, Incident, Standup, General)
- 5 webhook templates (GitHub, Jira, CI/CD, Slack, Monitoring)
- Create channels from templates with name prefix
- Webhook creation shows URL, events, setup instructions, curl test command
- Frontend: `ChannelToolsModal.jsx`, Backend: `enzi_channel_templates.py`, `enzi_webhook_templates.py`

## Team Analytics Dashboard (COMPLETED)
Premium team analytics with:
- Stats: Channels, Members, Messages, Active Bots with trend indicators
- Engagement Score (0-100) with gradient progress bar
- Top Channels by Activity ranking
- Activity Heatmap (7-day grid)
- Period selector (7d/30d/90d)
- File: `TeamAnalyticsDashboard.jsx`

## Other Completed Features
- End-to-End Encryption (ECDH P-256 + AES-GCM)
- Live Stripe Payments (4 tiers, test mode)
- Predictive Zero-Click Navigation
- Screen Sharing (WebRTC), Noise Cancellation, Virtual Backgrounds
- Rich Markdown, Sentiment Analysis, AI Summaries, Scheduled Messages
- AI Writing Assistant, Invite System, Kinetic Typography
- Cross-Portal Meeting Integration, Meeting History
- Advanced Behavioral Modeling with User Insights Panel

## Test Results
- iteration_202: 100% (19/19 BE, 24/24 features, all FE flows)
- iteration_201: 100% (18/18 BE)
- iteration_200: 100% FE, 77% BE (test fixture issues)
- iteration_199: 100% (25/25 BE)

## Remaining Tasks
- **P3**: Mobile-first optimization (further responsive refinements)
- **P3**: Advanced ML for better channel predictions
- **P3**: Deeper refactoring of LumiMessenger.jsx (~1350 lines)

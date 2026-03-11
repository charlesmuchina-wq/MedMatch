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

## Meeting-to-Channel Conversion (COMPLETED - Mar 11, 2026)
When a KARAU meeting ends, an ENZI channel is auto-created for continued collaboration.
- Internal members (same email domain) added automatically
- External members require admin approval
- Meeting recap posted as first message in channel
- Admin Approval Panel: global view of all pending external requests
- MeetingChannelBanner: in-channel banner showing meeting context with inline approve/deny
- Backend: `meeting_channel_sync.py` — convert, settings, pending-approvals, approve/deny-external, channels
- Frontend: `AdminApprovalPanel.jsx`, `MeetingChannelBanner.jsx`
- Hook in `karau_meet.py` end_meeting_room → convert_meeting_to_channel

## Domain-Aware Routing System (COMPLETED - Mar 11, 2026)
Multi-domain routing for production deployment with registered domains:
- `aikarau.com` / `ai.karau.com` → Full Ecosystem (all 3 portals, for recruiters)
- `medmatch.aikarau.com` → MedMatch AI (enterprise recruitment, company focus)
- `careers.aikarau.com` / `jobs.aikarau.com` → Job Seekers view
- `connect.aikarau.com` / `meet.aikarau.com` → AI KARAU Meetings
- `enzi.aikarau.com` → ENZI Messenger (subdomain)
- `enzilink.com` → ENZI Messenger (standalone domain)

Implementation:
- `DomainConfig.js`: Source of truth for all domain→portal mappings
- `DomainContext.js`: React context + useDomain() hook for app-wide access
- `DomainRouter` in App.js: Detects hostname → sets portal context → routes
- `?portal=` query param for testing in preview/staging environments
- Portal selector shows Direct Access domain URLs per app card
- Backend: `GET /api/portal/domain-config` returns portal config for hostname
- CORS updated to allow all registered domains
- Cookie domain strategy: `.aikarau.com` for subdomains, separate for `enzilink.com`

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
- iteration_204: 100% (12/12 BE, 6/6 FE - Domain Routing)
- iteration_203: 100% (15/15 BE, 7/7 FE - Meeting-to-Channel + Admin Approvals)
- iteration_202: 100% (19/19 BE, 24/24 FE features)

## Remaining Tasks
- **P1**: Full Bot Store/Marketplace (discover, publish, share bots)
- **P2**: Refactor LumiMessenger.jsx (~1388 lines) into smaller components
- **P2**: Voice/Video Call enhancements (recording, transcription)
- **P3**: Mobile-first optimization
- **P3**: Advanced ML for channel predictions

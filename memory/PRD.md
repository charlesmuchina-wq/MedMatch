# AI KARAU + ENZI - Product Requirements Document

## Original Problem Statement
Build a dual-platform communication suite: "AI KARAU" (webinar tool), "ENZI" (professional-grade AI messenger), and "MedMatch AI" (job-seeking toolkit). ENZI is the primary focus — a futuristic, AI-driven "Actionable Intelligence" hub with liquid glass aesthetics, bento grid layouts, and predictive behavior.

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + react-markdown
- Backend: FastAPI + MongoDB + emergentintegrations
- Real-time: WebSocket at /api/lumi/ws/{user_id}
- AI: GPT-4o via Emergent LLM Key (bots, writing, transcription, chapters, cover letters)
- Payments: Stripe via emergentintegrations (test mode)
- Push: Web Push (pywebpush + VAPID keys)
- Auth: Email/password, Google SSO, Microsoft SSO, Apple, GitHub (Demo), Passkeys/WebAuthn
- Desktop: Electron (Win/Mac/Linux)
- Mobile: Expo SDK 54 + React Native 0.81 (iOS/Android)
- Microsoft: Teams App + Outlook Add-in

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test: test@medmatch.io / TestPassword123!

## Test Results Summary
| Test | Scope | Result |
|------|-------|--------|
| iteration_215 | Quick Apply Bot + Predictive Channels | 100% (12 BE + all FE) |
| iteration_214 | Smart Apply initial | 100% BE, 95% FE (nav label) |
| iteration_213 | Passkeys/WebAuthn full flow | 100% (17 tests) |
| iteration_212 | ENZI logo + Platform Downloads | 100% (28 tests) |
| iteration_211 | Multi-platform deployment readiness | 100% (32 tests) |

## Complete Feature List (All Implemented)
1. Three-portal suite (AI KARAU, ENZI, MedMatch AI) with unified workspace
2. 18+ AI-powered bots (GPT-4o) with slash commands + autocomplete
3. Bot-to-Bot workflow chains with auto-triggers
4. Meeting-to-channel sync with admin approval
5. Domain-aware multi-subdomain routing
6. ML channel predictions (wired to ENZI sidebar)
7. Meeting replay: AI chapters + transcript search
8. Push notifications (VAPID configured)
9. Passkeys/WebAuthn (full frontend + backend flow)
10. Mobile bottom navigation
11. Stripe payments (4 tiers, live test mode)
12. AI Writing Assistant
13. End-to-end encryption, team analytics, channel templates, webhooks
14. Predictive zero-click navigation, behavioral modeling
15. Web PWA/TWA with share_target, protocol_handlers
16. Desktop (Electron) - Win/Mac/Linux with full suite branding
17. Mobile Android - APK/AAB via EAS Build
18. Mobile iOS - IPA via EAS Build, TestFlight ready
19. Microsoft Teams (3 static tabs, compose extensions)
20. Microsoft Outlook Add-in (meeting scheduling)
21. Platform Downloads Page (/downloads, public, 8 platforms)
22. ENZI brain-network neural logo (all components updated)
23. **Quick Apply Bot** (NEW) — AiApply-like feature:
    - AI-powered job matching with 24h freshness filter
    - Resume-based skill scoring per job
    - AI cover letter generation per matched job (GPT-4o)
    - Batch auto-apply with application tracking
    - Configurable preferences (roles, locations, exclude companies)
    - Run history tracking
    - ENZI bot marketplace integration (/quickapply slash command)
24. **Predictive Channel UI** (NEW) — ENZI sidebar wired to /api/lumi/behavior/predict-channels

## Key API Endpoints (Smart Apply)
- GET /api/smart-apply/config — User preferences
- PUT /api/smart-apply/config — Save preferences
- POST /api/smart-apply/run — Execute smart apply (job_title, location, max_jobs)
- GET /api/smart-apply/history — Run history

## Remaining Tasks
- **P3 - Resend email integration UI** (needs user API key)
- **P3 - Refactoring:** KarauSettingsPage (~862 lines), BotStoreModal
- **P3 - Advanced Bot Workflow UI** (trigger configuration from frontend)

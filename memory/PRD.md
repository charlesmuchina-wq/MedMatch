# AI KARAU + ENZI - Product Requirements Document

## Original Problem Statement
Build a dual-platform communication suite: "AI KARAU" (webinar tool), "ENZI" (professional-grade AI messenger), and "MedMatch AI" (job-seeking toolkit). ENZI is the primary focus -- a futuristic, AI-driven "Actionable Intelligence" hub with liquid glass aesthetics, bento grid layouts, and predictive behavior.

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
- CI/CD: GitHub Actions + Local runner (Phase 1 + Phase 3 gates)

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test: test@medmatch.io / TestPassword123!

## Test Results Summary (Updated March 2026)
| Test | Scope | Result |
|------|-------|--------|
| Phase 1 (iteration_216) | Functional Testing - Gate G1 | 59/59 PASS |
| Phase 2 (iteration_217) | Reliability Testing - Gate G2 | 31/31 PASS |
| Phase 3 (iteration_218) | Post-Reliability Regression - Gate G3 | 41/41 PASS |
| Phase 4 (iteration_219) | Deployment Readiness - Gate G4 | 54/54 PASS |
| Iteration 220 | CI/CD + Email Settings + Refactoring + Bot Triggers | 19/19 PASS |
| **Grand Total** | **5 iterations** | **204/204 PASS** |

## Complete Feature List (All Implemented)
1. Three-portal suite (AI KARAU, ENZI, MedMatch AI) with unified workspace
2. 18+ AI-powered bots (GPT-4o) with slash commands + autocomplete
3. Bot-to-Bot workflow chains with 5 triggers (manual, after meeting, on message, scheduled, on channel join)
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
23. Quick Apply Bot - AiApply-like feature with AI job matching
24. Predictive Channel UI - ENZI sidebar wired to behavioral predictions
25. CI/CD Pipeline - GitHub Actions + local runner (Phase 1 + Phase 3 gates)
26. Resend Email Settings UI - Admin page with API key management and test email
27. Refactored KarauSettingsPage (862 -> 120 lines + 7 sub-components)
28. Refactored BotStoreModal (535 -> 200 lines + 3 sub-components)
29. Advanced Bot Workflow UI - 5 trigger types with configurable values

## Key API Endpoints
- Auth: /api/auth/login, /api/auth/register, /api/auth/passkey/*
- Jobs: /api/jobs/search, /api/jobs/apply
- Smart Apply: /api/smart-apply/config, /api/smart-apply/run, /api/smart-apply/history
- AI Features: /api/cover-letter/generate, /api/salary/insights, /api/interview-prep, /api/assistant
- ENZI: /api/lumi/channels, /api/lumi/dm, /api/lumi/bots/catalog
- KARAU: /api/karau-meet/meetings, /api/advanced/webinars
- Admin: /api/admin-audit/logs, /api/privacy
- Email Settings: /api/admin/email-settings (GET/PUT), /api/admin/email-settings/test (POST)
- Behavioral: /api/lumi/behavior/predict-channels

## Deployment Readiness
- Gates G1-G3: PASSED (automated testing)
- Gate G4: Prerequisites met (configs validated, store submissions pending)
- Gate G5: Prerequisites met (no hardcoded secrets, CISO sign-off pending)
- Full results: /app/docs/TESTING_STRATEGY_RESULTS.md

## Remaining Tasks
- **External:** App store submissions, Azure AD registration, CISO sign-off
- **Enhancement:** Production monitoring & CRS dashboard, Chrome Extension

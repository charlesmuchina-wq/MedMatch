# AI KARAU + ENZI - Product Requirements Document

## Original Problem Statement
Build a dual-platform communication suite: "AI KARAU" (webinar tool), "ENZI" (professional-grade AI messenger), and "MedMatch AI" (job-seeking toolkit). ENZI is the primary focus — a futuristic, AI-driven "Actionable Intelligence" hub with liquid glass aesthetics, bento grid layouts, and predictive behavior.

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + react-markdown
- Backend: FastAPI + MongoDB + emergentintegrations
- Real-time: WebSocket at /api/lumi/ws/{user_id}
- AI: GPT-4o via Emergent LLM Key (bots, writing, transcription, chapters)
- Payments: Stripe via emergentintegrations (test mode)
- Push: Web Push (pywebpush + VAPID keys)
- Auth: Email/password, Google SSO, Microsoft SSO, Apple, GitHub (Demo), Passkeys/WebAuthn (full flow)
- Desktop: Electron (Win/Mac/Linux)
- Mobile: Expo SDK 54 + React Native 0.81 (iOS/Android)
- Microsoft: Teams App + Outlook Add-in

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test: test@medmatch.io / TestPassword123!

## Test Results Summary
| Test | Scope | Result |
|------|-------|--------|
| iteration_213 | Passkeys/WebAuthn full flow | 100% (7 BE + 10 FE) |
| iteration_212 | ENZI logo + Platform Downloads | 100% (28 FE tests) |
| iteration_211 | Multi-platform deployment readiness | 100% (32 tests) |

## Complete Feature List (All Implemented)
1. Three-portal suite (AI KARAU, ENZI, MedMatch AI) with unified workspace
2. 18 AI-powered bots (GPT-4o) with slash commands + autocomplete
3. Bot-to-Bot workflow chains with auto-triggers
4. Meeting-to-channel sync with admin approval
5. Domain-aware multi-subdomain routing
6. ML channel predictions
7. Meeting replay: AI chapters + transcript search
8. Push notifications (VAPID configured)
9. Mobile bottom navigation
10. Stripe payments (4 tiers, live test mode)
11. AI Writing Assistant
12. End-to-end encryption, team analytics, channel templates, webhooks
13. Predictive zero-click navigation, behavioral modeling
14. Web PWA/TWA with share_target, protocol_handlers
15. Desktop (Electron) - Win/Mac/Linux
16. Mobile Android (APK/AAB via EAS Build)
17. Mobile iOS (IPA via EAS Build, TestFlight ready)
18. Microsoft Teams (3 static tabs, compose extensions)
19. Microsoft Outlook Add-in (meeting scheduling)
20. Platform Downloads Page (/downloads, public)
21. ENZI brain-network neural logo
22. **Passkeys/WebAuthn - Full Frontend Flow** (NEW)
    - PasskeyManager in ENZI profile modal (list, add, delete)
    - Sign in with passkey on all login pages (ENZI, MedMatch, KARAU)
    - Backend: GET /api/auth/passkeys, DELETE /api/auth/passkeys/{id}

## Remaining Tasks
- **P2 - Predictive Channel UI:** Backend endpoint ready, need frontend sidebar integration
- **P3 - Resend email integration UI** (needs user API key)
- **P3 - Refactoring:** KarauSettingsPage (~862 lines), BotStoreModal
- **P3 - Advanced Bot Workflow UI** (trigger configuration from frontend)

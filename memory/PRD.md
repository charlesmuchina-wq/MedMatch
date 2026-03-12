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
| iteration_212 | ENZI logo + Platform Downloads page | 100% (28/28 FE tests) |
| iteration_211 | Multi-platform deployment readiness | 100% (32/32 tests) |
| iteration_210 | All remaining features | 100% (11/11 BE, all FE) |

## Complete Feature List (All Implemented)
1. Three-portal suite (AI KARAU, ENZI, MedMatch AI) with unified workspace
2. 18 AI-powered bots (GPT-4o) with slash commands + autocomplete
3. Bot-to-Bot workflow chains with auto-triggers (on_meeting_end, on_new_message)
4. Meeting-to-channel sync with admin approval
5. Domain-aware multi-subdomain routing
6. ML channel predictions (/api/lumi/behavior/predict-channels)
7. Meeting replay: AI chapters + transcript search
8. Push notifications (VAPID configured)
9. Passkeys/WebAuthn (backend ready, RP configured)
10. Mobile bottom navigation (Channels, DMs, Search, AI, Me)
11. Stripe payments (4 tiers, live test mode)
12. AI Writing Assistant (refine, suggest, translate, voice, templates)
13. End-to-end encryption, team analytics, channel templates, webhooks
14. Predictive zero-click navigation, behavioral modeling

## Multi-Platform Deployment (All Configured)
15. **Web PWA/TWA** - Enhanced manifest with share_target, protocol_handlers, related_applications
16. **Desktop (Electron)** - Windows (NSIS+Portable), macOS (DMG+ZIP, x64/arm64), Linux (AppImage)
17. **Mobile Android** - APK/AAB via EAS Build, Play Store ready
18. **Mobile iOS** - IPA via EAS Build, TestFlight/App Store ready
19. **Microsoft Teams** - 3 static tabs (ENZI, KARAU, MedMatch), compose extensions
20. **Microsoft Outlook** - Add-in with meeting scheduling from calendar events and emails
21. **Platform Downloads Page** - Public /downloads page with all 8 platforms, install instructions
22. **ENZI Logo Updated** - New brain-network neural icon across all components

## Remaining Tasks
- **P1 - Passkeys/WebAuthn Frontend Flow:** Backend ready, need frontend UI for registration/management
- **P2 - Predictive Channel UI:** Backend endpoint ready, need frontend sidebar integration
- **P3 - Resend email integration UI** (needs user API key)
- **P3 - Refactoring:** KarauSettingsPage (~862 lines), BotStoreModal
- **P3 - Advanced Bot Workflow UI** (trigger configuration from frontend)

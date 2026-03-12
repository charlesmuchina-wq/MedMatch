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

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test: test@medmatch.io / TestPassword123!

## Test Results Summary
| Test | Scope | Result |
|------|-------|--------|
| iteration_210 | All remaining features | 100% (11/11 BE, all FE) |
| iteration_209 | Phases 2-4 initial | 100% |
| iteration_208 | Phase 1 refactoring | 100% |
| iteration_207 | P1 AI Bot Marketplace | 100% |
| iteration_206 | P0 Messenger verification | 100% |

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

## Remaining (Low Priority)
- Resend email integration (needs user API key)
- Real-time co-editing with Y.js/Automerge
- Further refactoring: KarauSettingsPage (862 lines), BotStoreModal (534 lines)

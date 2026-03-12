# AI KARAU + ENZI - Product Requirements Document

## Original Problem Statement
Build a dual-platform communication suite: "AI KARAU" (webinar tool) and "ENZI" (professional-grade messenger), plus "MedMatch AI" (job-seeking toolkit). ENZI is the primary focus — a futuristic, AI-driven "Actionable Intelligence" hub with liquid glass aesthetics, bento grid layouts, and predictive behavior.

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + react-markdown + react-syntax-highlighter
- Backend: FastAPI + MongoDB + emergentintegrations + msal + resend
- Real-time: WebSocket at /api/lumi/ws/{user_id}
- AI: GPT-4o via Emergent LLM Key (bots, writing assistant, transcription, notes)
- Payments: Stripe via emergentintegrations (LIVE test mode)
- Push: Web Push (pywebpush + VAPID keys)
- Auth: Email/password, Google SSO, Microsoft SSO, Apple, GitHub (Demo), Passkeys

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test: test@medmatch.io / TestPassword123!

## Test Results Summary
| Test | Scope | Result |
|------|-------|--------|
| iteration_209 | Phases 2-4 (Push, Chains, KARAU) | 100% |
| iteration_208 | Phase 1 (Refactoring) | 100% |
| iteration_207 | P1 (AI Bot Marketplace) | 100% |
| iteration_206 | P0 (Messenger Verification) | 100% |
| iteration_205 | Bot Marketplace UI | 100% |

## Remaining Tasks
- **P2**: Voice/Video recording AI transcription UI improvements
- **P3**: Real-time co-editing in writing assistant
- **P3**: Mobile-first UX optimization pass (responsive audit)
- **P3**: Meeting Replay AI chapters + searchable transcript
- **P3**: Advanced ML for channel predictions

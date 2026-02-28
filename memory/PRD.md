# MedMatch-AI KARAU Platform - Product Requirements Document

## Original Problem Statement
Build "MedMatch-AI KARAU" - a dual-purpose platform featuring:
1. **AI KARAU** - Premium video meeting portal with AI-powered features
2. **MedMatch Job Toolkit** - AI-powered life sciences talent ecosystem

## Core Architecture
- **Frontend**: React + Tailwind CSS + Shadcn UI + react-i18next (52 locales)
- **Backend**: FastAPI + MongoDB
- **AI**: Emergent LLM Key for assistant, summaries, translation
- **Theme**: Purple/violet/emerald karau palette (karau-bg, karau-card, karau-accent, karau-emerald)

## What's Implemented

### AI KARAU Portal
- Single-page horizontal dashboard with real-time stats, activity feed, upcoming meetings, trending topics
- Meeting creation with scheduling + countdown timers
- Floating KARAU AI Avatar (React Portal) with chat panel
- Collapsible sections (highlights, recent meetings)
- Full meeting room: video controls, screen share, breakout rooms, polls, whiteboard, live captions, virtual backgrounds, recording with consent
- Settings: Accessibility, Calendar (MS/Google/Apple), Security, SSO/SAML, Compliance (GDPR/HIPAA), CRM Webhooks
- Guest join with OTP email verification + age confirmation
- Industry templates for meetings
- Dashboard auto-refresh every 30s with visual spinner indicator

### MedMatch Job Toolkit
- Resume parser/builder, AI job matching, semantic search with relevance scoring + filters
- Recruiter network, salary insights, interview prep, company reviews
- Admin panel, analytics, trust score system

### Internationalization
- 52 locale files with 314+ karauMeet keys, 20+ candidateSearch keys
- react-i18next with namespace-based translation
- All KARAU portal pages fully internationalized

### Theme (Feb 2026)
- Replaced all Teams-blue (turquoise/slate-800/900) with karau purple/green palette
- Login, Dashboard, Settings, Recordings, Guest Join, Meeting Room, Video Controls, all meeting panels updated

## P0/P1/P2 Prioritized Backlog

### P2 - Future
- Full noise cancellation with rnnoise-wasm library
- Payment gateway live keys (Stripe/PayPal) - blocked on user input
- Real-time WebRTC peer connections
- Native AI translations for all 51 non-English locales (currently using English fallback)

## User Personas
- **Meeting Host**: Creates/schedules meetings, manages participants, uses AI assistant
- **Guest**: Joins via link with email verification
- **Admin**: Enterprise SSO, compliance, organization management
- **Recruiter**: Uses MedMatch toolkit for talent search

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test User: test@medmatch.io / TestPassword123!

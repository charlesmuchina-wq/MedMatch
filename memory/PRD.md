# MedMatch-AI KARAU Platform - Product Requirements Document

## Original Problem Statement
Build "MedMatch-AI KARAU" - a dual-purpose platform featuring:
1. **AI KARAU** - Premium video meeting portal with AI-powered features
2. **MedMatch Job Toolkit** - AI-powered life sciences talent ecosystem

## Core Architecture
- **Frontend**: React + Tailwind CSS + Shadcn UI + react-i18next (52 locales)
- **Backend**: FastAPI + MongoDB + Motor (async)
- **AI**: Emergent LLM Key for assistant, summaries, translation
- **Theme**: Purple/violet/emerald karau palette
- **WebRTC**: Full signaling server + peer connection management

## What's Implemented

### AI KARAU Portal
- **Dashboard**: Single-page horizontal layout with:
  - Real-time stats, activity feed, upcoming meetings with countdowns, trending topics
  - Meeting Effectiveness Score (circular gauge, engagement level, tip)
  - Gamification (XP, levels, badges, streaks, rank titles)
  - Collapsible Team Leaderboard (top 50 users, XP ranking, streak indicators)
  - Quick Analytics (on-time rate, AI notes usage, action items progress bars)
  - Collapsible sections, floating KARAU AI Avatar
  - Auto-refresh every 30s with visual spinner

- **Meeting Room**: Full-featured video conferencing with:
  - WebRTC peer connections (signaling server + STUN/TURN)
  - Dual-engine noise cancellation (RNNoise WASM + Web Audio API fallback)
  - Screen share, breakout rooms, polls, whiteboard, live captions
  - Virtual backgrounds, recording with consent
  - AI assistant panel
  - **In-Meeting File Sharing** (P2P via WebSocket, 10MB limit, link sharing)

- **Webinar Mode** (WebEx-style, 1000+ attendees):
  - Webinar management page with create/list/start/end
  - Public registration page (no login required)
  - Host controls: mute all, disable chat, manage audio
  - Q&A system: submit, answer, upvote, dismiss questions
  - Webinar analytics: registrations, attendance rate, engagement score

- **Settings**: 6 tabs (Accessibility, Calendar, Security, SSO/SAML, Compliance, Webhooks)
- **Recordings**: Local recording management with stats
- **Guest Join**: 3-step OTP verification (Details → Verify → Confirm)

### MedMatch Job Toolkit
- Semantic search with relevance scoring + filtering (Excellent/Good/Fair/Low)
- Resume parser/builder, AI job matching, recruiter network
- Admin panel, analytics, trust score system

### Internationalization (52 Languages)
- 344+ i18n keys (karauMeet, candidateSearch, karau sections)
- AI-translated via GPT-4o-mini to all 51 non-English locales
- 50/50 locales at 80%+ translation coverage

### Theme (Feb 2026)
- Complete removal of Teams-blue palette (turquoise/slate)
- karau palette: purple (#6c3ce0), emerald (#10b981), dark bg (#0c0f1a)

## API Endpoints
- `GET /api/karau/analytics/effectiveness` - Meeting effectiveness score
- `GET /api/karau/analytics/gamification` - XP, levels, badges, streaks
- `GET /api/karau/analytics/participation` - Participation breakdown
- `GET /api/karau/analytics/leaderboard` - Team leaderboard (top 50)
- `GET /api/karau/webinar/list` - List user's webinars
- `POST /api/karau/webinar/create` - Create new webinar
- `GET /api/karau/webinar/{id}` - Get webinar details (public)
- `POST /api/karau/webinar/{id}/register` - Register for webinar (public)
- `POST /api/karau/webinar/{id}/start` - Start webinar (host only)
- `POST /api/karau/webinar/{id}/end` - End webinar (host only)
- `POST /api/karau/webinar/{id}/qa/ask` - Ask Q&A question
- `POST /api/karau/webinar/{id}/qa/{qid}/answer` - Answer question
- `GET /api/karau/webinar/{id}/qa` - Get all questions
- `GET /api/karau/webinar/{id}/analytics` - Webinar analytics
- `GET /api/karau/stats` - Dashboard statistics
- `GET /api/karau/activity` - Live activity feed
- `GET /api/karau/upcoming-meetings` - Scheduled meetings
- `GET /api/karau/trending-topics` - Trending topics from notes
- `POST /api/karau/ai-assistant` - AI chat assistant
- `WS /api/karau-meet/ws/{meeting_id}` - WebRTC signaling

## P0/P1/P2 Backlog

### P1 - Upcoming
- Refinement of rnnoise-wasm noise cancellation
- i18n propagation for new webinar/file-sharing keys to all 51 languages
- UI polish & UX refinements

### P2 - Future
- Payment gateway live keys (Stripe/PayPal)
- Meeting recording cloud storage
- Enhanced webinar analytics dashboard

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test User: test@medmatch.io / TestPassword123!

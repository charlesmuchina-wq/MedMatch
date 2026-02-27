# MedMatch-AI KARAU - Product Requirements Document

## Original Problem Statement
Build "MedMatch," an AI-powered Life Sciences & Engineering Talent Ecosystem, combined with "AI KARAU" - an enterprise-grade video meeting portal.

## Platforms
1. **AI KARAU** - Enterprise video conferencing with AI intelligence
2. **MedMatch Job Toolkit** - Life sciences talent recruitment platform

## Core Architecture
- Frontend: React + Shadcn UI + TailwindCSS
- Backend: FastAPI + MongoDB
- Real-time: WebRTC + WebSocket
- AI: Emergent LLM Integration (OpenAI via emergent key)

## Gap Assessment (Feb 27, 2026)
Full report at: /app/docs/GAP_ASSESSMENT.md
- AI KARAU scored 62/100 -> ~78/100 (after Phase 1+2)
- MedMatch scored 58/100 -> ~75/100 (after Phase 1+2)

---

## What's Been Implemented

### Phase 1 - Critical Gap Closures (Feb 27, 2026)
- [x] Live captions via Web Speech API
- [x] AI meeting summaries with action items (LLM)
- [x] In-meeting emoji reactions (8 types, floating animation)
- [x] Live polls & Q&A (create, vote, close, results)
- [x] AI candidate scoring & ranking (LLM)
- [x] AI job description generator
- [x] Interview scorecards with averaging
- [x] Hiring metrics dashboard (time-to-hire, cost-per-hire, pipeline, sources)

### Phase 2 - High Gap Closures (Feb 27, 2026)
- [x] DEI analytics dashboard (gender distribution, geographic diversity, pipeline equity, goals)
- [x] Talent CRM (talent pools, candidate notes, nurture campaigns)
- [x] Meeting whiteboard (canvas drawing, colors, sizes, undo, clear, save)
- [x] AI noise cancellation hook (Web Audio API: high-pass, low-pass, notch, compressor)
- [x] KARAU design overhaul (new karau color palette: #1a1b2e bg, #232436 cards, glass effects, dual coding buttons, 60-30-10 color rule)

### Previously Implemented (Before Gap Assessment)
- Pre-meeting lobby with guest 2FA + age gate
- WebRTC video/audio with screen sharing
- Host moderation controls (mute, mute all, pass mic)
- Active speaker highlighting
- Breakout rooms with AI auto-assignment
- Enterprise admin panel (licensing, branding, conference rooms)
- Employee directory (CSV + LDAP sync)
- Calendar integration (Microsoft, Google, iOS)
- SSO/SAML integration
- 50+ language UI translation
- Skin tone protection
- Job search, save, apply workflow
- Resume builder and profiles
- Interview prep (QA, video, voice coaching)
- ML success predictor, blind screening, ATS, salary insights
- Company profiles + messaging + Dragon AI

---

## Remaining Backlog

### P1 - High Priority
- [ ] Participant scaling (SFU/MCU architecture for 1000+)
- [ ] Full E2E encryption implementation
- [ ] One-click apply for job seekers
- [ ] Multi-channel outreach (email, SMS, InMail)
- [ ] Team collaboration on candidates

### P2 - Medium Priority
- [ ] Webinar mode (view-only attendees)
- [ ] Real-time language translation
- [ ] Offer management & templates
- [ ] Custom report builder
- [ ] CRM/Salesforce integration

### P3 - Long-term
- [ ] Native mobile apps (iOS/Android)
- [ ] Semantic matching engine (vector embeddings)
- [ ] HRIS bidirectional sync
- [ ] Background check integrations
- [ ] HIPAA/SOC2 compliance certification

## Key API Endpoints (New)
- `POST /api/karau-meet/ai/summarize` - AI meeting summary
- `GET/POST /api/karau-meet/ai/polls/*` - Meeting polls CRUD
- `POST /api/ai-talent/score-candidate` - AI candidate scoring
- `POST /api/ai-talent/generate-job-description` - JD generation
- `GET /api/ai-talent/hiring-metrics` - Hiring analytics
- `POST/GET /api/ai-talent/scorecards/*` - Interview scorecards
- `GET /api/dei-analytics/metrics` - DEI metrics
- `GET /api/dei-analytics/goals` - DEI goals
- `GET/POST /api/talent-crm/pools` - Talent pool CRUD
- `GET/POST /api/talent-crm/campaigns` - Nurture campaigns
- `GET/POST /api/talent-crm/notes/*` - Candidate notes

## Test Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test User: test@medmatch.io / TestPassword123!

## New Frontend Routes
- `/ai-scoring` - AI Candidate Scoring
- `/jd-generator` - AI Job Description Generator
- `/hiring-metrics` - Hiring Metrics Dashboard
- `/dei-analytics` - DEI Analytics
- `/talent-crm` - Talent CRM (pools, campaigns, notes)

## Design System (KARAU)
- Background: #1a1b2e (karau-bg)
- Cards/Panels: #232436 (karau-card)
- Surfaces: #2d2e42 (karau-surface)
- Borders: #2e303e (karau-border)
- Accent: #20b2aa / #40e0d0 (teal/cyan)
- Danger: #ef4444 (red)
- Glass effects: backdrop-blur-xl on headers/control bars
- 60-30-10 rule: 60% bg, 30% panels, 10% accents

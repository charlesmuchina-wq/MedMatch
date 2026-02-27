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

## What's Been Implemented

### AI KARAU Portal (Feature-Complete + Gap Assessment Phase 1)
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
- **NEW (Feb 27, 2026):** Live captions (Web Speech API)
- **NEW (Feb 27, 2026):** AI meeting summaries with action items (LLM-powered)
- **NEW (Feb 27, 2026):** In-meeting emoji reactions (floating animations)
- **NEW (Feb 27, 2026):** Live polls & Q&A system (create, vote, close)

### MedMatch Job Toolkit (Feature-Complete + Gap Assessment Phase 1)
- Job search, save, apply workflow
- Resume builder and profiles
- Interview prep (QA, video, voice coaching)
- ML success predictor
- Blind screening dashboard
- ATS management
- Recruiter dashboard
- Company profiles + messaging
- Skill assessments + credentials (ORCID, PSV)
- Salary insights + analytics
- Dragon AI automator
- **NEW (Feb 27, 2026):** AI Candidate Scoring (LLM-powered skill matching)
- **NEW (Feb 27, 2026):** AI Job Description Generator
- **NEW (Feb 27, 2026):** Interview Scorecards
- **NEW (Feb 27, 2026):** Hiring Metrics Dashboard (time-to-hire, cost-per-hire, source effectiveness)

## Gap Assessment (Feb 27, 2026)
Full report at: /app/docs/GAP_ASSESSMENT.md

### Readiness Scores
- AI KARAU: 62/100 -> ~70/100 (after Phase 1 implementations)
- MedMatch: 58/100 -> ~67/100 (after Phase 1 implementations)

### Phase 1 - COMPLETED (Critical Quick Wins)
- [x] Real-time transcription & captions
- [x] AI meeting summaries with action items
- [x] In-meeting reactions
- [x] Live polls & Q&A
- [x] AI candidate scoring & ranking
- [x] AI job description generator
- [x] Interview scorecards
- [x] Hiring metrics dashboard

### Phase 2 - Remaining Critical/High Gaps (Backlog)
**AI KARAU:**
- [ ] AI noise cancellation (Web Audio API + ML model)
- [ ] Whiteboard / collaborative canvas
- [ ] Participant scaling (SFU/MCU for 1000+)
- [ ] Full E2E encryption
- [ ] HIPAA/SOC2 compliance certification

**MedMatch:**
- [ ] Talent CRM (nurture campaigns, relationship management)
- [ ] One-click apply
- [ ] DEI/diversity analytics dashboard
- [ ] Multi-channel outreach
- [ ] Team collaboration on candidates

### Phase 3 - Long-term (Future)
- Native mobile apps
- Webinar mode
- Real-time language translation
- Semantic matching engine (vector embeddings)
- HRIS bidirectional sync
- Background check integrations

## Key API Endpoints (New)
- `POST /api/karau-meet/ai/summarize` - Generate meeting summary
- `GET/POST /api/karau-meet/ai/polls/*` - Polls CRUD
- `POST /api/ai-talent/score-candidate` - AI candidate scoring
- `POST /api/ai-talent/generate-job-description` - JD generation
- `GET /api/ai-talent/hiring-metrics` - Hiring analytics
- `POST/GET /api/ai-talent/scorecards/*` - Interview scorecards

## Test Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test User: test@medmatch.io / TestPassword123!

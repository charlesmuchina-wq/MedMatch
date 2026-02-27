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

---

## Implementation Status

### Phase 1 - Critical Gap Closures (DONE)
- [x] Live captions via Web Speech API
- [x] AI meeting summaries with action items
- [x] In-meeting emoji reactions
- [x] Live polls & Q&A
- [x] AI candidate scoring
- [x] AI job description generator
- [x] Interview scorecards
- [x] Hiring metrics dashboard

### Phase 2 - High Gap Closures (DONE)
- [x] DEI analytics dashboard
- [x] Talent CRM (pools, notes, campaigns)
- [x] Meeting whiteboard
- [x] AI noise cancellation hook
- [x] KARAU design overhaul (karau color palette)

### Phase 3 - P1 Features (DONE)
- [x] One-click apply (saved profile instant application)
- [x] Team collaboration (shared candidate reviews, comments, reactions)
- [x] Multi-channel outreach (email, SMS, InMail)

### Phase 4 - P2 Features (DONE)
- [x] Webinar mode (create, register, manage large events)
- [x] SFU scaling infrastructure (config, simulcast, adaptive bitrate)
- [x] E2E encryption (key exchange, AES-256-GCM, ECDH-P256)
- [x] Real-time language translation (16 languages via LLM)
- [x] Offer management with AI letter generation
- [x] Custom report builder (hiring funnel, DEI, source, time series)

### Phase 5 - P3 Features (DONE)
- [x] Semantic matching engine (AI-powered deep matching)
- [x] HRIS integration (Workday, BambooHR, ADP, SAP)
- [x] Background check system (identity, criminal, education, employment)
- [x] Compliance dashboard (SOC 2, HIPAA, GDPR, ISO 27001, CCPA)

### Previously Implemented (Pre-Gap Assessment)
- Pre-meeting lobby, guest 2FA + age gate
- WebRTC video/audio, screen sharing
- Host moderation, active speaker highlighting
- Breakout rooms with AI, enterprise admin panel
- Employee directory, calendar/SSO integration
- 50+ language UI, skin tone protection
- Job search/apply, resume builder, interview prep
- ML predictor, blind screening, ATS, salary insights

---

## API Endpoints Summary

### Meeting Intelligence
- `POST /api/karau-meet/ai/summarize` - AI meeting summary
- `GET/POST /api/karau-meet/ai/polls/*` - Meeting polls
- `GET /api/meeting-infra/sfu/config` - SFU configuration
- `POST /api/meeting-infra/e2ee/keys` - E2E key exchange
- `POST /api/meeting-infra/translate` - Real-time translation
- `GET /api/meeting-infra/translate/languages` - Supported languages

### Talent Intelligence
- `POST /api/ai-talent/score-candidate` - AI scoring
- `POST /api/ai-talent/generate-job-description` - JD generation
- `GET /api/ai-talent/hiring-metrics` - Hiring analytics
- `POST/GET /api/ai-talent/scorecards/*` - Interview scorecards

### Talent Tools
- `POST /api/talent-tools/one-click-apply` - Quick apply
- `POST/GET /api/talent-tools/collaborate/*` - Team collaboration
- `POST/GET /api/talent-tools/outreach/*` - Multi-channel outreach

### Advanced Features
- `POST/GET /api/advanced/webinars` - Webinar management
- `POST/GET /api/advanced/offers` - Offer management
- `POST /api/advanced/offers/{id}/generate-letter` - AI offer letter
- `POST/GET /api/advanced/reports` - Custom reports

### Platform
- `POST /api/platform/semantic-match` - AI semantic search
- `POST /api/platform/hris/*` - HRIS integration
- `POST/GET /api/platform/background-checks` - BG checks
- `GET /api/platform/compliance/status` - Compliance dashboard
- `GET/POST /api/dei-analytics/*` - DEI metrics
- `GET/POST /api/talent-crm/*` - Talent CRM

## Frontend Routes
- `/ai-scoring`, `/jd-generator`, `/hiring-metrics`, `/dei-analytics`
- `/talent-crm`, `/team-outreach`, `/webinars`
- `/offer-management`, `/report-builder`
- `/platform-settings`, `/semantic-search`

## MOCKED Integrations
- SFU relay servers (config only, no live servers)
- HRIS sync (returns success, no external connection)
- Background checks (creates records, no Checkr/Sterling)
- Payment gateways (need live Stripe/PayPal keys)

## Test Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test User: test@medmatch.io / TestPassword123!

## Design System (KARAU)
- Background: #1a1b2e | Cards: #232436 | Surfaces: #2d2e42
- Borders: #2e303e | Accent: #20b2aa/#40e0d0 | Danger: #ef4444
- Glass effects, 60-30-10 rule, dual-coded buttons

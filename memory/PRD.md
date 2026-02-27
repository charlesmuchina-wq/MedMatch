# MedMatch-AI KARAU - Product Requirements Document

## Original Problem Statement
Build "MedMatch," an AI-powered Life Sciences & Engineering Talent Ecosystem, combined with "AI KARAU" - an enterprise-grade video meeting portal. Perform competitive gap assessment and implement all identified feature gaps.

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

### Phase 1 - Core Features (DONE)
- [x] Pre-meeting lobby, guest 2FA + age gate
- [x] WebRTC video/audio, screen sharing
- [x] Host moderation, active speaker highlighting
- [x] Breakout rooms, enterprise admin panel
- [x] Job search/apply, resume builder, interview prep
- [x] ML predictor, blind screening, ATS, salary insights

### Phase 2 - AI Intelligence (DONE)
- [x] Live captions via Web Speech API
- [x] AI meeting summaries with action items
- [x] AI candidate scoring & JD generator
- [x] Interview scorecards & hiring metrics
- [x] Live polls & Q&A with persistence
- [x] In-meeting emoji reactions

### Phase 3 - Enterprise Suite (DONE)
- [x] DEI analytics dashboard
- [x] Meeting whiteboard with cloud save/load persistence
- [x] One-click apply, team collaboration, multi-channel outreach
- [x] Webinar mode, SFU scaling, E2E encryption
- [x] Real-time language translation (16 languages)

### Phase 4 - P0 Feature Build-Out (DONE - Feb 27, 2026)
- [x] **Talent CRM**: Contact CRUD, pipeline bar (8 stages), interaction timeline, pools, campaigns, search/filter
- [x] **Report Builder**: 5 report types with visual charts (bar, funnel, time series), stat cards, export
- [x] **Offer Management**: Status workflow (8 states), approval timeline, AI offer letter generation

### Phase 5 - P1 + P2 Features (DONE - Feb 27, 2026)
- [x] **Noise Cancellation**: Web Audio API hook with noise gate + bandpass filter for voice isolation
- [x] **Whiteboard Persistence**: Save/load canvas snapshots to MongoDB (one snapshot per meeting)
- [x] **Platform Settings Enhanced**:
  - Compliance Dashboard: Stat cards, 5 certifications with progress, data handling section
  - HRIS Integration: Config dialog (provider/URL/key/direction/fields), sync history
  - Background Checks: Initiation form, expandable results, multi-provider support

### Previously Complete
- Semantic matching engine, HRIS API routes, BG check API routes, Compliance status API
- 50+ language UI, skill assessments, employer reviews
- Calendar/SSO integration, employee directory

---

## Key API Endpoints

### Talent CRM
- `GET/POST /api/talent-crm/contacts` | `PUT/DELETE /api/talent-crm/contacts/{id}`
- `PUT /api/talent-crm/contacts/{id}/stage` | `GET /api/talent-crm/pipeline`
- `POST/GET /api/talent-crm/interactions` | `GET/POST/DELETE /api/talent-crm/pools`

### Offers & Reports
- `GET/POST /api/advanced/offers` | `PUT /api/advanced/offers/{id}/status`
- `POST /api/advanced/offers/{id}/generate-letter` (AI)
- `GET/POST/DELETE /api/advanced/reports` (5 types with visual data)

### Meeting Intelligence
- `POST /api/karau-meet/ai/summarize` | `POST/GET /api/karau-meet/ai/polls/*`
- `POST /api/karau-meet/ai/whiteboard/save` | `GET /api/karau-meet/ai/whiteboard/{id}`

### Platform
- `POST /api/platform/hris/configure` | `POST /api/platform/hris/sync`
- `POST/GET /api/platform/background-checks`
- `GET /api/platform/compliance/status`

## MOCKED Integrations
- HRIS sync (no external Workday/BambooHR connection)
- Background checks (no Checkr/Sterling API)
- Compliance status (static data)
- Payment gateways (need live Stripe/PayPal keys)
- SSO/LDAP/Calendar (need credentials)

## Test Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test User: test@medmatch.io / TestPassword123!

## Design System
- Background: #1a1b2e | Cards: #232436 | Accent: #20b2aa/#40e0d0
- Glass effects, 60-30-10 rule, dual-coded buttons

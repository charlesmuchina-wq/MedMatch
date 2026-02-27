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
- [x] WebRTC video/audio, screen sharing, host moderation
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
- [x] Webinar mode, SFU scaling, E2E encryption
- [x] Real-time language translation (16 languages)

### Phase 4 - P0 Feature Build-Out (DONE - Feb 27, 2026)
- [x] **Talent CRM**: Contact CRUD, pipeline bar (8 stages), interaction timeline, pools, campaigns
- [x] **Report Builder**: 5 report types with visual charts (bar, funnel, time series), stat cards, export
- [x] **Offer Management**: Status workflow (8 states), approval timeline, AI offer letter generation

### Phase 5 - P1 + P2 Features (DONE - Feb 27, 2026)
- [x] **Noise Cancellation**: Web Audio API hook with noise gate + bandpass filter
- [x] **Whiteboard Persistence**: Canvas snapshot save/load to MongoDB
- [x] **Platform Settings Enhanced**: Compliance dashboard, HRIS config, Background Checks

### Phase 6 - P0 Remaining + Kanban (DONE - Feb 27, 2026)
- [x] **One-Click Apply**: Quick-apply button in job dialog using saved profile, success/error/already-applied states
- [x] **Team Collaboration**: Candidate discussion threads, comments with reactions, CRM contact integration
- [x] **Multi-Channel Outreach**: Email/SMS/InMail compose with recipient picker, template system (create/use), outreach history with delivery tracking
- [x] **Kanban Pipeline View**: 7-column drag-and-drop board for CRM pipeline stages, view toggle (list/kanban), HTML5 DnD API with real-time stage updates

---

## Key Frontend Routes
- `/talent-crm` - CRM with pipeline, contacts, pools, campaigns, Kanban view
- `/report-builder` - Visual report builder with charts
- `/offer-management` - Offer workflow management
- `/team-outreach` - Team collaboration + multi-channel outreach + templates
- `/platform-settings` - Compliance, HRIS, Background Checks
- `/ai-scoring`, `/jd-generator`, `/hiring-metrics`, `/dei-analytics`
- `/skill-assessments`, `/webinars`, `/semantic-search`

## Key API Endpoints
### Talent CRM
- `GET/POST /api/talent-crm/contacts` | `PUT/DELETE /api/talent-crm/contacts/{id}`
- `PUT /api/talent-crm/contacts/{id}/stage` | `GET /api/talent-crm/pipeline`

### Offers & Reports
- `GET/POST /api/advanced/offers` | `PUT /api/advanced/offers/{id}/status`
- `POST /api/advanced/offers/{id}/generate-letter` (AI)
- `GET/POST/DELETE /api/advanced/reports`

### Team & Outreach
- `POST /api/talent-tools/one-click-apply`
- `POST/GET /api/talent-tools/collaborate/comment(s)`
- `POST /api/talent-tools/outreach/send` | `GET /api/talent-tools/outreach/history`
- `POST/GET /api/talent-tools/outreach/templates`

### Platform
- `POST /api/platform/hris/configure` | `POST /api/platform/hris/sync`
- `POST/GET /api/platform/background-checks`
- `GET /api/platform/compliance/status`

## MOCKED Integrations
- Outreach send (DB records, no actual email/SMS)
- HRIS sync (no external Workday/BambooHR)
- Background checks (no Checkr/Sterling)
- Payment gateways (need Stripe/PayPal keys)

## Test Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test User: test@medmatch.io / TestPassword123!

## Design System
- Background: #1a1b2e | Cards: #232436 | Accent: #20b2aa/#40e0d0
- Glass effects, 60-30-10 rule

# MedMatch-AI KARAU - Product Requirements Document

## Original Problem Statement
Build "MedMatch," an AI-powered Life Sciences & Engineering Talent Ecosystem, combined with "AI KARAU" - an enterprise-grade video meeting portal. Perform competitive gap assessment and implement all identified feature gaps.

## Platforms
1. **AI KARAU** - Enterprise video conferencing with AI intelligence
2. **MedMatch Job Toolkit** - Life sciences talent recruitment platform

## Core Architecture
- Frontend: React + Shadcn UI + TailwindCSS
- Backend: FastAPI + MongoDB + WebSocket
- Real-time: WebRTC + WebSocket
- AI: Emergent LLM Integration
- PDF Export: reportlab (server-side)

---

## Implementation Status (All Complete)

### Core Features
- [x] Pre-meeting lobby, guest 2FA + age gate
- [x] WebRTC video/audio, screen sharing, host moderation
- [x] Breakout rooms, enterprise admin panel
- [x] Job search/apply, resume builder, interview prep
- [x] ML predictor, blind screening, ATS, salary insights

### AI Intelligence
- [x] Live captions, AI meeting summaries, polls & Q&A
- [x] AI candidate scoring, JD generator, interview scorecards
- [x] In-meeting emoji reactions, DEI analytics

### Enterprise Suite
- [x] Real-time collaborative whiteboard with WebSocket sync + persistence
- [x] Noise cancellation (Web Audio API)
- [x] Webinar mode, SFU scaling, E2E encryption, 16-lang translation

### Talent CRM & Pipeline (Feb 27, 2026)
- [x] Contact CRUD, 8-stage pipeline bar, interaction timeline
- [x] **Kanban drag-and-drop board** with real-time stage updates
- [x] Pools management, campaigns, search/filter

### Report Builder (Feb 27, 2026)
- [x] 5 report types: hiring funnel, DEI, source, time series, offer analysis
- [x] Visual charts (bar, funnel, time series, tables)
- [x] **Server-side PDF export** (reportlab with styled tables)
- [x] **CSV export** with all data sections
- [x] JSON export

### Offer Management (Feb 27, 2026)
- [x] 8-state workflow (draft → pending → approved → sent → negotiating → accepted/declined/withdrawn)
- [x] AI offer letter generation, approval timeline, stat dashboard

### Team Collaboration & Outreach (Feb 27, 2026)
- [x] **One-Click Apply** with saved profile
- [x] **Team collaboration** — candidate discussion threads, comments, reactions
- [x] **Multi-channel outreach** — Email/SMS/InMail compose, template system, delivery tracking

### Real-time Collaborative Whiteboard (Feb 27, 2026)
- [x] WebSocket sync — strokes broadcast live to all participants
- [x] Remote cursor presence (see who's drawing with name labels)
- [x] whiteboard_stroke, whiteboard_cursor, whiteboard_clear message types
- [x] Cloud save/load persistence

### Mobile Responsiveness (Feb 27, 2026)
- [x] `overflow-x-hidden` on main layout containers
- [x] Sidebar collapses with hamburger menu on mobile
- [x] All pages verified zero horizontal overflow at 375px

### Enhanced Onboarding Wizard (Feb 27, 2026)
- [x] 5-step flow: Welcome → Role Selection → Interest Picker → Feature Cards → Complete
- [x] Animated progress bar, step dots, back/next/skip navigation
- [x] 3 role options, 8 interest categories, 6 feature quick-launch cards
- [x] Saves preferences to backend, localStorage persistence

### Platform Settings (Feb 27, 2026)
- [x] Compliance dashboard (5 certifications with progress, data handling)
- [x] HRIS integration config (provider/URL/key/direction/fields, sync history)
- [x] Background checks (initiation, 8 check types, multi-provider, expandable results)

---

## Key API Endpoints

### Exports
- `GET /api/advanced/reports/{id}/export/pdf` — Server-side PDF
- `GET /api/advanced/reports/{id}/export/csv` — CSV download

### Talent CRM
- `GET/POST/PUT/DELETE /api/talent-crm/contacts/*`
- `PUT /api/talent-crm/contacts/{id}/stage` — Kanban stage updates
- `GET /api/talent-crm/pipeline`

### WebSocket
- `WS /api/karau-meet/ws/{meetingId}` — whiteboard_stroke, whiteboard_cursor, whiteboard_clear

### Team & Outreach
- `POST /api/talent-tools/one-click-apply`
- `POST/GET /api/talent-tools/collaborate/comment(s)`
- `POST /api/talent-tools/outreach/send` | `GET /api/talent-tools/outreach/history`
- `POST/GET /api/talent-tools/outreach/templates`

## MOCKED Integrations
- Outreach send (DB records, no actual email/SMS)
- HRIS sync (no external Workday/BambooHR)
- Background checks (no Checkr/Sterling)
- Payment gateways (need Stripe/PayPal keys)

## Test Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test User: test@medmatch.io / TestPassword123!

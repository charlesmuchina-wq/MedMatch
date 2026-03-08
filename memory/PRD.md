# AI KARAU + ENZI - Product Requirements Document

## Original Problem Statement
Build a dual-platform communication suite: "AI KARAU" (webinar tool) and "ENZI" (professional-grade messenger, formerly LUMI). ENZI is the primary focus — a futuristic, AI-driven "Actionable Intelligence" hub.

## What's Been Implemented

### Phase 1: AI Auto-Responses + Conversation Summaries (Completed - March 8, 2026)
- **AI Auto-Reply Suggestions**: Smart quick replies based on message bucket category (Urgent→"I'm on it!", Action Required→"On it!", Meeting Request→"I'll join")
- **AI Conversation Summaries**: One-click "Summarize" button generates AI summary of channel conversations (key decisions, action items, unresolved questions)
- Backend: `POST /api/lumi/ai/auto-reply/suggestions`, `POST /api/lumi/ai/summarize`

### Phase 2: Scheduled Messages + Bot/Automation Platform (Completed - March 8, 2026)
- **Scheduled Messages**: Schedule messages for future delivery with date/time picker, view/cancel pending messages
- **Webhook System**: Create incoming webhooks for channels, post messages via HTTP (no auth needed for webhook send)
- **Auto-Responders**: Keyword-triggered automatic responses per channel
- **Background Processor**: Checks every 30 seconds for due scheduled messages and delivers them
- Backend: `/api/lumi/automation/schedule`, `/api/lumi/automation/webhooks`, `/api/lumi/automation/auto-responders`

### Phase 3: Notification Customization (Completed - March 8, 2026)
- **Per-Channel Mute**: Set notification level per channel (All, @Mentions Only, Muted)
- **Do Not Disturb**: Toggle DND with configurable quiet hours
- **Keyword Alerts**: Add keywords to get alerted when they appear in any message
- Backend: `/api/lumi/notifications/preferences`, `/channel`, `/dnd`, `/keywords`

### Sidebar Restructure (Completed - March 8, 2026)
- "Recent" and "New Message" quick action buttons above Channels
- Smart Buckets in sidebar (Priority section with Urgent/Action Required/Meeting counts)
- Collapsible Admin Tools (2x3 grid behind Settings gear)
- Compact footer (avatar + theme + settings + logout)

### Invite System with Registration-Gated Security (Completed - March 8, 2026)
- Email/SMS/WhatsApp/LinkedIn/Instagram/Copy Link invite options
- Registration gate: invited users MUST register before accessing ENZI
- Domain-based company colleague discovery

### Brand Rename: LUMI → ENZI (Completed - March 8, 2026)
- All user-visible text updated across 15+ files

### Core Infrastructure (Previous Sessions)
- Full messenger with channels, DMs, WebSocket real-time messaging
- Google SSO + Microsoft SSO + email/password + invite registration
- AI Writing Assistant (Refine, Suggest, Translate, Voice) + Templates
- Smart Buckets, Channel Invites, MS Calendar Sync, Predictive Nav
- Compliance framework (HIPAA/GDPR), Dark/Light mode, Keyboard shortcuts

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + Outfit font
- Backend: FastAPI + MongoDB + emergentintegrations + msal + resend
- Real-time: WebSocket at /api/lumi/ws/{user_id}
- AI: GPT-4.1-mini via Emergent LLM Key

## Pending / Backlog
### P0
- E2E Encryption (E2EE) — Signal Protocol or equivalent

### P1
- Screen Sharing in Calls
- Rich Message Formatting (code blocks with syntax highlighting, tables, collapsible sections)
- Task-Driven Side Layout refinement

### P2
- Activate Sentiment Analysis (tone badges, mood trends in channels)
- Channel Templates (Project, Sprint, Incident Response)
- Full Predictive Zero-Click Navigation (reorder UI by usage frequency)
- Kinetic Typography & Micro-interactions

### P3
- Native Mobile App (React Native/Flutter)
- Live Payment Gateway (Stripe)
- Passkeys & Biometric Authentication

## Gap Assessment
Full report at `/app/memory/GAP_ASSESSMENT.md`
- ENZI leads in AI (+4), onboarding (+6), UX (+1)
- Needs E2EE, integrations, enhanced video calling

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test: test@medmatch.io / TestPassword123!
- Azure AD: Client ID 40a72049..., Tenant d4e8b623...

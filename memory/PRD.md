# AI KARAU + ENZI - Product Requirements Document

## Original Problem Statement
Build a dual-platform communication suite: "AI KARAU" (webinar tool) and "ENZI" (professional-grade messenger, formerly LUMI). ENZI is the primary focus — a futuristic, AI-driven "Actionable Intelligence" hub with Liquid Glass aesthetics and predictive design.

## What's Been Implemented

### Sidebar Restructure & New Message Flow (Completed - March 8, 2026)
- **Quick Actions**: "Recent" and "New Message" buttons above Channels section
- **Recent View**: Shows all conversations (channels + DMs) sorted by last activity with unread badges
- **New Message Panel**: Search users → find registered → start DM; user not found → invite via Email, SMS, WhatsApp, LinkedIn, Instagram, or Copy Link
- **Smart Buckets in Sidebar**: Priority section shows Urgent, Action Required, Meeting Requests with live counts
- **Collapsible Admin Tools**: Settings gear in footer expands 2x3 grid (Analytics, Retention, Audit Log, Compliance, Shortcuts, AI KARAU) + Return to Portal
- **Compact Footer**: User avatar + name + theme toggle + settings gear + logout (replaced 8 full-width buttons)

### Invite System with Registration-Gated Security (Completed - March 8, 2026)
- Email invitations via Resend API with branded HTML template
- Shareable links with 7-day expiry
- Social sharing: SMS, LinkedIn, Twitter/X, WhatsApp, Instagram
- Registration gate: invited users MUST register before accessing ENZI
- Token validation, expiry checking, already-used detection
- Invite history tracking
- Backend: `/api/lumi/invite/send`, `/api/lumi/invite/link`, `/api/lumi/invite/validate/{token}`, `/api/lumi/invite/register`, `/api/lumi/invite/history`

### Domain-Based Company Discovery (Completed - March 8, 2026)
- Users with same email domain can find and message each other
- Free email domains excluded from company matching
- Backend: `/api/lumi/domain/colleagues`, `/api/lumi/domain/info`

### ENZI Splash Screen (Completed - March 8, 2026)
- Animated logo intro (icon + gradient text + loading bar)
- Shows once per session

### Brand Rename: LUMI → ENZI (Completed - March 8, 2026)
- All user-visible text updated across 15+ files
- Translation files (en.json, sw.json) updated
- Internal code (file names, API routes, CSS classes) preserved

### Gap Assessment (Completed - March 8, 2026)
- Compared ENZI vs top 10 AI messaging apps (Teams, Slack, Discord, Zoom, Google Chat, Mattermost, Rocket.Chat, Wire, Telegram, Chanty)
- Document: `/app/memory/GAP_ASSESSMENT.md`
- Key findings: ENZI leads in AI features (+4) and invite/onboarding (+6), needs E2EE, bot platform, and enhanced video calling

### Core Infrastructure (Previous Sessions)
- Full messenger with channels, DMs, WebSocket real-time messaging
- Google SSO + Microsoft SSO (Azure AD) + email/password authentication
- AI Writing Assistant (Refine, Suggest, Translate, Voice) + Templates
- Smart Buckets (AI categorization)
- Channel invite system with approval flow
- MS Calendar status sync
- Predictive navigation
- Compliance framework (HIPAA/GDPR)
- Dark/Light mode, keyboard shortcuts

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + Outfit font
- Backend: FastAPI + MongoDB + emergentintegrations + msal + resend
- Real-time: WebSocket at /api/lumi/ws/{user_id}
- Auth: Google SSO + Microsoft SSO + email/password + invite registration

## Pending / Backlog (from Gap Assessment)
### P0 — Critical
- End-to-End Encryption (E2EE)
- Bot/Automation Platform (webhooks, scheduled messages)
- AI Conversation Summaries (meeting recaps)

### P1 — High Impact
- Screen Sharing in Calls
- Notification Customization (per-channel mute, DND, keyword alerts)
- Rich Message Formatting (code blocks, tables)
- Task-Driven Side Layout refinement

### P2 — Differentiators
- Activate Sentiment Analysis (tone badges, mood trends)
- Scheduled Messages
- Channel Templates (Project, Sprint, Incident)
- Kinetic Typography & Micro-interactions
- Full Predictive Zero-Click Navigation

### P3 — Future
- Native Mobile App (React Native/Flutter)
- Live Payment Gateway (Stripe)
- Passkeys & Biometric Authentication

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test: test@medmatch.io / TestPassword123!
- Azure AD: Client ID 40a72049..., Tenant d4e8b623...
- Resend: Testing mode (sends only to owner email)

# AI KARAU + ENZI - Product Requirements Document

## Original Problem Statement
Build a dual-platform communication suite: "AI KARAU" (webinar tool) and "ENZI" (professional-grade messenger, formerly LUMI). ENZI is the primary focus — a futuristic, AI-driven "Actionable Intelligence" hub.

## What's Been Implemented

### Rich Message Formatting (Completed - March 8, 2026)
- Full Markdown rendering: bold, italic, strikethrough, blockquotes, links, headings
- Code blocks with syntax highlighting (Prism + oneDark theme) for 50+ languages
- Tables with styled headers/cells
- Lists (ordered + unordered)
- Copy-to-clipboard button on code blocks
- Packages: react-markdown, remark-gfm, react-syntax-highlighter

### Sentiment Analysis (Completed - March 8, 2026)
- Real-time tone detection: positive, neutral, urgent, negative
- AI-powered via GPT-4.1-mini with keyword fallback
- Channel mood trends (distribution of tones across recent messages)
- CSS tone badges (.tone-positive, .tone-neutral, .tone-urgent, .tone-negative)
- Backend: `/api/lumi/sentiment/analyze`, `/api/lumi/sentiment/channel/{id}/mood`

### Channel Templates (Completed - March 8, 2026)
- 5 pre-built templates: Project, Sprint, Incident, Standup, General
- Auto-create channels with description and pinned messages
- Backend: `/api/lumi/templates/channels/list`, `/api/lumi/templates/channels/create`

### Webhook Templates (Completed - March 8, 2026)
- 5 pre-configured integrations: GitHub, Jira, CI/CD Pipeline, Slack-Compatible, Monitoring
- One-click setup with webhook URL, sample payload, and curl example
- Backend: `/api/lumi/automation/webhook-templates/list`, `/api/lumi/automation/webhook-templates/create`

### Kinetic Typography & Micro-interactions (Completed - March 8, 2026)
- Stagger-in animations on dashboard bento tiles (5 delay variants)
- Scale-in, shimmer, float CSS animations
- Hover-lift effect on interactive cards
- Gradient shimmer text effect

### AI Auto-Responses + Conversation Summaries (Completed - March 8, 2026)
- Smart quick replies based on bucket category
- AI conversation summaries (key decisions, action items, unresolved questions)

### Scheduled Messages + Bot/Automation (Completed - March 8, 2026)
- Schedule future messages with date/time picker
- Webhook system for incoming bot messages
- Auto-responder framework with keyword triggers
- Background processor (30s interval) for delivery

### Notification Customization (Completed - March 8, 2026)
- Per-channel mute (All, @Mentions, None)
- DND schedule with quiet hours
- Keyword alerts

### Sidebar Restructure + Invite System (Completed - March 8, 2026)
- Recent/New Message quick actions above Channels
- New Message: search users → invite if not found (Email, SMS, WhatsApp, LinkedIn, Instagram)
- Registration-gated invites (MUST register before accessing)
- Domain-based company colleague discovery
- Collapsible admin tools, compact footer

### Core Infrastructure (Previous Sessions)
- Full messenger with channels, DMs, WebSocket real-time messaging
- Google SSO + Microsoft SSO + email/password + invite registration
- AI Writing Assistant (Refine, Suggest, Translate, Voice) + Templates
- Smart Buckets, Channel Invites, MS Calendar Sync, Predictive Nav
- Compliance (HIPAA/GDPR), Dark/Light mode, Keyboard shortcuts

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + react-markdown + react-syntax-highlighter
- Backend: FastAPI + MongoDB + emergentintegrations + msal + resend
- Real-time: WebSocket at /api/lumi/ws/{user_id}
- AI: GPT-4.1-mini via Emergent LLM Key

## Pending / Backlog
### P0
- E2E Encryption (E2EE) — client-side key generation, key exchange, encrypted DMs

### P1
- Screen Sharing in Calls (WebRTC)
- Full Predictive Zero-Click Navigation (reorder UI by usage)

### P2
- Native Mobile App (React Native/Flutter)
- Live Payment Gateway (Stripe)
- Passkeys & Biometric Authentication

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test: test@medmatch.io / TestPassword123!
- Azure AD: Client ID 40a72049..., Tenant d4e8b623...

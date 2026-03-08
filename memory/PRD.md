# AI KARAU + ENZI - Product Requirements Document

## Original Problem Statement
Build a dual-platform communication suite: "AI KARAU" (webinar tool) and "ENZI" (professional-grade messenger, formerly LUMI). ENZI is the primary focus — a futuristic, AI-driven "Actionable Intelligence" hub.

## What's Been Implemented

### Expanded Authentication (Completed - March 8, 2026)
- GitHub SSO (MOCKED/demo mode): redirects through own callback, creates demo user
- Passkeys/WebAuthn: register + login endpoints, browser-native biometric/security key support
- Full login page with 6 auth providers: Google, Microsoft, Apple, GitHub, Phone OTP, Passkey
- "More sign-in options" expandable section for secondary auth methods
- Backend: `/api/auth/github/login`, `/api/auth/github/callback`, `/api/auth/github/config`
- Backend: `/api/auth/passkey/register/start`, `/api/auth/passkey/register/finish`
- Backend: `/api/auth/passkey/login/start`, `/api/auth/passkey/login/finish`

### Cross-Portal Integration (Completed - March 8, 2026)
- Create AI KARAU meetings directly from ENZI messenger
- Instant meeting creation with channel notification
- Scheduled meeting creation with date/time picker
- Meeting modal accessible from dashboard bento tile and chat header toolbar
- Backend: `/api/lumi/meetings/quick`, `/api/lumi/meetings/schedule`, `/api/lumi/meetings/active`
- Frontend: EnziMeetingModal component with Instant/Schedule tabs

### Rich Message Formatting (Completed - March 8, 2026)
- Full Markdown rendering: bold, italic, strikethrough, blockquotes, links, headings
- Code blocks with syntax highlighting (Prism + oneDark theme) for 50+ languages
- Tables with styled headers/cells, Lists (ordered + unordered)
- Copy-to-clipboard on code blocks
- Packages: react-markdown, remark-gfm, react-syntax-highlighter

### Sentiment Analysis (Completed - March 8, 2026)
- Real-time tone detection: positive, neutral, urgent, negative
- AI-powered via GPT-4.1-mini with keyword fallback
- Channel mood trends

### Channel Templates + Webhook Templates (Completed - March 8, 2026)
- 5 pre-built channel templates, 5 webhook integrations

### Kinetic Typography & Micro-interactions (Completed - March 8, 2026)
- Stagger-in animations, scale-in, shimmer, float CSS animations

### AI Auto-Responses + Conversation Summaries (Completed - March 8, 2026)
- Smart quick replies, AI conversation summaries

### Scheduled Messages + Bot/Automation (Completed - March 8, 2026)
- Schedule future messages, webhook system, auto-responder framework

### Notification Customization (Completed - March 8, 2026)
- Per-channel mute, DND schedule, keyword alerts

### Sidebar Restructure + Invite System (Completed - March 8, 2026)
- Recent/New Message quick actions, invite system (Email, SMS, social media)

### Core Infrastructure (Previous Sessions)
- Full messenger with channels, DMs, WebSocket real-time messaging
- Google SSO + Microsoft SSO + email/password + invite registration
- AI Writing Assistant + Templates, Smart Buckets, MS Calendar Sync, Predictive Nav
- Compliance (HIPAA/GDPR), Dark/Light mode, Keyboard shortcuts

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + react-markdown + react-syntax-highlighter
- Backend: FastAPI + MongoDB + emergentintegrations + msal + resend
- Real-time: WebSocket at /api/lumi/ws/{user_id}
- AI: GPT-4.1-mini via Emergent LLM Key

## Pending / Backlog
### P1
- Bot Store/Marketplace: backend routes + frontend UI for browsing/installing bots
- Full Predictive Zero-Click Navigation: reorder UI elements by predicted user intent

### P2
- End-to-End Encryption (E2EE) — client-side key generation, key exchange, encrypted DMs
- Screen Sharing in Calls (WebRTC)
- Live Payment Gateway (Stripe)
- Advanced Behavioral Modeling

### P3
- Legacy Admin User Display fix (show auth method instead of role)
- LumiMessenger.jsx refactoring (1200+ lines → smaller components)

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test: test@medmatch.io / TestPassword123!
- Azure AD: Client ID 40a72049..., Tenant d4e8b623...

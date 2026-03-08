# AI KARAU + ENZI - Product Requirements Document

## Original Problem Statement
Build a dual-platform communication suite: "AI KARAU" (webinar tool) and "ENZI" (professional-grade messenger). ENZI is the primary focus — a futuristic, AI-driven "Actionable Intelligence" hub with liquid glass aesthetics, bento grid layouts, and predictive behavior.

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + react-markdown + react-syntax-highlighter
- Backend: FastAPI + MongoDB + emergentintegrations + msal + resend
- Real-time: WebSocket at /api/lumi/ws/{user_id}
- AI: GPT-4.1-mini via Emergent LLM Key
- Payments: Stripe via emergentintegrations (LIVE test mode)

## Implementation Status

### Completed Features

#### Authentication (6 Providers)
- Google SSO (Emergent-managed), Microsoft SSO (MSAL), Apple (config-ready)
- GitHub SSO (MOCKED demo mode), Passkeys/WebAuthn, Email/Password
- "More sign-in options" expandable section
- Backend: `/api/auth/github/*`, `/api/auth/passkey/*`

#### Cross-Portal Integration
- Create AI KARAU meetings from ENZI messenger
- Instant + scheduled meetings with channel notifications
- Dashboard bento tile + chat header Video button
- Backend: `/api/lumi/meetings/quick|schedule|active|history`

#### Bot Store/Marketplace
- 8 pre-built bots: Standup, Reminder, Poll, Meeting, Welcome, Summary, Translator, GitHub Notify
- Browse/install/uninstall per channel, category filtering, search
- Bot Actions Bar in channels with quick-trigger buttons (Start Poll, Run Standup, etc.)
- Backend: `/api/lumi/bots/catalog|install|installed|uninstall|action|channel/{id}`

#### End-to-End Encryption (E2EE)
- ECDH P-256 key exchange + AES-GCM 256-bit encryption
- Client-side keys in IndexedDB (never leave device)
- E2EE indicator in DM channels with enable button
- Backend: `/api/lumi/e2ee/keys/*`, `/api/lumi/e2ee/dm/{id}/status`

#### Live Stripe Payment Gateway
- 4 premium tiers: Pro Monthly ($9.99), Pro Yearly ($99.99), Team ($29.99), Enterprise ($99.99)
- Real Stripe checkout via emergentintegrations (test mode with real sessions)
- Payment polling, subscription management, transaction history
- Backend: `/api/lumi/payments/packages|checkout|status/{id}|my-subscription|history`

#### Advanced Behavioral Modeling
- Context-aware triggers (unread overload, inactive channels, time-based, scheduled messages)
- Smart suggestions (bot recommendations, meeting suggestions, wellbeing tips, security)
- Usage insights (engagement score, message counts, peak hours)
- Backend: `/api/lumi/behavior/context-triggers|smart-suggestions|usage-insights`

#### Predictive Zero-Click Navigation
- Channels/DMs sorted by predicted usage with Zap indicators
- Tracks channel visits, DM opens, time-of-day patterns
- Backend: `/api/lumi/predict/track|suggestions|stats`

#### Screen Sharing (WebRTC)
- Already implemented in MeetingRoom.jsx with getDisplayMedia API
- Track replacement for peer connections
- Auto-revert on share end

#### Rich Message Formatting
- Markdown: bold, italic, strikethrough, blockquotes, links, headings
- Code blocks with syntax highlighting (50+ languages)
- Tables, ordered/unordered lists

#### AI Feature Suite
- Sentiment Analysis, Conversation Summaries, Scheduled Messages
- AI Writing Assistant, Auto-Responses, Smart Quick Replies

#### Other Features
- Channel Templates, Webhook Templates, Kinetic Typography
- Advanced Invite System (Email, SMS, social media)
- Sidebar restructure, Notification customization
- Domain-based colleague discovery
- Meeting History panel, User Profile with auth method badges

### Refactoring Done
- Extracted `useEnziData` custom hook for data loading
- Created separate components: BotActionsBar, BotStoreModal, E2EEIndicator, EnziMeetingModal, MeetingHistoryPanel, PremiumModal, InsightsPanel

## Test Results
- Batch A (Bot Actions + Predictive Nav): 100% (15/15 BE, 12/12 FE)
- Batch B (E2EE + Refactoring): 100% (21/21 BE, 12/12 FE)
- Batch C (Stripe + Behavioral): 100% (24/24 BE, 15/15 FE)

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test: test@medmatch.io / TestPassword123!

## Remaining / Future Enhancements
- Voice/Video call improvements (noise cancellation, virtual backgrounds)
- Advanced ML models for more accurate behavioral predictions
- Webhook & Channel Template marketplace
- Mobile app optimization
- Advanced admin analytics dashboard

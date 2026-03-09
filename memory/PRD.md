# AI KARAU + ENZI - Product Requirements Document

## Original Problem Statement
Build a dual-platform communication suite: "AI KARAU" (webinar tool) and "ENZI" (professional-grade messenger), plus "MedMatch AI" (job-seeking toolkit). ENZI is the primary focus — a futuristic, AI-driven "Actionable Intelligence" hub with liquid glass aesthetics, bento grid layouts, and predictive behavior. The platform should offer bundled and standalone packages with a unified workspace that allows running portals side-by-side.

## Architecture
- Frontend: React + Tailwind + Shadcn/UI + react-markdown + react-syntax-highlighter
- Backend: FastAPI + MongoDB + emergentintegrations + msal + resend
- Real-time: WebSocket at /api/lumi/ws/{user_id}
- AI: GPT-4.1-mini via Emergent LLM Key
- Payments: Stripe via emergentintegrations (LIVE test mode)

## Unified Authentication (All 3 Portals)
All portals share the same `/api/auth/login` backend. Standardized auth providers:
- **Google SSO** (Emergent-managed) - All portals
- **Microsoft SSO** (MSAL) - All portals
- **Apple Sign-In** - All portals (config-ready)
- **GitHub SSO** (MOCKED demo) - All portals
- **Passkeys/WebAuthn** - ENZI + AI KARAU
- **Phone OTP** - ENZI (planned)
- **Email/Password** - All portals
- **Cross-Portal Auth Sync** - `/api/portal/sync-session` creates both cookie + localStorage token
- Credentials: admin@medmatch.com / Swampdrainer2026!, test@medmatch.io / TestPassword123!

## Portal Packaging System (COMPLETED - Feb 2026)
Users can select from 3 packages:
- **Standard**: AI KARAU + ENZI (Communication Suite) — Popular
- **Standalone**: MedMatch Job Toolkit (Career Intelligence)
- **Enterprise**: All 3 portals (Complete Platform) — Full Access

### Key Files:
- Landing page: `frontend/src/pages/PortalSelector.jsx` (package-focused)
- Post-login management: `frontend/src/components/Lumi/PackageSelector.jsx` (at /packages route)
- Backend API: `backend/routes/portal_access.py`
- Header button: "Portals" button in App.js header navigates to /packages

### API Endpoints:
- `GET /api/portal/packages` - List all packages
- `GET /api/portal/access` - Get user's current package
- `POST /api/portal/set-package` - Update user's package
- `POST /api/portal/sync-session` - Cross-portal auth sync (cookie + token)
- `GET /api/portal/check-access/{portal}` - Check portal access

## Portal Workspace (COMPLETED - Mar 2026)
Unified multi-portal workspace allowing side-by-side portal usage.

### Flow:
1. User selects a bundle on landing page → Login
2. After login, portals appear in a dock bar at the bottom
3. Main portal runs full-width
4. Click dock icon to open secondary portal as side panel
5. Side panel supports 3 sizes: narrow (320px), wide (440px), half (50%)
6. Swap button exchanges main and side portals
7. Both portals run simultaneously (e.g., KARAU meeting + ENZI chat)

### Key Files:
- `frontend/src/components/PortalWorkspace.jsx` - Workspace layout, dock, side panel, hub
- `frontend/src/components/Lumi/EnziCompactPanel.jsx` - Compact ENZI for side panel
- `frontend/src/components/KarauMeet/KarauCompactPanel.jsx` - Compact KARAU for side panel
- `frontend/src/App.js` - Workspace integration, PortalDockOverlay for MedMatch

### Features:
- PortalDock: Persistent footer bar with portal icons (Main/Side/Dock states)
- PortalHub: Initial view showing all bundle portals to select main
- Side Panel: Resizable with controls (resize/swap/close)
- Compact Panels: Lightweight versions of portals for side panel usage
- MedMatch floating dock: Floating portal switcher in bottom-right corner
- localStorage polling: Workspace detects portal_access changes after login

## Completed Features

### Cross-Portal Meeting Integration
- Create AI KARAU meetings from ENZI, instant + scheduled, channel notifications

### Bot Store/Marketplace
- 8 pre-built bots with quick-trigger Bot Actions Bar in channels

### End-to-End Encryption (E2EE)
- ECDH P-256 + AES-GCM, client-side keys, DM indicators

### Live Stripe Payments
- 4 premium tiers ($9.99-$99.99), real Stripe checkout (test mode)

### Advanced Behavioral Modeling
- Context-aware triggers, smart suggestions, usage insights, engagement scoring

### Predictive Zero-Click Navigation
- Channels/DMs sorted by predicted usage with Zap indicators

### Screen Sharing (WebRTC)
- Already in MeetingRoom.jsx with getDisplayMedia

### Other Features
- Rich Markdown + code blocks, Sentiment Analysis, AI Summaries, Scheduled Messages
- AI Writing Assistant, Invite System, Channel/Webhook Templates, Kinetic Typography
- Notification customization, Domain colleague discovery, Meeting History

## Test Results
- Portal Workspace: 100% frontend, 77% backend (6 failures are test fixture issues) — iteration_200
- Portal Packaging: 25/25 BE, all FE flows — 100% pass (iteration_199)
- Previous batches: All passed 100%

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test: test@medmatch.io / TestPassword123!

## Remaining Tasks (Priority Order)
- **P1**: Full Bot Store/Marketplace — install, configure, manage bots
- **P2**: Webhook & Channel Templates — full implementation
- **P2**: Refactor `LumiMessenger.jsx` — break monolith into smaller components
- **P3**: Voice/Video improvements (noise cancellation, virtual backgrounds)
- **P3**: Advanced ML for better predictions
- **P3**: Mobile optimization
- **P3**: Team Analytics Dashboard (premium feature idea)

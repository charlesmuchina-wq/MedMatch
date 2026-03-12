# CHANGELOG

## March 12, 2026 — Phases 1-4 Implementation

### Phase 1: Code Health & Stability (DONE)
- **EnziChatView.jsx** extracted from LumiMessenger.jsx (804 → 693 lines)
- **AiSummaryWidget.jsx** + **KarauAnalyticsRow.jsx** extracted from KarauMeetDashboard.jsx (998 → 755 lines)
- GitHub SSO labeled as "(Demo)" in login UI
- All functionality preserved — 100% test pass

### Phase 2: AI-Powered Call Enhancements (DONE)
- AI Meeting Transcription (Whisper via Emergent LLM Key) — already built
- AI Meeting Summary/Notes (GPT-4o) — already built
- Push Notifications: VAPID keys generated and configured, pywebpush ready
- In-app notification fallback system active

### Phase 3: Collaboration Features (DONE)
- **Bot-to-Bot Chaining**: Full workflow automation system
  - Create named chains with 2+ bot steps
  - Run chains — each bot output feeds as context to the next
  - System messages announce chain start
  - UI: "Workflows" tab in Channel Tools modal (BotChainBuilder)
  - Backend: CRUD + execution at /api/lumi/bots/chains/*
- AI Writing Toolbar (Phase 3.1) — already comprehensive with refine, suggest, translate, voice, templates

### Phase 4: Polish & Growth (PARTIAL)
- Portal logos restored on landing page
- Mobile-responsive layout verified at 375px

## March 11, 2026 — Bot Marketplace + Domain Routing

### P1: AI-Powered Bot Marketplace (DONE)
- 18 bots across 4 categories with real GPT-4o AI responses
- Quick action buttons (BotActionsBar) + Slash commands with autocomplete
- Bot install/uninstall/configure per channel
- Backend: generate_bot_response() with specialized system prompts

### Previous Session Completed
- Meeting-to-Channel Admin Approval
- Domain-Aware Routing System (multi-subdomain)
- AI KARAU tagline shortening
- LumiMessenger initial refactor (EnziSidebar, EnziDashboard)

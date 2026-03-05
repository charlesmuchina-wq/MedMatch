# AI KARAU + LUMI — Product Requirements Document

## Original Problem Statement
Build a dual-platform communication suite:
- **AI KARAU**: Feature-rich webinar/meeting tool with AI meeting intelligence
- **LUMI**: Professional-grade enterprise messenger with AI-driven "Actionable Intelligence" hub

## Core Requirements
1. Secure, compliant messenger (chat, DMs, file sharing, reactions, presence)
2. ESY-themed UI with accessibility (pink, turquoise, deep red accents)
3. AI productivity features (summaries, action items, sentiment analysis, reports)
4. Futuristic AI & agentic workflows (NLP querying, anomaly alerts, decision cards, knowledge graph, bottleneck detection, what-if simulations, real-time translation)
5. SSO integration (Google + Microsoft)
6. Core app features (threading, voice/video calls, message retention)
7. User Profile Dashboard (capabilities, channel subscriptions, notification preferences, status)

## Architecture
```
/app/
├── backend/
│   ├── routes/
│   │   ├── auth.py                      # Auth: login, register, Google SSO, Microsoft placeholder
│   │   ├── lumi_messenger.py            # Core LUMI: channels, DMs, presence, profile, notification prefs
│   │   ├── lumi_ai_routes.py            # AI: sentiment, tasks, reports, translation
│   │   ├── futuristic_ai_routes.py      # AI: ask, anomalies, decision cards
│   │   ├── knowledge_graph_routes.py    # Knowledge graph, impact analysis
│   │   └── advanced_collaboration_routes.py  # Simulations, bottlenecks, notifications
│   └── server.py
└── frontend/
    └── src/
        ├── components/
        │   └── Lumi/                    # REFACTORED components (16 files)
        │       ├── constants.js         # ESY theme, API, status constants
        │       ├── ChannelIcon.jsx      
        │       ├── StatusDot.jsx        
        │       ├── MessageBubble.jsx    # Message display with reactions, translation
        │       ├── ThreadPanel.jsx      # Message threading
        │       ├── MembersPanel.jsx     # Channel members
        │       ├── AiProductivityPanel.jsx  # Sentiment, Tasks, Reports
        │       ├── AiChatPanel.jsx      # Conversational AI
        │       ├── AlertsPanel.jsx      # Anomaly Alerts & Decision Cards
        │       ├── CommandBar.jsx       # Ctrl+K global search
        │       ├── KnowledgeGraphPanel.jsx  # Knowledge graph visualization
        │       ├── BottleneckPanel.jsx  # Bottleneck detection
        │       ├── SimulationPanel.jsx  # What-if simulations
        │       ├── NotificationsPanel.jsx   # Smart notifications
        │       ├── CreateChannelModal.jsx
        │       ├── NewDmModal.jsx
        │       ├── LumiLogin.jsx        # Login with Google SSO + Microsoft placeholder
        │       ├── UserProfileModal.jsx # NEW: Profile, capabilities, channel prefs, status
        │       └── index.js             # Barrel exports
        └── pages/
            ├── LoginPage.jsx            # Main login (Google, Apple, ORCID, Microsoft)
            ├── LumiMessenger.jsx        # Main LUMI container (imports from /Lumi)
            └── KarauMeet/
                ├── KarauMeetLogin.jsx   # KarauMeet login (Google SSO + Microsoft)
                └── Dashboard.jsx
```

## What's Been Implemented

### Previous Sessions
- Full LUMI messenger: channels, DMs, reactions, search, file sharing, read receipts
- AI Feature Suite: Sentiment, Tasks, Reports, Ask LUMI AI, Decision Cards, Anomaly Alerts
- Graph Intelligence: Ctrl+K Command Bar, Knowledge Graph, Bottleneck Detection
- Advanced: What-If Simulations, Smart Notifications
- Real-time Translation (20 languages), ESY theme throughout

### Current Session (Feb 2026)
- **Google SSO**: Integrated Emergent-managed Google Auth across all 3 login pages
- **Microsoft SSO**: Placeholder button on all login pages (shows "coming soon" toast)
- **Refactoring**: LumiMessenger.jsx from 2218→~500 lines with 16 extracted components
- **Contrast Fix**: Fixed faint grey text against white background across LUMI
- **User Profile Modal**: Accessible from sidebar avatar, shows:
  - User info (name, email, role, messages sent)
  - Presence status selector (5 statuses)
  - LUMI Capabilities (15 features in 7 categories, collapsible)
  - Channel Subscriptions (11 channels) with per-channel notification preferences (All/Mentions/None)

## Prioritized Backlog

### P1 - Upcoming
- User Profile & Status Sync (calendar status from Google/Microsoft)
- Centralized Notification Center (consolidate all AI alerts)
- Voice & Video Calls (LUMI → AI KARAU integration)
- Message Edit/Delete with configurable time window

### P2 - Future
- Message Retention Policy (admin UI)
- Full Knowledge Graph Integration (MS Project/SharePoint)
- End-to-End Encryption (E2EE)
- Admin Audit Logs
- Live Payment Gateway (Stripe live keys)

## 3rd Party Integrations
- **Emergent LLM Key**: Gemini + GPT-5.2 for AI features
- **Emergent Object Storage**: File sharing in LUMI
- **Emergent Google Auth**: SSO for all login pages
- **Stripe**: Payments (test keys)
- **Microsoft Graph API**: To be integrated (SSO placeholder ready)

## Test Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test: test@medmatch.io / TestPassword123!

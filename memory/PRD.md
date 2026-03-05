# AI KARAU + LUMI — Product Requirements Document

## Original Problem Statement
Build a dual-platform communication suite:
- **AI KARAU**: Feature-rich webinar/meeting tool with AI meeting intelligence
- **LUMI**: Professional-grade enterprise messenger — *"Intelligence in Every Conversation"*

## Core Requirements
1. Secure, compliant messenger (chat, DMs, file sharing, reactions, presence)
2. ESY-themed UI with accessibility (pink, turquoise, deep red accents)
3. AI productivity features (summaries, action items, sentiment analysis, reports)
4. Futuristic AI & agentic workflows (NLP querying, anomaly alerts, decision cards, knowledge graph, bottleneck detection, what-if simulations, real-time translation)
5. SSO integration (Google + Microsoft)
6. Core app features (threading, voice/video calls, message edit/delete, retention)
7. Content moderation & multi-jurisdiction compliance (HIPAA, GDPR, PIPL, APPI, UK DPA, AU Privacy)
8. Visualizations: Activity charts, project timelines, knowledge graph

## Architecture
```
/app/
├── backend/
│   ├── routes/
│   │   ├── auth.py                       # Auth + Google SSO + Microsoft placeholder
│   │   ├── lumi_messenger.py             # Core: channels, DMs, presence, profile, edit/delete, calls, notif hub, retention, org-settings, audit log, moderation, compliance, calendar sync, analytics/visualizations
│   │   ├── lumi_ai_routes.py             # AI: sentiment, tasks, reports, translation
│   │   ├── futuristic_ai_routes.py       # AI: ask, anomalies, decision cards
│   │   ├── knowledge_graph_routes.py     # Knowledge graph, impact analysis
│   │   └── advanced_collaboration_routes.py  # Simulations, bottlenecks, notifications
│   └── server.py
└── frontend/
    └── src/
        ├── components/Lumi/              # 25 extracted components
        │   ├── VisualizationsPanel.jsx   # Activity/Timeline/Knowledge with Recharts
        │   ├── ComplianceWidget.jsx      # Sidebar compliance score widget
        │   ├── CompliancePanel.jsx       # Multi-jurisdiction compliance dashboard
        │   ├── AdminAuditPanel.jsx       # Audit log viewer
        │   ├── EmojiPicker.jsx           # Native emoji picker
        │   ├── KeyboardShortcuts.jsx     # Shortcuts panel + hook
        │   ├── RetentionPanel.jsx        # Retention with approval workflow
        │   ├── UserProfileModal.jsx      # Profile with theme picker
        │   └── ... (17 more components)
        └── pages/
            ├── LumiMessenger.jsx         # Main orchestrator
            └── LoginPage.jsx             # Google + Microsoft SSO
```

## Completed Features

### Core Messenger
- Channels (group, project, announcement, domain-based), DMs, file sharing, reactions
- Real-time WebSocket messaging, read receipts, presence, search
- Message threading, real-time translation (20 languages)
- Message edit/delete with 15-min window

### SSO & Auth
- Google SSO (Emergent Auth) fully integrated
- Microsoft SSO placeholder
- JWT email/password auth

### AI Suite
- Sentiment Analysis, Task Extraction, Weekly Reports
- Ask LUMI AI, Decision Cards, Anomaly Alerts
- Knowledge Graph, Bottleneck Detection, What-If Simulations
- Command Bar (Ctrl+K), Smart Notifications

### Privacy & Compliance (March 5, 2026)
- **Content Moderation**: Profanity filter, configurable settings, moderation log
- **6 Compliance Frameworks**: HIPAA, GDPR, UK DPA, AU Privacy, China PIPL, Japan APPI
- **92% Compliance Score** with 10 platform security controls
- **AI KARAU compliance reference** integration
- **Compliance Widget**: Always-visible sidebar score bar (auto-refreshes)

### Visualizations (March 5, 2026)
- **Activity Dashboard**: 4 KPI cards, 7-day message volume chart, channel activity bars, 24-hour heatmap
- **Project Timeline**: 6 milestones with status tracking, task burndown chart, team capability radar
- **Knowledge Graph**: Entity distribution pie, connection strength bars, interactive 12-node SVG network

### Admin & Retention
- 90-day auto-delete with hold approval workflow
- Admin Audit Log with search & category filters
- Organization settings (IT admin, manager contacts)

### UX Polish
- Emoji Picker (9 categories, search, recents, Ctrl+E)
- Keyboard Shortcuts system (Ctrl+/ panel, global hotkeys)
- Profile Theme Picker (10 accent colors)
- Google Calendar Status Sync (5-min auto)
- Tagline: "Intelligence in Every Conversation"

## Prioritized Backlog

### P0 - Next
- **Microsoft SSO Integration** — Full MS Graph API auth flow (currently placeholder)

### P1
- **WebSocket 403 Fix** — Investigate real-time connection failure
- **Microsoft Calendar Sync** — After MS SSO

### P2 - Future
- Full Knowledge Graph + MS Project/SharePoint integration
- End-to-End Encryption (E2EE)
- Stripe live payment transition

## Key API Endpoints
- `GET /api/lumi/analytics/visualizations?tab=activity|timeline|graph`
- `GET /api/lumi/compliance/status` + `/frameworks`
- `GET /api/lumi/admin/audit-log`
- `POST /api/lumi/moderation/check`
- `GET/PUT /api/lumi/moderation/settings`
- `POST /api/lumi/calendar/sync`
- `POST /api/lumi/admin/hold` + `/hold-requests/{id}`

## 3rd Party Integrations
- Emergent LLM Key (Gemini + GPT-5.2), Emergent Object Storage, Emergent Google Auth
- Stripe (test keys), Microsoft Graph API (placeholder)
- Recharts for data visualization

## Test Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test: test@medmatch.io / TestPassword123!

## Known Issues
- WebSocket connection returns 403 (non-blocking)
- Microsoft SSO returns 501 (placeholder)

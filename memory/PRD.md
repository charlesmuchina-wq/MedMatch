# AI KARAU + LUMI — Product Requirements Document

## Original Problem Statement
Build a dual-platform communication suite:
- **AI KARAU**: Feature-rich webinar/meeting tool with AI meeting intelligence
- **LUMI**: Professional-grade enterprise messenger — *"Intelligence in Every Conversation"*

## Architecture
```
/app/
├── backend/
│   ├── routes/
│   │   ├── auth.py                       # Auth + Google SSO + Microsoft placeholder
│   │   ├── lumi_messenger.py             # Core messenger + WebSocket + moderation + compliance + analytics
│   │   ├── lumi_ai_routes.py             # AI features
│   │   ├── futuristic_ai_routes.py       # Advanced AI
│   │   ├── knowledge_graph_routes.py     # Knowledge graph
│   │   └── advanced_collaboration_routes.py  # Simulations, bottlenecks
│   └── server.py
└── frontend/
    └── src/
        ├── components/
        │   ├── LumiFooter.jsx            # Shared footer (3 variants: default, compact, overlay)
        │   └── Lumi/                     # 25+ extracted components
        └── pages/
            ├── LumiMessenger.jsx         # Main orchestrator
            └── ...
```

## Completed Features

### Core Messenger
- Channels, DMs, file sharing, reactions, threading, real-time translation (20 languages)
- Real-time WebSocket messaging (FIXED - was 403, now working via @router.websocket)
- Message edit/delete with 15-min window, read receipts, presence, search

### Auth & SSO
- Google SSO (Emergent Auth) fully integrated
- Microsoft SSO placeholder (501)
- JWT email/password auth

### AI Suite
- Sentiment Analysis, Task Extraction, Weekly Reports
- Ask LUMI AI, Decision Cards, Anomaly Alerts, Knowledge Graph
- Bottleneck Detection, What-If Simulations, Command Bar (Ctrl+K)

### Privacy & Compliance
- Content Moderation: Profanity filter, configurable settings, moderation log
- 6 Compliance Frameworks: HIPAA, GDPR, UK DPA, AU Privacy, China PIPL, Japan APPI
- 92% Compliance Score, 10 platform security controls, AI KARAU compliance reference
- Compliance Widget: Always-visible sidebar score bar

### Visualizations
- Activity Dashboard: KPIs, 7-day message volume, channel activity bars, 24h heatmap
- Project Timeline: 6 milestones with status, burndown chart, team radar
- Knowledge Graph: Entity distribution, connection strength, 12-node SVG network

### Admin & Retention
- 90-day auto-delete with hold approval workflow
- Admin Audit Log with search & category filters
- Organization settings (IT admin, manager contacts)

### UX
- Emoji Picker (9 categories, search, Ctrl+E)
- Keyboard Shortcuts (Ctrl+/ panel, global hotkeys)
- Profile Theme Picker (10 accent colors)
- Google Calendar Status Sync (5-min auto)
- **Global Footer**: "Intelligence in Every Conversation" on ALL pages (Portal, Login, KarauMeet, LUMI, Dashboard, public routes)

## Prioritized Backlog

### P0 - Next
- Microsoft SSO — Full MS Graph API auth flow

### P1
- Microsoft Calendar Sync (after MS SSO)
- Interactive Knowledge Graph (clickable nodes → navigate to channels/users/tasks)

### P2 - Future
- Full Knowledge Graph + MS Project/SharePoint integration
- End-to-End Encryption (E2EE)
- Stripe live payment transition

## Test Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test: test@medmatch.io / TestPassword123!

## Known Issues
- Microsoft SSO returns 501 (placeholder)
- WebSocket: FIXED (was 403, now working)

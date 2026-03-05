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
│   │   ├── auth.py                       # Auth + Google SSO + Microsoft SSO (configurable)
│   │   ├── lumi_messenger.py             # Core messenger + WebSocket + moderation + compliance + analytics
│   │   ├── lumi_ai_routes.py             # AI features
│   │   ├── futuristic_ai_routes.py       # Advanced AI
│   │   ├── knowledge_graph_routes.py     # Knowledge graph
│   │   └── advanced_collaboration_routes.py
│   └── server.py
└── frontend/
    └── src/
        ├── components/
        │   ├── LumiFooter.jsx            # Shared footer with LUMI icon
        │   └── Lumi/                     # 25+ components
        │       ├── VisualizationsPanel.jsx  # Interactive Knowledge Graph + Charts
        │       └── ...
        └── pages/
            ├── LumiMessenger.jsx
            └── ...
```

## Completed Features

### Branding
- **LUMI App Icon**: Custom icon integrated across favicon, sidebar, login hero, welcome screen, portal selector, footer
- **Tagline**: "Intelligence in Every Conversation" on all pages
- **Global Footer**: Visible on Portal Selector, Login, KarauMeet, LUMI Messenger, Dashboard

### Auth & SSO
- Google SSO (Emergent Auth) fully integrated
- **Microsoft SSO**: Full OAuth2 flow architecture (configurable placeholder)
  - Endpoints: /microsoft/login, /microsoft/callback, /microsoft/config
  - Ready to activate with AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET
  - Returns "not configured" message when keys missing
- JWT email/password auth

### Core Messenger
- Channels, DMs, file sharing, reactions, threading, translation (20 languages)
- Real-time WebSocket messaging (FIXED from 403)
- Message edit/delete, read receipts, presence, search

### AI Suite
- Sentiment Analysis, Task Extraction, Weekly Reports
- Ask LUMI AI, Decision Cards, Anomaly Alerts
- Knowledge Graph, Bottleneck Detection, What-If Simulations

### Privacy & Compliance
- Content Moderation: Profanity filter, configurable, incident log
- 6 Frameworks: HIPAA, GDPR, UK DPA, AU Privacy, China PIPL, Japan APPI
- 92% Compliance Score, 10 platform controls, AI KARAU reference
- Compliance Widget: Sidebar score bar (auto-refresh)

### Visualizations
- **Activity Dashboard**: KPIs, message volume, channel activity, 24h heatmap
- **Project Timeline**: Milestones, burndown chart, team radar
- **Interactive Knowledge Graph**: Clickable nodes with hover effects, pulse animations, connection highlighting, detail card popup, category labels

### Admin
- Audit Log with search & category filters
- 90-day auto-delete with hold approval workflow

### UX
- Emoji Picker (Ctrl+E), Keyboard Shortcuts (Ctrl+/)
- Profile Theme Picker, Google Calendar Status Sync

## Prioritized Backlog

### P1 - Next
- Microsoft Calendar Sync (after Azure keys provided)
- Full Knowledge Graph + MS Project/SharePoint integration

### P2 - Future
- End-to-End Encryption (E2EE)
- Stripe live payment transition

## Test Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test: test@medmatch.io / TestPassword123!

## Configuration Required
- **Microsoft SSO**: Set AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET in backend/.env

## Known Issues
- Microsoft SSO returns 501 until Azure credentials configured (by design)

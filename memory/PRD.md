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
6. Core app features (threading, voice/video calls, message edit/delete, retention)
7. User Profile Dashboard (capabilities, channel subscriptions, notification preferences, status)
8. Centralized Notification Center (aggregated from all sources)

## Architecture
```
/app/
├── backend/
│   ├── routes/
│   │   ├── auth.py                       # Auth + Google SSO + Microsoft placeholder
│   │   ├── lumi_messenger.py             # Core: channels, DMs, presence, profile, edit/delete, calls, notif hub
│   │   ├── lumi_ai_routes.py             # AI: sentiment, tasks, reports, translation
│   │   ├── futuristic_ai_routes.py       # AI: ask, anomalies, decision cards
│   │   ├── knowledge_graph_routes.py     # Knowledge graph, impact analysis
│   │   └── advanced_collaboration_routes.py  # Simulations, bottlenecks, notifications
│   └── server.py
└── frontend/
    └── src/
        ├── components/Lumi/              # 17 extracted components
        │   ├── MessageBubble.jsx         # + edit/delete, profile pics, (edited) label
        │   ├── NotificationsPanel.jsx    # Centralized hub with source tabs
        │   ├── UserProfileModal.jsx      # + profile pic, auth method badge
        │   └── ... (14 more components)
        └── pages/
            ├── LumiMessenger.jsx         # + edit/delete/call handlers, ws events
            ├── LoginPage.jsx             # Google + Microsoft SSO
            └── KarauMeet/KarauMeetLogin.jsx
```

## Completed Features (All Sessions)

### Core Messenger
- Channels (group, project, announcement, domain-based), DMs, file sharing, reactions
- Real-time WebSocket messaging, read receipts, presence, search
- Message threading, real-time translation (20 languages)

### SSO & Auth
- Google SSO (Emergent Auth) on all 3 login pages
- Microsoft SSO placeholder buttons
- JWT email/password auth

### AI Feature Suite
- Sentiment Analysis, Task Extraction, Weekly Reports
- Ask LUMI AI (conversational), Decision Cards, Anomaly Alerts
- Knowledge Graph, Bottleneck Detection, What-If Simulations
- Command Bar (Ctrl+K), Smart Notifications

### P1 Features (Current Session)
- **User Profile Modal**: Capabilities, channel subscriptions, notification prefs, status picker
- **Profile Picture Sync**: Stored from Google SSO, displayed in chat & profile
- **Centralized Notification Hub**: Aggregates mentions, anomalies, tasks, DMs with source tabs
- **Voice & Video Calls**: Phone + Camera buttons in DM headers, creates call records, opens AI KARAU
- **Message Edit/Delete**: Pencil/trash on hover (own messages), 15-min window, inline edit, (edited) label
- **Contrast/Accessibility Fix**: All text darkened for readability

## Prioritized Backlog

### P2 - Future
- Message Retention Policy (admin UI for auto-delete rules)
- Full Knowledge Graph Integration (MS Project/SharePoint via Graph API)
- End-to-End Encryption (E2EE) for messages and files
- Admin Audit Logs (secure, searchable admin action log)

### P3 - Backlog
- Live Payment Gateway (Stripe test → production keys)

## 3rd Party Integrations
- Emergent LLM Key (Gemini + GPT-5.2), Emergent Object Storage, Emergent Google Auth
- Stripe (test keys), Microsoft Graph API (placeholder)

## Test Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test: test@medmatch.io / TestPassword123!

## Mocked/Placeholder
- Microsoft SSO (501 placeholder)
- Voice/Video calls (record created, no real WebRTC)
- Stripe payments (test keys)

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
9. **Message Retention Policy**: 90-day auto-delete with privileged hold management (approval workflow)

## Architecture
```
/app/
├── backend/
│   ├── routes/
│   │   ├── auth.py                       # Auth + Google SSO + Microsoft placeholder
│   │   ├── lumi_messenger.py             # Core: channels, DMs, presence, profile, edit/delete, calls, notif hub, retention, org-settings
│   │   ├── lumi_ai_routes.py             # AI: sentiment, tasks, reports, translation
│   │   ├── futuristic_ai_routes.py       # AI: ask, anomalies, decision cards
│   │   ├── knowledge_graph_routes.py     # Knowledge graph, impact analysis
│   │   └── advanced_collaboration_routes.py  # Simulations, bottlenecks, notifications
│   └── server.py
└── frontend/
    └── src/
        ├── components/Lumi/              # 20 extracted components
        │   ├── RetentionPanel.jsx        # Retention with approval workflow, org settings, tabs
        │   ├── UserProfileModal.jsx      # Profile with theme picker, capabilities, subscriptions
        │   ├── MessageBubble.jsx         # + edit/delete, profile pics, (edited) label
        │   ├── NotificationsPanel.jsx    # Centralized hub with source tabs
        │   └── ... (16 more components)
        └── pages/
            ├── LumiMessenger.jsx         # Main orchestrator
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

### P1 Features
- **User Profile Modal**: Capabilities, channel subscriptions, notification prefs, status picker
- **Profile Theme Picker**: 10 accent colors, persists to DB, preview
- **Profile Picture Sync**: Stored from Google SSO, displayed in chat & profile
- **Centralized Notification Hub**: Aggregates mentions, anomalies, tasks, DMs with source tabs
- **Voice & Video Calls**: Phone + Camera buttons in DM headers, creates call records
- **Message Edit/Delete**: Pencil/trash on hover, 15-min window, inline edit, (edited) label
- **Contrast/Accessibility Fix**: All text darkened for readability

### Message Retention & Privacy (Updated)
- **Global 90-day auto-delete**: Automatic for all channels (not per-channel)
- **Hold Approval Workflow**: Holds require IT admin + manager approval
- **Organization Admin Settings**: IT admin, manager contacts, department, compliance officer
- **Hold Request System**: Submit → Pending → Approve/Reject → Active hold
- **Legal Hold**: Indefinite preservation until released
- **Contractual Hold**: Custom duration with expiration date
- **Hold Release**: Admins can release active holds

## Prioritized Backlog

### P0 - Next
- Finalize Microsoft SSO Integration (user has no Azure credentials yet)

### P1
- User Status Sync from Google/Microsoft calendars

### P2 - Future
- Full Knowledge Graph Integration (MS Project/SharePoint via Graph API)
- End-to-End Encryption (E2EE) for messages and files
- Admin Audit Logs (secure, searchable admin action log)

### P3 - Backlog
- Live Payment Gateway (Stripe test → production keys)

## Key API Endpoints (Retention)
- `GET /api/lumi/admin/retention` - Overview with channels, holds, requests, global_retention_days
- `GET/PUT /api/lumi/admin/org-settings` - IT admin and manager contacts
- `POST /api/lumi/admin/hold` - Submit hold request (creates pending)
- `PUT /api/lumi/admin/hold-requests/{id}` - Approve/reject hold request
- `DELETE /api/lumi/admin/hold/{id}` - Release active hold
- `GET/PUT /api/lumi/profile/theme` - User accent color

## DB Collections (Retention)
- `lumi_org_settings`: key="admin_config", it_admin_name/email, manager_name/email, department, compliance_officer
- `lumi_hold_requests`: id, channel_id, hold_type, reason, status (pending/approved/rejected), it_admin_email, manager_email
- `lumi_holds`: id, channel_id, hold_type, reason, duration_days, active, approved_by, expires_at

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

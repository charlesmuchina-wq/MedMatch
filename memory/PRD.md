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
10. **Content Moderation**: Professional environment filtering with auto-profanity filter
11. **Multi-jurisdiction Privacy Compliance**: HIPAA, GDPR, PIPL, APPI, UK DPA, Australian Privacy Act

## Architecture
```
/app/
├── backend/
│   ├── routes/
│   │   ├── auth.py                       # Auth + Google SSO + Microsoft placeholder
│   │   ├── lumi_messenger.py             # Core: channels, DMs, presence, profile, edit/delete, calls, notif hub, retention, org-settings, audit log, moderation, compliance, calendar sync
│   │   ├── lumi_ai_routes.py             # AI: sentiment, tasks, reports, translation
│   │   ├── futuristic_ai_routes.py       # AI: ask, anomalies, decision cards
│   │   ├── knowledge_graph_routes.py     # Knowledge graph, impact analysis
│   │   └── advanced_collaboration_routes.py  # Simulations, bottlenecks, notifications
│   └── server.py
└── frontend/
    └── src/
        ├── components/Lumi/              # 23 extracted components
        │   ├── RetentionPanel.jsx        # Retention with approval workflow, org settings, tabs
        │   ├── UserProfileModal.jsx      # Profile with theme picker, capabilities, subscriptions
        │   ├── MessageBubble.jsx         # + edit/delete, profile pics, (edited) label
        │   ├── NotificationsPanel.jsx    # Centralized hub with source tabs
        │   ├── EmojiPicker.jsx           # Native emoji picker with categories, search, recents
        │   ├── KeyboardShortcuts.jsx     # Shortcuts panel + useKeyboardShortcuts hook
        │   ├── AdminAuditPanel.jsx       # Admin audit log viewer with search & filters
        │   ├── CompliancePanel.jsx       # Multi-jurisdiction compliance dashboard
        │   └── ... (15 more components)
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

### Message Retention & Privacy
- **Global 90-day auto-delete**: Automatic for all channels (not per-channel)
- **Hold Approval Workflow**: Holds require IT admin + manager approval
- **Organization Admin Settings**: IT admin, manager contacts, department, compliance officer
- **Hold Request System**: Submit → Pending → Approve/Reject → Active hold
- **Legal Hold**: Indefinite preservation until released
- **Contractual Hold**: Custom duration with expiration date
- **Hold Release**: Admins can release active holds

### New Features (Current Session - March 5, 2026)
- **Emoji Picker**: Native picker with 9 categories, search, recent emojis. Integrated into chat input with Smile icon. Keyboard shortcut: Ctrl+E
- **Keyboard Shortcuts**: Full shortcut system with useKeyboardShortcuts hook. Shortcuts panel accessible via sidebar button or Ctrl+/. Covers navigation, messaging, and panel toggles
- **Admin Audit Log**: Comprehensive audit trail for all admin actions (hold requests, approvals, moderation settings, compliance changes). Searchable with category filters
- **Google Calendar Status Sync**: Auto-syncs every 5 minutes for Google SSO users. Updates presence based on calendar events
- **Content Moderation**: Professional environment filter. Auto-filters profanity from messages. Configurable settings (enable/disable, auto-filter, block, notify admin). Moderation log for incident tracking
- **Multi-jurisdiction Compliance Framework**: 
  - HIPAA (US) - PHI protection, audit trails, access controls
  - GDPR (EU) - Data minimization, right to erasure, consent management
  - UK DPA 2018 - ICO registration, SAR process
  - Australian Privacy Act + APPs - NDB scheme, security measures
  - China PIPL - Data localization, cross-border assessment
  - Japan APPI - Purpose limitation, PPC oversight
  - AI KARAU compliance reference integration
  - 92% compliance score with 10 platform security controls

## Prioritized Backlog

### P0 - Next
- Finalize Microsoft SSO Integration (user has no Azure credentials yet)
- Visualizations: Data/activity charts, interactive project graphs/timelines, knowledge graph visualization

### P1
- User Status Sync from Microsoft calendars (after MS SSO)

### P2 - Future
- Full Knowledge Graph Integration (MS Project/SharePoint via Graph API)
- End-to-End Encryption (E2EE) for messages and files

### P3 - Backlog
- Live Payment Gateway (Stripe test → production keys)

## Key API Endpoints
- `GET /api/lumi/admin/retention` - Retention overview
- `GET/PUT /api/lumi/admin/org-settings` - IT admin and manager contacts
- `POST /api/lumi/admin/hold` - Submit hold request
- `PUT /api/lumi/admin/hold-requests/{id}` - Approve/reject hold request
- `DELETE /api/lumi/admin/hold/{id}` - Release active hold
- `GET /api/lumi/admin/audit-log` - Audit log with category filtering
- `POST /api/lumi/moderation/check` - Content moderation check
- `GET/PUT /api/lumi/moderation/settings` - Moderation settings
- `GET /api/lumi/moderation/log` - Moderation incident log
- `GET /api/lumi/compliance/frameworks` - Compliance frameworks
- `GET /api/lumi/compliance/status` - Compliance posture
- `PUT /api/lumi/compliance/frameworks` - Enable/disable frameworks
- `POST /api/lumi/calendar/sync` - Google Calendar status sync
- `GET /api/lumi/calendar/status` - Calendar sync status
- `GET/PUT /api/lumi/profile/theme` - User accent color

## DB Collections
- `lumi_org_settings`: key="admin_config", IT admin/manager contacts
- `lumi_hold_requests`: Hold request approval workflow
- `lumi_holds`: Active holds with expiration
- `lumi_audit_log`: Admin action audit trail
- `lumi_moderation_settings`: Content moderation configuration
- `lumi_moderation_log`: Moderation incident records
- `lumi_compliance_config`: Enabled compliance frameworks

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

## Known Issues
- WebSocket connection returns 403 (non-blocking, affects real-time updates)

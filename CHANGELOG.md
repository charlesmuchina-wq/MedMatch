# CHANGELOG

## March 12, 2026 — Complete Feature Implementation

### Automatic Bot Chain Triggers
- "After Meeting" trigger: chains auto-run when meetings convert to channels
- "On Message" trigger: chains auto-run every 10th message in a channel
- Integrated into meeting_channel_sync.py and lumi_messenger.py

### Meeting Replay AI Chapters + Transcript Search
- POST /api/karau/replay/{id}/generate-chapters — GPT-4o generates 4-8 chapters
- GET /api/karau/replay/{id}/search?q=term — searches transcript segments
- Frontend: search bar + AI chapter generation button in replay sidebar

### ML Channel Predictions
- GET /api/lumi/behavior/predict-channels — predicts which channels user visits next
- Uses 7-day message frequency + recency scoring
- Returns time-of-day context (morning/afternoon/evening/night)

### Mobile Bottom Navigation
- New MobileBottomNav component (< 768px)
- Tabs: Channels, DMs, Search, AI, Me
- Portal dock hidden on mobile to prevent z-index conflict

### Push Notifications Configured
- VAPID keys generated and stored in backend .env
- pywebpush ready for real push subscriptions

### Passkeys/WebAuthn Configured
- WEBAUTHN_RP_ID set to preview domain
- Backend biometric.py has full challenge/response flow (589 lines)

### Phase 1 Refactoring (earlier today)
- EnziChatView.jsx extracted from LumiMessenger (804→693 lines)
- AiSummaryWidget + KarauAnalyticsRow extracted from KarauMeetDashboard (998→755 lines)
- GitHub SSO labeled "(Demo)"

### Phase 2-3 Bot Features (earlier today)
- Bot-to-Bot chaining with BotChainBuilder UI
- Workflows tab in Channel Tools modal
- 18 AI-powered bots with real GPT-4o responses

## March 11, 2026 — Bot Marketplace + Domain Routing
- 18 bots across 4 categories with AI responses
- Slash commands + autocomplete
- Domain-aware multi-subdomain routing
- Meeting-to-channel admin approval
- LumiMessenger initial refactor

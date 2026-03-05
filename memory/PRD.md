# AI KARAU + LUMI - Product Requirements Document

## Original Problem Statement
Build a dual-platform communication suite: "AI KARAU" (webinar tool) and "LUMI" (professional-grade messenger). LUMI is the primary focus — a futuristic, AI-driven "Actionable Intelligence" hub for project productivity and internal communication.

## Core Requirements
1. **Foundation:** Secure, compliant messenger with chat, DMs, file sharing, reactions, presence
2. **UI/UX:** Highly accessible, readable UI with user-selectable profile themes (pink, turquoise, deep red accents)
3. **Productivity AI:** Meeting summaries, action items, sentiment analysis, status reporting
4. **Futuristic AI:** Conversational data querying, anomaly alerts, decision cards, knowledge graph, bottleneck detection, what-if simulations, real-time translation
5. **Integrations:** Google SSO (done), Microsoft SSO (placeholder), MS Graph API
6. **Core Features:** Threading, edit/delete, voice/video, retention policies, emoji reactions, keyboard shortcuts
7. **Admin:** Audit logging for all administrative actions
8. **Compliance:** HIPAA, GDPR, PIPL, APPI, UK data laws content filtering

## What's Been Implemented
- Full LUMI messenger with channels, DMs, WebSocket real-time messaging
- Google SSO authentication
- Microsoft SSO placeholder (awaiting API keys)
- Emoji picker, keyboard shortcuts panel, admin audit logs
- Google Calendar status sync
- Content moderation system (profanity filter)
- Compliance framework panel with HIPAA/GDPR/PIPL/APPI/UK DPA coverage
- Message retention & holds system (legal, contractual holds with approval workflow)
- Data visualizations panel (KPI charts, project timeline, knowledge graph)
- Reusable LumiBrand component with inline SVG icon, shared footer
- Dark/Light mode toggle in LUMI sidebar
- **P0 Accessibility Fix (March 5, 2026):** Fixed critical dark mode CSS specificity bug — removed global `.dark h1-h6, .dark p/span/label` color overrides from index.css that were overriding Tailwind utility classes
- **Icon Visibility Fix (March 5, 2026):** Replaced invisible dark PNG bubble icon with bright inline SVG chat bubble using turquoise→purple→pink gradient. Removed dark PNG logo from Portal Selector LUMI card.

## Architecture
- Frontend: React + Tailwind + Shadcn/UI
- Backend: FastAPI + MongoDB
- Real-time: WebSocket at /api/lumi/ws/{user_id}
- Charts: Recharts library

## Pending / Backlog
- **P0:** Microsoft SSO finalization (blocked on Azure API keys)
- **P1:** Microsoft Calendar status sync
- **P2:** Full Knowledge Graph + MS Project/SharePoint integration
- **P2:** End-to-End Encryption (E2EE)
- **P2:** Stripe live payment transition
- **P3:** Legacy admin user display fix (role vs auth_method)

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test: test@medmatch.io / TestPassword123!

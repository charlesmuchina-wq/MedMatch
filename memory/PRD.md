# MedMatch-AI KARAU Platform - Product Requirements Document

## Original Problem Statement
Build "AI KARAU," a sophisticated AI-powered video meeting portal, and MedMatch Job Toolkit for Life Sciences & Engineering talent.

## Core Products
1. **AI KARAU Meeting Portal** - Enterprise video conferencing with AI features
2. **MedMatch Job Toolkit** - Hiring platform with Talent CRM, AI scoring, offer management

## Implemented Features

### AI KARAU Portal
- Real-time video meetings with WebRTC
- AI Meeting Notes with PDF export (reportlab)
- Full AI Meeting Assistant - Real LLM integration (GPT-4o-mini) for Q&A, action items, summaries
- Floating KARAU AI Avatar - App-wide chatbot at bottom-right (React Portal)
- Real-time Dashboard Analytics - Stats from MongoDB + Activity Feed
- **Upcoming Meetings** - Shows waiting/scheduled meetings with quick Start buttons
- **AI Trending Topics** - Extracts discussion topics from recent meetings using GPT-4o-mini
- Real-time caption translation (16+ languages)
- Industry-specific meeting templates
- CRM webhook integration
- Collaborative whiteboard, polls, reactions, noise cancellation, recordings, semantic search

### Dashboard Layout
- Single-page horizontal bento grid (no scrolling)
- Row 1: Welcome + New Meeting button
- Row 2: Start Meeting | Join Meeting | Stats (198 meetings, 6 AI insights, 173 participants)
- Row 3: Upcoming Meetings (5 with Start buttons) | Trending Topics (5 AI-extracted)
- Row 4: Feature badges (smaller) + Active count
- Row 5: Collapsible Highlights + Recent Meetings (both hidden by default)
- Sidebar: 6 nav items, w-52/w-14, auto-collapse mobile
- Purple/Blue/Green color scheme (60-30-10 rule)

## Key API Endpoints
- GET /api/karau-meet/stats - Real stats from MongoDB
- GET /api/karau-meet/activity-feed - Live activity feed
- GET /api/karau-meet/upcoming - Upcoming scheduled meetings
- GET /api/karau-meet/trending-topics - AI-extracted trending topics
- POST /api/karau-features/ai-assistant/ask - AI Q&A
- POST /api/karau-features/ai-assistant/generate-summary/{id} - Meeting summary
- GET /api/karau-features/ai-assistant/insights/{id} - Meeting insights

## P1 Backlog
- Enhanced noise cancellation (rnnoise-wasm)
- Semantic search improvements
- Dashboard stats auto-refresh (polling)

## P2 Backlog
- Payment gateway config (Stripe/PayPal - needs API keys)
- Production email OTP (Resend)
- Mobile app optimization

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test: test@medmatch.io / TestPassword123!

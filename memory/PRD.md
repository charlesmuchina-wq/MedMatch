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
- Real-time Dashboard Analytics - Stats from MongoDB + Live Meeting Pulse
- Real-time caption translation (16+ languages)
- Industry-specific meeting templates
- CRM webhook integration
- Collaborative whiteboard, polls, reactions
- Noise cancellation hook, recordings, semantic search

### Dashboard & UI (Current)
- Single-page horizontal layout, no scrolling required
- **Collapsible Highlights** - Only AI insights & meeting starts, hidden by default
- **Collapsible Recent Meetings** - Compact list, hidden by default
- Sidebar: 6 nav items, w-52 expanded / w-14 collapsed, auto-collapse on mobile
- Purple/Blue/Green color scheme (60-30-10 rule)
- Real stats from MongoDB (meetings, hours, AI insights, participants)
- Premium dark theme, IBM Plex Sans font

## Architecture
- Frontend: React + Tailwind CSS + Shadcn/UI
- Backend: FastAPI + MongoDB
- AI: Emergent LLM Key (GPT-4o-mini via emergentintegrations)
- Auth: JWT-based

## Key API Endpoints
- GET /api/karau-meet/stats - Real dashboard stats from MongoDB
- GET /api/karau-meet/activity-feed - Live activity feed
- POST /api/karau-features/ai-assistant/ask - AI Q&A with follow-up suggestions
- POST /api/karau-features/ai-assistant/generate-summary/{id} - Meeting summary
- GET /api/karau-features/ai-assistant/insights/{id} - Meeting insights

## P0 Backlog
- Trending Topics - AI-powered extraction from recent meetings

## P1 Backlog
- Enhanced noise cancellation (rnnoise-wasm)
- Semantic search improvements

## P2 Backlog
- Payment gateway config (Stripe/PayPal - needs API keys)
- Production email OTP (Resend)
- Mobile optimization

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test: test@medmatch.io / TestPassword123!

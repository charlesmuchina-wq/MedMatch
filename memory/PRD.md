# MedMatch-AI KARAU Platform PRD

## Original Problem Statement
Build "MedMatch," an AI-powered Life Sciences & Engineering Talent Ecosystem, combined with "AI KARAU," a sophisticated video meeting portal.

## Core Products
1. **AI KARAU Portal** - Video meeting solution with real-time transcription, AI summaries, collaborative whiteboard, polls, reactions, DEI analytics
2. **MedMatch Job Toolkit** - Comprehensive hiring platform with Talent CRM, AI Job Description Generator, AI Candidate Scoring, Offer Management, Advanced Reporting

## Architecture
- **Frontend**: React (port 3000) with Tailwind CSS + shadcn/ui
- **Backend**: FastAPI (port 8001) with MongoDB
- **Real-time**: WebSockets for whiteboard collaboration and meeting signaling
- **Auth**: Cookie-based session management + KARAU separate auth

## What's Been Implemented

### AI KARAU Meeting Room - REDESIGNED (Feb 27, 2026)
- **Minimal header**: Title + E2E badge + share/copy buttons only
- **Full-width video area** as the central focus
- **Single unified bottom control bar** (Teams-style): Audio | Video | Screen Share | Record | Hand Raise | Chat | People | AI Notes | More (...) | Leave
- **Smooth sliding side panel** from right (flex-based, 300ms transition)
- **"More" dropdown menu**: Polls, Captions, Virtual Background, Whiteboard, Breakout Rooms, Add to Calendar, Settings
- **Mobile bottom sheet** for panels on small screens
- **Fixed pre-existing bug**: `effectiveUserId` ReferenceError in active speaker detection
- **Fixed duplicate panel headers**: Hidden internal panel headers in MeetingPanels.jsx, moved Mute All button to panel footer

### Previously Completed Features
- Talent CRM with Kanban view (react-beautiful-dnd)
- Advanced Reporting with PDF/CSV export (reportlab)
- Offer Management with approval workflow
- Real-time Collaborative Whiteboard (WebSocket-based)
- Enhanced Platform Settings (HRIS, Background Checks, Compliance)
- One-Click Apply, Team Collaboration & Outreach
- Mobile Responsiveness across entire platform
- Onboarding Wizard
- Semantic Search (AI-powered, full backend + frontend at /semantic-search)
- Noise Cancellation hook (Web Audio API chain - not integrated into meeting room audio pipeline, browser noiseSuppression active)

## Test Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test User: test@medmatch.io / TestPassword123!

## Key Files
- `/app/frontend/src/components/KarauMeet/MeetingRoom.jsx` - Redesigned meeting room
- `/app/frontend/src/components/KarauMeet/MeetingPanels.jsx` - Updated panel components
- `/app/frontend/src/pages/SemanticSearchPage.jsx` - Semantic search UI
- `/app/frontend/src/components/KarauMeet/useNoiseCancellation.js` - Noise cancellation hook

## Backlog
- **P2**: Integrate useNoiseCancellation hook into meeting room audio pipeline
- **P3**: Payment Gateway Configuration (Stripe/PayPal - needs API keys from user)
- **P3**: Production email OTP (Resend - needs API key)

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
- **"More" dropdown menu**: Polls, Captions, Virtual Background, Noise Cancellation, Whiteboard, Breakout Rooms, Add to Calendar, Settings
- **Mobile bottom sheet** for panels on small screens
- **Fixed pre-existing bug**: `effectiveUserId` ReferenceError in active speaker detection
- **Fixed duplicate panel headers**: Hidden internal panel headers, moved Mute All to panel footer

### Noise Cancellation Integration (Feb 28, 2026)
- **useNoiseCancellation hook** wired into meeting room audio pipeline
- **Auto-applies** on meeting start when noise_cancellation setting is enabled
- **Toggle** available in More (...) menu with Volume2 icon showing On/Off state
- **Filter chain**: High-pass (85Hz) -> Notch (60Hz hum) -> Low-pass (14kHz) -> DynamicsCompressor
- **Peer connection update**: toggleing NC updates audio tracks in all peer connections

### Enhanced Semantic Search (Feb 28, 2026)
- **Search history**: Persists in localStorage (max 8 entries), shows query, hit count, time ago
- **Example queries**: 6 pre-defined queries for life sciences roles, clickable to search
- **Enhanced result cards**: Ranking number, matched skills highlighted in turquoise, location display
- **AI criteria display**: Shows extracted skills, experience level, domain badges from AI parsing
- **Clear history** button to reset search history

### Enhanced Meeting Reactions (Feb 28, 2026)
- **Varied floating animations**: Each emoji gets random drift, rotation, size, and duration
- **Burst particles**: Celebration (party) and fire emojis trigger 6 radial burst particles
- **Improved reaction bar**: Rounded design with hover scale effects
- **Button style**: Matches redesigned control bar aesthetic (rounded-xl)

### Previously Completed Features
- Talent CRM with Kanban view (react-beautiful-dnd)
- Advanced Reporting with PDF/CSV export (reportlab)
- Offer Management with approval workflow
- Real-time Collaborative Whiteboard (WebSocket-based)
- Enhanced Platform Settings (HRIS, Background Checks, Compliance)
- One-Click Apply, Team Collaboration & Outreach
- Mobile Responsiveness across entire platform
- Onboarding Wizard

## Test Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test User: test@medmatch.io / TestPassword123!

## Key Files
- `/app/frontend/src/components/KarauMeet/MeetingRoom.jsx` - Meeting room with NC integration
- `/app/frontend/src/components/KarauMeet/MeetingPanels.jsx` - Panel components
- `/app/frontend/src/components/KarauMeet/useNoiseCancellation.js` - Web Audio API noise hook
- `/app/frontend/src/components/KarauMeet/MeetingReactions.jsx` - Enhanced reactions with burst
- `/app/frontend/src/pages/SemanticSearchPage.jsx` - Enhanced semantic search UI

## Backlog
- **P3**: Payment Gateway Configuration (Stripe/PayPal - needs API keys from user)
- **P3**: Production email OTP (Resend - needs API key)

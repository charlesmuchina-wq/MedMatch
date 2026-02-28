# MedMatch-AI KARAU Platform - Product Requirements Document

## Original Problem Statement
Build "AI KARAU," a sophisticated AI-powered video meeting portal, and MedMatch Job Toolkit for Life Sciences & Engineering talent.

## Core Products
1. **AI KARAU Meeting Portal** - Enterprise video conferencing with AI features
2. **MedMatch Job Toolkit** - Hiring platform with Talent CRM, AI scoring, offer management

## User Personas
- Enterprise meeting hosts and participants
- Life Sciences/Engineering recruiters and hiring managers
- Admin/org managers

## Implemented Features

### AI KARAU Portal
- Real-time video meetings with WebRTC
- AI Meeting Notes with PDF export (reportlab)
- **Full AI Meeting Assistant** - Real LLM integration (Emergent Key + GPT-4o-mini) for Q&A, action items, summaries, smart suggestions
- **Floating KARAU AI Avatar** - App-wide chatbot at bottom-right (React Portal)
- Real-time caption translation (16+ languages)
- Industry-specific meeting templates (6 templates)
- CRM webhook integration (generic webhooks)
- Collaborative whiteboard, polls, reactions
- Noise cancellation hook
- Meeting recordings
- Semantic search

### Dashboard & UI
- **Single-page horizontal layout** - No scrolling, bento grid
- **Collapsible Recent Meetings** - Collapsed by default
- **Purple/Blue/Green color scheme** - 60-30-10 rule with gradients
- Premium dark theme with custom font (IBM Plex Sans)
- Responsive design (desktop + mobile)

### MedMatch Toolkit
- Talent CRM (Kanban)
- AI Job Description Generator
- AI Candidate Scoring
- Offer Management
- Advanced Reporting (PDF/CSV export)

## Architecture
- Frontend: React + Tailwind CSS + Shadcn/UI
- Backend: FastAPI + MongoDB
- AI: Emergent LLM Key (GPT-4o-mini via emergentintegrations)
- Auth: JWT-based

## Color Palette (Current)
- 60% Blue: `#0a0e1a` (bg), `#3b82f6` (accents)
- 30% Purple: `#6c3ce0` (secondary), `#8b5cf6` (bright)
- 10% Green: `#10b981` (CTAs, success)

## P0 Backlog
- None currently

## P1 Backlog
- Dashboard stats from real API (currently hardcoded)
- Enhanced noise cancellation with rnnoise-wasm
- Semantic search improvements

## P2 Backlog
- Payment gateway configuration (Stripe/PayPal - needs API keys)
- Production email OTP (Resend)
- Mobile app optimization

## Credentials
- Admin: admin@medmatch.com / Swampdrainer2026!
- Test: test@medmatch.io / TestPassword123!

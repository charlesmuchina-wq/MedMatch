# MedMatch - Remote Job Finder PRD

## Original Problem Statement
Create an app that uses a resume to find remote jobs that fit the user's profile.

## User Personas
- **Primary**: Job seekers looking for remote positions
- **Use Case**: Quality Assurance / Regulatory Compliance professionals in medical device industry (e.g., Charles Muchina)

## Core Requirements
- Resume upload and AI-powered parsing
- Job search from multiple free APIs
- AI-powered job matching with match scores
- Save/bookmark jobs
- Track application status
- Email alerts for new matching jobs
- Filters for date posted, location, source

## Architecture
- **Backend**: FastAPI + MongoDB
- **Frontend**: React + Tailwind CSS + Shadcn UI
- **AI**: OpenAI GPT-5.2 via Emergent integrations
- **Job APIs**: RemoteOK, Remotive, Jobicy, Arbeitnow, Himalayas (5 free APIs)
- **Email**: Gmail SMTP

## What's Been Implemented

### Phase 1 (Jan 12, 2026)
- [x] Resume PDF upload with AI parsing (GPT-5.2)
- [x] Skills extraction (37+ skills from resume)
- [x] Dashboard with stats
- [x] Job search from 2 APIs (RemoteOK, Remotive)
- [x] AI job matching with match scores
- [x] Save/bookmark jobs
- [x] Application tracking

### Phase 2 (Jan 12, 2026)
- [x] Email alerts via Gmail SMTP
- [x] Date posted filter (24h, 3d, 7d, 14d, 30d)
- [x] Location filter (USA, Europe, UK, Canada, Germany, Remote)
- [x] Quick search presets for Supplier Quality Manager/Director
- [x] AI-enhanced search with related job suggestions
- [x] Added 3 more job sources (Jobicy, Arbeitnow, Himalayas)
- [x] Job alerts page with send now feature

## Test Results
- Backend: 100% (19/19 tests passed)
- Frontend: 95% functional
- New Features: 100% working
- Overall: 98%

## Prioritized Backlog

### P0 (Critical) - DONE
- Resume upload ✓
- Job search ✓
- Application tracking ✓
- Email alerts ✓
- Filters ✓

### P1 (Important)
- Scheduled email alerts (daily/weekly digest)
- Cover letter generator using AI
- Interview preparation tips

### P2 (Nice to Have)
- Multiple resume profiles
- LinkedIn job integration
- Salary comparison tool
- Job market trends dashboard

## Next Tasks
1. Add scheduled email alerts (daily/weekly)
2. Implement cover letter generator
3. Add more job sources (Adzuna, etc.)

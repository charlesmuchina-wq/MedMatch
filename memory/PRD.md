# MedMatch - Remote Job Finder PRD

## Original Problem Statement
Create an app that uses a resume to find remote jobs that fit the user's profile.

## User Personas
- **Primary**: Job seekers looking for remote positions
- **Use Case**: Quality Assurance / Regulatory Compliance professionals in medical device industry

## Core Requirements
- Resume upload and AI-powered parsing
- Job search from free APIs (RemoteOK, Remotive)
- AI-powered job matching with match scores
- Save/bookmark jobs
- Track application status

## Architecture
- **Backend**: FastAPI + MongoDB
- **Frontend**: React + Tailwind CSS + Shadcn UI
- **AI**: OpenAI GPT-5.2 via Emergent integrations
- **Job APIs**: RemoteOK, Remotive (free public APIs)

## What's Been Implemented (Jan 12, 2026)
- [x] Resume PDF upload with AI parsing (GPT-5.2)
- [x] Skills extraction (37+ skills from resume)
- [x] Dashboard with stats (saved jobs, applications, interviews, skills)
- [x] Job search from RemoteOK & Remotive APIs
- [x] AI job matching with match scores and analysis
- [x] Save/bookmark jobs functionality
- [x] Application tracking (Applied, Interview, Offer, Rejected)
- [x] Full CRUD for applications
- [x] Responsive design with sidebar navigation

## Test Results
- Backend: 100% (12/12 tests passed)
- Frontend: 100% functional
- Integration: 100% (AI, APIs, database working)

## Prioritized Backlog

### P0 (Critical) - DONE
- Resume upload ✓
- Job search ✓
- Application tracking ✓

### P1 (Important)
- Job filters by salary range, experience level
- Resume editing (add/remove skills manually)
- Email notifications for saved job updates

### P2 (Nice to Have)
- Multiple resume profiles
- Cover letter generator
- Interview preparation tips
- Job alerts scheduling

## Next Tasks
1. Add salary range filter to job search
2. Implement manual skill editing on resume page
3. Add job category filter (Engineering, QA, Management)

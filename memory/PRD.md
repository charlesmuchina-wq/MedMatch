# MedMatch - AI-Powered Remote Job Finder PRD

## Original Problem Statement
Create an app that uses a resume to find remote jobs that fit the user's profile, with focus on Quality, Medical Device, and Manufacturing roles.

## User Personas
- **Primary**: Charles Muchina - Quality Assurance/Supplier Quality professional in medical device industry
- **Target**: Job seekers in regulated industries (medical devices, pharma, manufacturing)

## Core Requirements (All Implemented ✅)
1. Resume upload and AI-powered parsing
2. Job search from multiple sources
3. AI-powered job matching with match scores
4. Save/bookmark jobs
5. Track application status
6. Email alerts for new matching jobs
7. Filters for date posted, location, source
8. Advanced filters for industries and technologies

## Architecture
- **Backend**: FastAPI + MongoDB + JobSpy
- **Frontend**: React + Tailwind CSS + Shadcn UI
- **AI**: OpenAI GPT-5.2 via Emergent integrations
- **Job Sources**: 
  - JobSpy: LinkedIn, Indeed, Glassdoor, Google Jobs, ZipRecruiter
  - Free APIs: RemoteOK, Remotive, Jobicy, Arbeitnow, Himalayas
- **Email**: Gmail SMTP

## What's Been Implemented

### Phase 1 - MVP (Jan 12, 2026)
- [x] Resume PDF upload with AI parsing (GPT-5.2)
- [x] Skills extraction (37+ skills)
- [x] Dashboard with stats
- [x] Job search from 2 APIs
- [x] AI job matching with match scores
- [x] Save/bookmark jobs
- [x] Application tracking

### Phase 2 - Filters & Alerts (Jan 12, 2026)
- [x] Email alerts via Gmail SMTP
- [x] Date posted filter (24h, 3d, 7d, 14d, 30d)
- [x] Location filter (USA, Europe, UK, Canada, Germany, Remote)
- [x] Quick search presets for Quality roles
- [x] Added 3 more job sources

### Phase 3 - TheirStack + JobSpy Integration (Jan 12, 2026)
- [x] JobSpy integration (LinkedIn, Indeed, Glassdoor, Google, ZipRecruiter)
- [x] TheirStack-inspired advanced filters
- [x] Industry tags: Medical Devices, Pharmaceutical, Healthcare, Biotechnology, Manufacturing
- [x] Technology tags: ISO 13485, ISO 9001, FDA 21 CFR 820, EU MDR
- [x] AI Deep Search with GPT-5.2 generated queries
- [x] 10 quick search presets for Quality/Medical Device roles
- [x] Relevance scoring for jobs
- [x] 9 total job sources

## Test Results
- Backend: 89% (17/19 tests)
- Frontend: 100%
- Integration: 100%
- Overall: 95%

## Job Sources (9 Total)
1. LinkedIn (via JobSpy)
2. Indeed (via JobSpy)
3. Glassdoor (via JobSpy)
4. Google Jobs (via JobSpy)
5. ZipRecruiter (via JobSpy)
6. RemoteOK (Free API)
7. Remotive (Free API)
8. Jobicy (Free API)
9. Arbeitnow (Free API)
10. Himalayas (Free API)

## Quick Search Presets
1. Supplier Quality Manager
2. Supplier Quality Director
3. Quality Manager
4. Quality Director
5. Lead Auditor
6. Medical Device
7. Manufacturing Quality
8. Regulatory Compliance
9. ISO Auditor
10. FDA Compliance

## Prioritized Backlog

### P0 (Critical) - DONE ✅
- Resume upload ✅
- Job search (9 sources) ✅
- AI Deep Search ✅
- Application tracking ✅
- Email alerts ✅
- Advanced filters ✅

### P1 (Important)
- Scheduled daily/weekly email digests
- Cover letter generator using AI
- Job deduplication improvements

### P2 (Nice to Have)
- Multiple resume profiles
- Salary comparison tool
- Job market trends dashboard
- Interview preparation tips

## Configuration
- Gmail: charles.muchina@gmail.com
- Alert Recipient: cmuchina@outlook.com

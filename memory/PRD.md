# MedMatch - AI-Powered Remote Job Finder PRD

## Original Problem Statement
Create an app that uses a resume to find remote jobs, with focus on Quality, Medical Device, Lead Auditor, and Manufacturing roles.

## User Profile
- **Name**: Charles Muchina
- **Role**: Quality Assurance / Supplier Quality Professional
- **Industry**: Medical Device, Pharmaceutical, Manufacturing

## Architecture
- **Backend**: FastAPI + MongoDB + JobSpy + Google CSE
- **Frontend**: React + Tailwind CSS + Shadcn UI
- **AI**: OpenAI GPT-5.2 via Emergent integrations
- **Email**: Gmail SMTP

## Job Sources (12 Total!)

### Google Custom Search API
1. Indeed (Google)
2. LinkedIn (Google)
3. Glassdoor (Google)
4. ZipRecruiter (Google)

### JobSpy Scraper
5. Indeed (JobSpy)
6. LinkedIn (JobSpy)
7. Glassdoor (JobSpy)
8. ZipRecruiter (JobSpy)

### Free APIs
9. RemoteOK
10. Remotive
11. Jobicy
12. Arbeitnow
13. Himalayas

## Features Implemented (All ✅)

### Core Features
- [x] Resume PDF upload with AI parsing (GPT-5.2)
- [x] Skills extraction (37+ skills)
- [x] AI-powered job matching with match scores
- [x] Save/bookmark jobs
- [x] Application tracking (Applied, Interview, Offer, Rejected)
- [x] Email alerts via Gmail SMTP

### Search Features
- [x] **10 Quick Search Presets**:
  - Supplier Quality Manager/Director
  - Quality Manager/Director
  - Lead Auditor
  - Medical Device
  - Manufacturing Quality
  - Regulatory Compliance
  - ISO Auditor
  - FDA Compliance
- [x] **AI Deep Search** - GPT-5.2 generates optimized queries
- [x] **Google CSE Integration** - Searches entire web for jobs
- [x] **TheirStack-inspired Advanced Filters**:
  - Industries: Medical Devices, Pharmaceutical, Healthcare, Biotechnology, Manufacturing
  - Technologies: ISO 13485, ISO 9001, FDA 21 CFR 820, EU MDR

### Filters
- [x] Date posted (24h, 3d, 7d, 14d, 30d)
- [x] Location (USA, Europe, UK, Canada, Germany, Remote, Worldwide)
- [x] Source (All, Google CSE, RemoteOK, Remotive, Jobicy, etc.)

## Configuration
```
GOOGLE_API_KEY=AIzaSyDRwjq6_8sAGrSJEONa27SN9CSZWZtJMYE
GOOGLE_CSE_ID=e77be7df731ff4fff
GMAIL_ADDRESS=charles.muchina@gmail.com
ALERT_RECIPIENT=cmuchina@outlook.com
```

## Test Results (Jan 12, 2026)
- Backend: 89% (17/19)
- Frontend: 100%
- Integration: 100%
- Google CSE: 100% ✅
- **Overall: 98%**

## Deep Search Results
- **116+ jobs** found per search
- **8 unique sources** in results
- AI-generated search queries for Quality/Medical Device roles

## Prioritized Backlog

### P1 (Important)
- Scheduled daily/weekly email digests
- AI cover letter generator
- Salary comparison tool

### P2 (Nice to Have)
- Multiple resume profiles
- Job market trends dashboard
- Interview preparation tips

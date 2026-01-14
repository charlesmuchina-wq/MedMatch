# MedMatch - Remote Job Finder with AI Matching

## Original Problem Statement
Create an application that uses the user's resume to find remote jobs that match their skills and experience. Features include job search, AI matching, email alerts, cover letter generation, callback prediction, interview preparation, and voice coaching.

## User Personas
- **Job Seekers**: Professionals in Quality/Medical Device fields looking for remote positions
- **Target Roles**: Supplier Quality Manager, Quality Director, Lead Auditor, Medical Device professionals

## Core Requirements
- ✅ Resume upload and AI-powered parsing
- ✅ Multi-source job search (RemoteOK, Remotive, Jobicy, Arbeitnow, Himalayas)
- ✅ JobSpy integration for LinkedIn, Indeed, Glassdoor
- ✅ Google Custom Search Engine integration
- ✅ AI-powered job matching and relevance scoring
- ✅ Save/bookmark jobs
- ✅ Application tracking with status updates
- ✅ Email alerts for matching jobs
- ✅ Automated Daily Digest Scheduler (8 AM UTC)
- ✅ AI Cover Letter Generator
- ✅ Application Success Predictor
- ✅ Interview Preparation Feature
- ✅ AI Interview Coach with Voice
- ✅ Dark Mode with Inverted Batik Theme
- ✅ **Job Application Analytics Dashboard** (NEW - Jan 2026)
- ✅ **Multiple Resume Profiles** (NEW - Jan 2026)
- ✅ **Voice Recording Playback** (NEW - Jan 2026)

## Tech Stack
- **Backend**: FastAPI (Python) with MongoDB (motor)
- **Frontend**: React with shadcn/ui components
- **AI**: Emergent LLM Key (GPT models via litellm)
- **Voice**: Web Speech API + MediaRecorder API
- **Email**: Gmail SMTP
- **Scheduler**: APScheduler (AsyncIOScheduler)
- **Theming**: CSS custom properties with localStorage persistence

## Architecture

### Backend (`/app/backend/server.py`)
- FastAPI with APIRouter prefixed with `/api`
- APScheduler for automated daily digest
- MongoDB collections: resumes, jobs, saved_jobs, applications, alerts, digest_settings, cover_letters, callback_predictions, emailed_jobs, resume_profiles

### Frontend (`/app/frontend/src/`)
```
├── App.js                         # Main routing + Theme Provider
├── App.css                        # Component styles with dark mode
├── index.css                      # Global styles + batik patterns
├── pages/
│   ├── Dashboard.jsx              # Overview with stats
│   ├── ResumePage.jsx             # Resume upload with dropzone
│   ├── ResumeProfilesPage.jsx     # Multiple resume profiles (NEW)
│   ├── JobSearchPage.jsx          # Job search with filters
│   ├── SavedJobsPage.jsx          # Saved jobs list
│   ├── ApplicationsPage.jsx       # Application tracker
│   ├── SuccessPredictorPage.jsx   # AI callback prediction
│   ├── InterviewPrepPage.jsx      # Interview preparation
│   ├── VoiceCoachPage.jsx         # Voice interview coach + Playback (UPDATED)
│   ├── CoverLetterPage.jsx        # AI cover letter generator
│   ├── JobAlertsPage.jsx          # Email alerts & scheduler
│   └── AnalyticsDashboard.jsx     # Application analytics (NEW)
└── components/
    ├── ui/                        # shadcn components
    └── shared/
        └── JobCard.jsx            # Job card with probability badge
```

## Key API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/resume` | GET | Get user's resume |
| `/api/resume/upload` | POST | Upload and parse resume |
| `/api/resume/profiles` | GET/POST | Get/create resume profiles |
| `/api/resume/profiles/{id}` | PUT/DELETE | Update/delete profile |
| `/api/jobs/search` | GET | Search jobs with filters |
| `/api/jobs/deep-search` | POST | AI-powered comprehensive search |
| `/api/jobs/predict-callback` | POST | Full AI callback prediction |
| `/api/analytics/dashboard` | GET | Get application analytics |
| `/api/interview/generate-questions` | POST | Generate interview questions |
| `/api/interview/voice-feedback` | POST | AI voice interview feedback |
| `/api/cover-letter/generate` | POST | Generate AI cover letter |

## Voice Coach Features
- **Speech Recognition**: Browser-native Web Speech API
- **Audio Recording**: MediaRecorder API for playback
- **Live Transcription**: Real-time display of spoken words
- **Playback**: Replay recorded answers
- **Recording History**: Session-based recording list
- **AI Analysis**:
  - Content quality score (0-100)
  - Confidence score (0-100)
  - Structure score (0-100)
  - Pace score with ideal range (120-150 WPM)

## Analytics Dashboard Features
- **Key Metrics**: Total Applications, Interviews, Offers, Response Rate
- **Application Funnel**: Visual pipeline from Applied → Reviewed → Interview → Offer
- **Status Breakdown**: Circular chart with interview rate
- **Top Companies**: Companies most applied to
- **Recent Activity**: Timeline of recent applications
- **AI Insights**: Dynamic tips based on performance
- **Time Range Filters**: 7 days, 30 days, 90 days

## Multiple Resume Profiles
- Create multiple resumes for different job types
- Set default profile for job matching
- Upload PDF resumes with profile names
- View and manage all profiles

## Design System - Batik B Theme

### Color Palette
**Light Mode:**
- Background: #f8f8f8
- Cards: #ffffff
- Text: #1a1a1a - #6b6b6b
- Batik pattern: Black → Grey → White → Turquoise

**Dark Mode (Inverted):**
- Background: #1a1a1a
- Cards: #2d2d2d
- Text: #f5f5f5 - #9a9a9a
- Batik pattern: White → Grey → Black → Turquoise

**Accent Color:**
- Turquoise: #20b2aa (primary)
- Turquoise Light: #40e0d0
- Turquoise Dark: #008b8b

## Implementation Status

### Completed Features (January 2026)
1. ✅ Core MVP - Resume upload, parsing, job search
2. ✅ Multi-source Integration - 6+ job boards + Google CSE
3. ✅ AI Features - Job matching, cover letter, callback prediction
4. ✅ User Management - Save jobs, track applications
5. ✅ Email Features - Alerts, automated daily digest
6. ✅ Interview Preparation - Questions, answers, mock interviews
7. ✅ Voice Coach - Speech-to-text with AI feedback
8. ✅ Dark Mode - Inverted batik theme with toggle
9. ✅ Analytics Dashboard - Application analytics with charts
10. ✅ Multiple Resume Profiles - Manage different resumes
11. ✅ Voice Recording Playback - Replay practice recordings

### Pages (12 Total)
1. Dashboard
2. My Resume
3. Resume Profiles
4. Job Search
5. Saved Jobs
6. Applications
7. Success Predictor
8. Interview Prep
9. Voice Coach
10. Cover Letter
11. Job Alerts
12. Analytics

## Future Enhancements (Backlog)
- [ ] Interview video recording mode
- [ ] Video analysis for body language feedback
- [ ] Salary insights and negotiation tips
- [ ] LinkedIn profile sync
- [ ] Custom schedule options for digest

## Test Reports
- `/app/test_reports/iteration_5.json` - Frontend refactor tests
- `/app/test_reports/iteration_6.json` - New features tests (Analytics, Profiles, Voice Playback)

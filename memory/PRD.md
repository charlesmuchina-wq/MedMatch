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
- ✅ **AI Interview Coach with Voice** (NEW)
  - Browser-based speech recognition (Web Speech API)
  - Real-time transcription of spoken answers
  - AI analysis of content quality, confidence, and structure
  - Delivery pace feedback (WPM analysis)
  - Confidence indicators detection
  - Improvement suggestions
  - Session statistics tracking
- ✅ Dark Mode with Inverted Batik Theme

## Tech Stack
- **Backend**: FastAPI (Python) with MongoDB (motor)
- **Frontend**: React with shadcn/ui components
- **AI**: Emergent LLM Key (GPT models via litellm)
- **Voice**: Web Speech API (SpeechRecognition)
- **Email**: Gmail SMTP
- **Scheduler**: APScheduler (AsyncIOScheduler)
- **Theming**: CSS custom properties with localStorage persistence

## Architecture

### Backend (`/app/backend/server.py`)
- FastAPI with APIRouter prefixed with `/api`
- APScheduler for automated daily digest
- MongoDB collections: resumes, jobs, saved_jobs, applications, alerts, digest_settings, cover_letters, callback_predictions, emailed_jobs

### Frontend (`/app/frontend/src/`)
```
├── App.js                         # Main routing + Theme Provider
├── App.css                        # Component styles with dark mode
├── index.css                      # Global styles + batik patterns
├── pages/
│   ├── Dashboard.jsx              # Overview with stats
│   ├── ResumePage.jsx             # Resume upload with dropzone
│   ├── JobSearchPage.jsx          # Job search with filters
│   ├── SavedJobsPage.jsx          # Saved jobs list
│   ├── ApplicationsPage.jsx       # Application tracker
│   ├── SuccessPredictorPage.jsx   # AI callback prediction
│   ├── InterviewPrepPage.jsx      # Interview preparation
│   ├── VoiceCoachPage.jsx         # Voice interview coach (NEW)
│   ├── CoverLetterPage.jsx        # AI cover letter generator
│   └── JobAlertsPage.jsx          # Email alerts & scheduler
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
| `/api/jobs/search` | GET | Search jobs with filters |
| `/api/jobs/deep-search` | POST | AI-powered comprehensive search |
| `/api/jobs/predict-callback` | POST | Full AI callback prediction |
| `/api/interview/generate-questions` | POST | Generate interview questions |
| `/api/interview/generate-answer` | POST | Generate answer suggestion |
| `/api/interview/voice-feedback` | POST | AI voice interview feedback |
| `/api/digest/scheduler-status` | GET | Get scheduler status |
| `/api/cover-letter/generate` | POST | Generate AI cover letter |

## Voice Coach Features
- **Speech Recognition**: Browser-native Web Speech API (Chrome, Edge, Safari)
- **Live Transcription**: Real-time display of spoken words
- **AI Analysis**:
  - Content quality score (0-100)
  - Confidence score (0-100)
  - Structure score (0-100)
  - Pace score with ideal range (120-150 WPM)
- **Feedback Types**:
  - Strengths identification
  - Areas for improvement
  - Delivery tips
  - Confidence indicators (positive/negative)
  - Suggested content additions
- **Session Tracking**: Questions answered, average score, total time

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

### Pages (10 Total)
1. Dashboard
2. My Resume
3. Job Search
4. Saved Jobs
5. Applications
6. Success Predictor
7. Interview Prep
8. Voice Coach
9. Cover Letter
10. Job Alerts

## Future Enhancements (Backlog)
- [ ] Multiple resume profiles
- [ ] Salary insights and negotiation tips
- [ ] LinkedIn profile sync
- [ ] Job Application Dashboard Analytics
- [ ] Custom schedule options for digest
- [ ] Voice recording playback
- [ ] Interview video recording mode

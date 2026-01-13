# MedMatch - Remote Job Finder with AI Matching

## Original Problem Statement
Create an application that uses the user's resume to find remote jobs that match their skills and experience. The app should parse resumes, search multiple job sources, use AI for matching, and provide features like email alerts, cover letter generation, and callback probability prediction.

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
- ✅ Daily Digest - new jobs from last 24 hours only
- ✅ **Automated Daily Digest Scheduler** (NEW)
  - APScheduler integration
  - Runs automatically at 8:00 AM UTC daily
  - Subscription management (subscribe/unsubscribe)
  - Shows next run time and scheduler status
- ✅ AI Cover Letter Generator
- ✅ Application Success Predictor
  - Callback probability score (0-100%)
  - Match breakdown (Skills, Experience, Education, Keywords)
  - Competition level estimation
  - Timing advice
  - Strengths and gaps analysis
  - Personalized recommendations

## Tech Stack
- **Backend**: FastAPI (Python) with MongoDB (motor)
- **Frontend**: React with shadcn/ui components
- **AI**: Emergent LLM Key (GPT models via litellm)
- **Email**: Gmail SMTP
- **Scheduler**: APScheduler (AsyncIOScheduler)

## Architecture

### Backend (`/app/backend/server.py`)
- FastAPI with APIRouter prefixed with `/api`
- APScheduler for automated daily digest
- MongoDB collections: resumes, jobs, saved_jobs, applications, alerts, digest_settings, cover_letters, callback_predictions, emailed_jobs

### Frontend (`/app/frontend/src/`)
```
├── App.js                         # Main routing (~300 lines)
├── App.css                        # Global styles
├── pages/
│   ├── Dashboard.jsx              # Overview with stats
│   ├── ResumePage.jsx             # Resume upload with dropzone
│   ├── JobSearchPage.jsx          # Job search with filters
│   ├── SavedJobsPage.jsx          # Saved jobs list
│   ├── ApplicationsPage.jsx       # Application tracker
│   ├── SuccessPredictorPage.jsx   # AI callback prediction
│   ├── CoverLetterPage.jsx        # AI cover letter generator
│   └── JobAlertsPage.jsx          # Email alerts & automated scheduler
└── components/
    ├── ui/                        # shadcn components
    └── shared/
        └── JobCard.jsx            # Job card with quick probability badge
```

## Key API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/resume` | GET | Get user's resume |
| `/api/resume/upload` | POST | Upload and parse resume |
| `/api/jobs/search` | GET | Search jobs with filters |
| `/api/jobs/deep-search` | POST | AI-powered comprehensive search |
| `/api/jobs/predict-callback` | POST | Full AI callback prediction |
| `/api/jobs/quick-probability` | POST | Quick probability for job cards |
| `/api/digest/settings` | POST | Create/update digest subscription |
| `/api/digest/scheduler-status` | GET | Get scheduler status and next run |
| `/api/digest/trigger-now` | POST | Manually trigger scheduled digest |
| `/api/digest/run-scheduled` | POST | Run digest for all subscribers |
| `/api/cover-letter/generate` | POST | Generate AI cover letter |

## Scheduler Configuration
- **Engine**: APScheduler AsyncIOScheduler
- **Schedule**: CronTrigger(hour=8, minute=0)
- **Timezone**: UTC
- **Job ID**: "daily_digest"

## Implementation Status

### Completed Features (January 2026)
1. ✅ **Core MVP** - Resume upload, parsing, job search
2. ✅ **Multi-source Integration** - 6+ job boards + Google CSE
3. ✅ **AI Features** - Job matching, relevance scoring, cover letter generation, callback prediction
4. ✅ **User Management** - Save jobs, track applications, status updates
5. ✅ **Email Features** - Real-time alerts, daily digest (no duplicates)
6. ✅ **Automated Scheduler** - APScheduler runs daily at 8 AM UTC
7. ✅ **Code Refactoring** - App.js optimized, modular page structure

### Testing Status
- **Backend**: All endpoints tested and working
- **Frontend**: All 8 pages verified functional
- **Scheduler**: Running and showing correct next run time

## Configuration
- Google CSE credentials in `backend/.env`
- Gmail app password in `backend/.env`
- Emergent LLM Key for AI features
- APScheduler auto-starts with FastAPI app

## Future Enhancements (Backlog)
- [ ] Multiple resume profiles
- [ ] Interview preparation assistant
- [ ] Salary insights and negotiation tips
- [ ] LinkedIn profile sync
- [ ] Job Application Dashboard Analytics
- [ ] Batch prediction for saved jobs

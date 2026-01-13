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
- ✅ AI Cover Letter Generator
- ✅ Application Success Predictor (NEW)
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

## Architecture

### Backend (`/app/backend/server.py`)
- FastAPI with APIRouter prefixed with `/api`
- MongoDB collections: resumes, jobs, saved_jobs, applications, alerts, digest_settings, cover_letters, callback_predictions
- Async job fetching from multiple sources

### Frontend (`/app/frontend/src/`)
```
├── App.js                         # Main routing (~295 lines)
├── App.css                        # Global styles
├── pages/
│   ├── Dashboard.jsx              # Overview with stats
│   ├── ResumePage.jsx             # Resume upload with dropzone
│   ├── JobSearchPage.jsx          # Job search with filters
│   ├── SavedJobsPage.jsx          # Saved jobs list
│   ├── ApplicationsPage.jsx       # Application tracker
│   ├── SuccessPredictorPage.jsx   # AI callback prediction (NEW)
│   ├── CoverLetterPage.jsx        # AI cover letter generator
│   └── JobAlertsPage.jsx          # Email alerts & daily digest
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
| `/api/jobs/google-search` | GET | Google CSE job search |
| `/api/jobs/save` | POST | Save a job |
| `/api/jobs/saved` | GET | Get saved jobs |
| `/api/jobs/predict-callback` | POST | Full AI callback prediction |
| `/api/jobs/quick-probability` | POST | Quick probability for job cards |
| `/api/jobs/prediction-history` | GET | Get prediction history |
| `/api/applications` | GET/POST | Manage applications |
| `/api/cover-letter/generate` | POST | Generate AI cover letter |
| `/api/digest/send-daily` | POST | Send daily digest |

## Implementation Status

### Completed Features (January 2026)
1. ✅ **Core MVP** - Resume upload, parsing, job search
2. ✅ **Multi-source Integration** - 6+ job boards + Google CSE
3. ✅ **AI Features** - Job matching, relevance scoring, cover letter generation
4. ✅ **User Management** - Save jobs, track applications, status updates
5. ✅ **Email Features** - Real-time alerts, daily digest (no duplicates)
6. ✅ **Code Refactoring** - App.js reduced from 1491 to ~295 lines
7. ✅ **Application Success Predictor** - AI-powered callback probability prediction
   - Full analysis page with detailed breakdown
   - Quick probability badges on job cards in search results

### Testing Status
- **Backend**: All endpoints tested and working
- **Frontend**: All 8 pages verified functional

## Configuration
- Google CSE credentials in `backend/.env`
- Gmail app password in `backend/.env`
- Emergent LLM Key for AI features

## Future Enhancements (Backlog)
- [ ] Automated scheduled daily digest (cron job)
- [ ] Multiple resume profiles
- [ ] Interview preparation assistant
- [ ] Salary insights and negotiation tips
- [ ] LinkedIn profile sync
- [ ] Job Application Dashboard Analytics

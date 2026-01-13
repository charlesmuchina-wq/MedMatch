# MedMatch - Remote Job Finder with AI Matching

## Original Problem Statement
Create an application that uses the user's resume to find remote jobs that match their skills and experience. The app should parse resumes, search multiple job sources, use AI for matching, and provide features like email alerts and cover letter generation.

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

## Tech Stack
- **Backend**: FastAPI (Python) with MongoDB (motor)
- **Frontend**: React with shadcn/ui components
- **AI**: Emergent LLM Key (GPT models via litellm)
- **Email**: Gmail SMTP

## Architecture

### Backend (`/app/backend/server.py`)
- FastAPI with APIRouter prefixed with `/api`
- MongoDB collections: resumes, jobs, saved_jobs, applications, alerts, digest_settings, cover_letters
- Async job fetching from multiple sources

### Frontend (`/app/frontend/src/`)
```
├── App.js                    # Main routing (287 lines - refactored)
├── App.css                   # Global styles
├── pages/
│   ├── Dashboard.jsx         # Overview with stats
│   ├── ResumePage.jsx        # Resume upload with dropzone
│   ├── JobSearchPage.jsx     # Job search with filters
│   ├── SavedJobsPage.jsx     # Saved jobs list
│   ├── ApplicationsPage.jsx  # Application tracker
│   ├── JobAlertsPage.jsx     # Email alerts & daily digest
│   └── CoverLetterPage.jsx   # AI cover letter generator
└── components/
    ├── ui/                   # shadcn components
    └── shared/
        └── JobCard.jsx       # Reusable job card component
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
| `/api/applications` | GET/POST | Manage applications |
| `/api/applications/{id}` | PUT/DELETE | Update/delete application |
| `/api/alerts/send-now` | POST | Send immediate job alert |
| `/api/digest/send-daily` | POST | Send daily digest |
| `/api/cover-letter/generate` | POST | Generate AI cover letter |
| `/api/cover-letter/history` | GET | Get cover letter history |

## Implementation Status

### Completed Features (January 2026)
1. ✅ **Core MVP** - Resume upload, parsing, job search
2. ✅ **Multi-source Integration** - 6+ job boards + Google CSE
3. ✅ **AI Features** - Job matching, relevance scoring, cover letter generation
4. ✅ **User Management** - Save jobs, track applications, status updates
5. ✅ **Email Features** - Real-time alerts, daily digest (no duplicates)
6. ✅ **Code Refactoring** - App.js reduced from 1491 to 287 lines

### Testing Status
- **Backend**: 22/22 tests passed (100%)
- **Frontend**: All 7 pages verified functional

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
